"""
Interpreter Expressions - Expression Evaluation Engine

Contains the core expression evaluator, string interpolation, function
invocation (both user-defined and builtin), and the ``await`` / ``next`` /
``previous`` keyword handlers that appear inside expressions.

Circular dependency note:
    ``evaluate_normal_function`` needs ``interpret_code_statements`` from
    execution.py.  This is resolved via a late import inside the function
    body to break the import cycle.
"""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Optional, Union

from gulfofmexico.base import (
    OperatorType,
    Token,
    TokenType,
    debug_print,
    debug_print_no_token,
    raise_error_at_line,
    raise_error_at_token,
)
from gulfofmexico.builtin import (
    BuiltinFunction,
    GulfOfMexicoBoolean,
    GulfOfMexicoFunction,
    GulfOfMexicoIndexable,
    GulfOfMexicoKeyword,
    GulfOfMexicoList,
    GulfOfMexicoNamespaceable,
    GulfOfMexicoNumber,
    GulfOfMexicoObject,
    GulfOfMexicoPendingInit,
    GulfOfMexicoPromise,
    GulfOfMexicoSpecialBlankValue,
    GulfOfMexicoString,
    GulfOfMexicoUndefined,
    GulfOfMexicoValue,
    Name,
    Variable,
    db_to_boolean,
    db_to_string,
)
from gulfofmexico.processor.expression_tree import (
    ExpressionNode,
    ExpressionTreeNode,
    FunctionNode,
    IndexNode,
    ListNode,
    SingleOperatorNode,
    ValueNode,
    build_expression_tree,
    get_expr_first_token,
)
from gulfofmexico.processor.lexer import tokenize as db_tokenize
from gulfofmexico.processor.syntax_tree import (
    CodeStatement,
    ReturnStatement,
)

from .context import (
    AsyncStatements,
    InterpreterContext,
    Namespace,
    ReturnSentinel,
    WhenStatementWatchers,
)
from .helpers import gather_names_or_values, get_built_expression
from .namespaces import (
    determine_non_name_value,
    get_name_and_namespace_from_namespaces,
    get_name_from_namespaces,
    get_value_from_namespaces,
)
from .operators import (
    perform_single_value_operation,
    perform_two_value_operation,
)


# ---------------------------------------------------------------------------
# When-statement watcher helpers (used by expression evaluation)
# ---------------------------------------------------------------------------

def get_code_from_when_statement_watchers(
    name_or_id: Union[str, int],
    when_statement_watchers: WhenStatementWatchers,
) -> list[tuple[ExpressionTreeNode, list[tuple[CodeStatement, ...]], list[dict[str, Variable | Name]]]]:
    """Collect all watcher entries matching *name_or_id*."""
    vals: list[tuple[ExpressionTreeNode, list[tuple[CodeStatement, ...]], list[dict[str, Variable | Name]]]] = []
    for watcher_dict in when_statement_watchers:
        if val := watcher_dict.get(name_or_id):
            vals += val
    return vals


# ---------------------------------------------------------------------------
# Async function registration
# ---------------------------------------------------------------------------

def register_async_function(
    expr: FunctionNode,
    func: GulfOfMexicoFunction,
    namespaces: list[Namespace],
    args: list[GulfOfMexicoValue],
    async_statements: AsyncStatements,
    ctx: InterpreterContext,
) -> None:
    """Queue *func* for deferred (async) execution."""
    if len(func.args) > len(args):
        raise_error_at_token(
            ctx.filename, ctx.code,
            f"Expected more arguments for function call with {len(func.args)} argument{'s' if len(func.args) != 1 else ''}.",
            expr.name,
        )
    function_namespaces = namespaces + [{name: Name(name, arg) for name, arg in zip(func.args, args)}]
    async_statements.append((func.code, function_namespaces, 0, 1))


# ---------------------------------------------------------------------------
# Normal (synchronous) function evaluation
# ---------------------------------------------------------------------------

def evaluate_normal_function(
    expr: FunctionNode,
    func: Union[GulfOfMexicoFunction, BuiltinFunction],
    namespaces: list[Namespace],
    args: list[GulfOfMexicoValue],
    when_statement_watchers: WhenStatementWatchers,
    ctx: InterpreterContext,
) -> GulfOfMexicoValue:
    """Call a user-defined or built-in function and return its result."""
    # Late import to break circular dependency with execution.py
    from .execution import interpret_code_statements  # noqa: PLC0415

    if isinstance(func, BuiltinFunction):
        if func.arg_count > len(args):
            raise_error_at_token(
                ctx.filename, ctx.code,
                f"Expected more arguments for function call with {func.arg_count} argument{'s' if func.arg_count != 1 else ''}.",
                expr.name,
            )
        max_arg_count = func.arg_count if func.arg_count >= 0 else len(args)
        result = func.function(*args[:max_arg_count]) or GulfOfMexicoUndefined()

        # Handle pending init for constructors
        if isinstance(result, GulfOfMexicoPendingInit):
            instance = result.instance
            init_args = result.init_args
            if "init" in instance.namespace:
                init_entry = instance.namespace["init"]
                init_func = (
                    init_entry.value
                    if isinstance(init_entry, Name)
                    else (
                        init_entry.lifetimes[0].value
                        if isinstance(init_entry, Variable) and init_entry.lifetimes
                        else None
                    )
                )
                if isinstance(init_func, GulfOfMexicoFunction):
                    if len(init_func.args) > len(init_args):
                        raise_error_at_token(
                            ctx.filename, ctx.code,
                            f"init method expects {len(init_func.args)} argument{'s' if len(init_func.args) != 1 else ''}, got {len(init_args)}.",
                            expr.name,
                        )
                    init_namespace: Namespace = {
                        name: Name(name, arg)
                        for name, arg in zip(init_func.args, init_args)
                    }
                    interpret_code_statements(
                        init_func.code,
                        namespaces + [instance.namespace, init_namespace],
                        [],
                        when_statement_watchers + [{}, {}],
                        {},
                        [],
                        ctx,
                    )
            return instance

        # Enforce single-instance class constraint per spec
        if isinstance(result, GulfOfMexicoObject) and result.class_name:
            if ctx.class_instance_counts.get(result.class_name, 0) >= 1:
                raise_error_at_token(
                    ctx.filename, ctx.code,
                    f"Error: Can't have more than one '{result.class_name}' instance!",
                    expr.name,
                )
            ctx.class_instance_counts[result.class_name] = ctx.class_instance_counts.get(result.class_name, 0) + 1

        return result

    # User-defined function
    if len(func.args) > len(args):
        raise_error_at_token(
            ctx.filename, ctx.code,
            f"Expected more arguments for function call with {len(func.args)} argument{'s' if len(func.args) != 1 else ''}.",
            expr.name,
        )
    new_namespace: Namespace = {name: Name(name, arg) for name, arg in zip(func.args, args)}
    result = interpret_code_statements(
        func.code,
        namespaces + [new_namespace],
        [],
        when_statement_watchers + [{}],
        {},
        [],
        ctx,
    )
    if isinstance(result, ReturnSentinel):
        return result.value
    return result or GulfOfMexicoUndefined()


# ---------------------------------------------------------------------------
# Debug printing for expressions
# ---------------------------------------------------------------------------

def print_expression_debug(
    debug: int,
    expr: Union[list[Token], ExpressionTreeNode],
    value: GulfOfMexicoValue,
    namespaces: list[Namespace],
    ctx: InterpreterContext,
) -> None:
    """Emit debug output for an evaluated expression based on *debug* level."""
    expr = get_built_expression(expr)
    msg = None
    match debug:
        case 0:
            pass
        case 1:
            msg = f"Expression evaluates to value {db_to_string(value).value}."
        case 2:
            names = gather_names_or_values(expr)
            msg = (
                f"Expression evaluates to value {db_to_string(value).value}.\n"
                f"The value of each name in the expression is the following: \n"
                + "\n".join(
                    f"  {name}: {db_to_string(get_value_from_namespaces(name, namespaces, ctx)).value}"
                    for name in names
                )
            )
        case _:
            names = gather_names_or_values(expr)
            msg = (
                f"Expression evaluates to value {db_to_string(value).value}.\n"
                f"The value of each name in the expression is the following: \n"
                + "\n".join(
                    f"  {name}: {db_to_string(get_value_from_namespaces(name, namespaces, ctx)).value}"
                    for name in names
                )
                + f"\nThe expression used to get this value is: \n{expr.to_string()}"
            )

    if not msg:
        return
    if t := get_expr_first_token(expr):
        debug_print(ctx.filename, ctx.code, msg, t)
    else:
        debug_print_no_token(ctx.filename, msg)


# ---------------------------------------------------------------------------
# String interpolation
# ---------------------------------------------------------------------------

def interpret_formatted_string(
    string_token: Token,
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    ctx: InterpreterContext,
) -> GulfOfMexicoString:
    """Process currency-symbol interpolation in strings.

    Supports ``${expr}``, ``£{expr}``, ``¥{expr}`` (prefix) and
    ``{expr}€`` (postfix).  ``$`` inside braces acts as dot-access
    (Cape Verdean escudo notation).
    """
    string_value = string_token.value
    result = ""
    i = 0
    CURRENCY_PREFIXES = {"$", "£", "¥"}

    while i < len(string_value):
        # Prefix interpolation: ${}, £{}, ¥{}
        if i + 1 < len(string_value) and string_value[i] in CURRENCY_PREFIXES and string_value[i + 1] == "{":
            j = i + 2
            brace_count = 1
            while j < len(string_value) and brace_count > 0:
                if string_value[j] == "{":
                    brace_count += 1
                elif string_value[j] == "}":
                    brace_count -= 1
                j += 1
            if brace_count > 0:
                raise_error_at_token(
                    ctx.filename, ctx.code,
                    f"Unclosed {string_value[i]}{{}} expression in string",
                    string_token,
                )
            expr_str = string_value[i + 2 : j - 1].replace("$", ".")
            tokens = db_tokenize(ctx.filename, expr_str)
            expr_tree = build_expression_tree(ctx.filename, tokens, ctx.code)
            value = evaluate_expression(expr_tree, namespaces, async_statements, when_statement_watchers, ctx)
            result += db_to_string(value).value
            i = j
        # Postfix euro interpolation: {expr}€
        elif string_value[i] == "{":
            j = i + 1
            brace_count = 1
            while j < len(string_value) and brace_count > 0:
                if string_value[j] == "{":
                    brace_count += 1
                elif string_value[j] == "}":
                    brace_count -= 1
                j += 1
            if brace_count == 0 and j < len(string_value) and string_value[j] == "€":
                expr_str = string_value[i + 1 : j - 1].replace("$", ".")
                tokens = db_tokenize(ctx.filename, expr_str)
                expr_tree = build_expression_tree(ctx.filename, tokens, ctx.code)
                value = evaluate_expression(expr_tree, namespaces, async_statements, when_statement_watchers, ctx)
                result += db_to_string(value).value
                i = j + len("€")
            else:
                result += string_value[i]
                i += 1
        else:
            result += string_value[i]
            i += 1

    return GulfOfMexicoString(result)


# ---------------------------------------------------------------------------
# Escape sequences
# ---------------------------------------------------------------------------

def evaluate_escape_sequences(string_value: GulfOfMexicoString) -> GulfOfMexicoString:
    """Process backslash escape sequences in a GulfOfMexicoString."""
    escaped = string_value.value
    escaped = escaped.replace("\\\\", "\x00ESCAPED_BACKSLASH\x00")
    escaped = escaped.replace("\\n", "\n")
    escaped = escaped.replace("\\t", "\t")
    escaped = escaped.replace("\\r", "\r")
    escaped = escaped.replace('\\"', '"')
    escaped = escaped.replace("\\'", "'")
    escaped = escaped.replace("\x00ESCAPED_BACKSLASH\x00", "\\")
    return GulfOfMexicoString(escaped)


# ---------------------------------------------------------------------------
# Main expression evaluator
# ---------------------------------------------------------------------------

def evaluate_expression(
    expr: Union[list[Token], ExpressionTreeNode],
    namespaces: list[dict[str, Union[Variable, Name]]],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    ctx: InterpreterContext,
    *,
    ignore_string_escape_sequences: bool = False,
) -> GulfOfMexicoValue:
    """Public entry point — evaluates *expr* and checks for deleted values."""
    retval = _evaluate_expression_impl(
        expr, namespaces, async_statements, when_statement_watchers, ctx,
        ignore_string_escape_sequences,
    )
    if isinstance(retval, (GulfOfMexicoNumber, GulfOfMexicoString)) and retval in ctx.deleted_values:
        raise_error_at_line(
            ctx.filename, ctx.code, ctx.current_line,
            f"The value {retval.value} has been deleted.",
        )
    return retval


def _evaluate_expression_impl(
    expr: Union[list[Token], ExpressionTreeNode],
    namespaces: list[dict[str, Union[Variable, Name]]],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    ctx: InterpreterContext,
    ignore_string_escape_sequences: bool,
) -> GulfOfMexicoValue:
    """Core recursive expression evaluator."""
    # Late import to break circular dependency
    from .execution import execute_conditional  # noqa: PLC0415
    from .helpers import get_modified_next_name  # noqa: PLC0415

    expr = get_built_expression(expr)

    match expr:
        # ----- Function calls -----
        case FunctionNode():
            func = get_name_from_namespaces(expr.name.value, namespaces)
            if func is None:
                raise_error_at_token(ctx.filename, ctx.code, "Cannot find token in namespace.", expr.name)

            force_execute_sync = False

            if isinstance(func.value, GulfOfMexicoKeyword):
                # await keyword
                if func.value.value == "await":
                    if len(expr.args) != 1:
                        raise_error_at_token(ctx.filename, ctx.code, "Expected only one argument for await function.", expr.name)
                    if not isinstance(expr.args[0], FunctionNode):
                        raise_error_at_token(ctx.filename, ctx.code, "Expected argument of await function to be a function call.", expr.name)
                    force_execute_sync = True
                    expr = expr.args[0]
                    func = get_name_from_namespaces(expr.name.value, namespaces)
                    if func is None:
                        raise_error_at_token(ctx.filename, ctx.code, "Cannot find token in namespaces.", expr.name)

                # previous keyword
                elif isinstance(func.value, GulfOfMexicoKeyword) and func.value.value == "previous":
                    if len(expr.args) != 1:
                        raise_error_at_token(ctx.filename, ctx.code, "Expected only one argument for previous function.", expr.name)
                    if not isinstance(expr.args[0], ValueNode):
                        raise_error_at_token(ctx.filename, ctx.code, "Expected argument of previous function to be a variable.", expr.name)
                    val = get_name_from_namespaces(expr.args[0].name_or_value.value, namespaces)
                    if not isinstance(val, Variable):
                        raise_error_at_token(ctx.filename, ctx.code, "Expected argument of previous function to be a defined variable.", expr.args[0].name_or_value)
                    if not val.prev_values:
                        raise_error_at_token(ctx.filename, ctx.code, "Variable has no previous values.", expr.args[0].name_or_value)
                    return val.prev_values[-1]

                # next keyword
                elif isinstance(func.value, GulfOfMexicoKeyword) and func.value.value == "next":
                    if len(expr.args) != 1:
                        raise_error_at_token(ctx.filename, ctx.code, "Expected only one argument for next function.", expr.name)
                    if not isinstance(expr.args[0], ValueNode):
                        raise_error_at_token(ctx.filename, ctx.code, "Expected argument of next function to be a variable.", expr.name)
                    val = get_name_from_namespaces(expr.args[0].name_or_value.value, namespaces)
                    if not isinstance(val, Variable):
                        raise_error_at_token(ctx.filename, ctx.code, "Expected argument of next function to be a defined variable.", expr.args[0].name_or_value)

                    promise = GulfOfMexicoPromise(None)
                    _, ns = get_name_and_namespace_from_namespaces(expr.args[0].name_or_value.value, namespaces)
                    if not ns:
                        raise_error_at_token(ctx.filename, ctx.code, "Could not find namespace for variable.", expr.args[0].name_or_value)
                    ns_id = id(ns)
                    var_name = expr.args[0].name_or_value.value
                    dummy_return = ReturnStatement(
                        keyword=None,
                        expression=[expr.args[0].name_or_value],
                        debug=0,
                    )
                    watchers_key = (var_name, ns_id)
                    ctx.name_watchers[watchers_key] = (
                        dummy_return,
                        {watchers_key},
                        namespaces + [{}],
                        promise,
                    )
                    return promise

            if not isinstance(func.value, (BuiltinFunction, GulfOfMexicoFunction)):
                raise_error_at_token(ctx.filename, ctx.code, "Attempted function call on non-function value.", expr.name)

            caller = None
            dotted_call = len(name_split := expr.name.value.split(".")) > 1
            if dotted_call:
                caller = ".".join(name_split[:-1])
                if isinstance(func.value, BuiltinFunction) and func.value.modifies_caller:
                    expr = deepcopy(expr)
                    expr.args.insert(
                        0,
                        ValueNode(Token(TokenType.NAME, caller, expr.name.line, expr.name.col)),
                    )

            args = [
                evaluate_expression(arg, namespaces, async_statements, when_statement_watchers, ctx)
                for arg in expr.args
            ]
            if args and isinstance(args[0], GulfOfMexicoSpecialBlankValue):
                args = args[1:]

            extended_namespaces = namespaces
            if caller is not None:
                caller_entry = get_name_from_namespaces(caller, namespaces)
                if isinstance(caller_entry, (Variable, Name)):
                    caller_val = caller_entry.value
                    if isinstance(caller_val, GulfOfMexicoNamespaceable):
                        extended_namespaces = namespaces + [caller_val.namespace]

            if isinstance(func.value, GulfOfMexicoFunction) and func.value.is_async and not force_execute_sync:
                register_async_function(expr, func.value, extended_namespaces, args, async_statements, ctx)
                return GulfOfMexicoUndefined()

            elif isinstance(func.value, BuiltinFunction) and func.value.modifies_caller:
                if caller:
                    caller_var = get_name_from_namespaces(caller, namespaces)
                    if isinstance(caller_var, Variable) and not caller_var.can_edit_value:
                        raise_error_at_line(ctx.filename, ctx.code, ctx.current_line, "Cannot edit the value of this variable.")

                retval = evaluate_normal_function(expr, func.value, extended_namespaces, args, when_statement_watchers, ctx)
                when_watchers = get_code_from_when_statement_watchers(id(args[0]), when_statement_watchers)
                for when_watcher in when_watchers:
                    condition, inside_statements, captured_namespaces = when_watcher
                    condition_val = evaluate_expression(condition, captured_namespaces, async_statements, when_statement_watchers, ctx)
                    execute_conditional(
                        condition_val,
                        inside_statements,
                        captured_namespaces,
                        when_statement_watchers,
                        {},
                        [],
                        ctx,
                    )
                return retval

            return evaluate_normal_function(expr, func.value, extended_namespaces, args, when_statement_watchers, ctx)

        # ----- List literals -----
        case ListNode():
            return GulfOfMexicoList(
                [evaluate_expression(x, namespaces, async_statements, when_statement_watchers, ctx) for x in expr.values]
            )

        # ----- Value nodes -----
        case ValueNode():
            if expr.name_or_value.type == TokenType.STRING:
                retval = interpret_formatted_string(expr.name_or_value, namespaces, async_statements, when_statement_watchers, ctx)
                if not ignore_string_escape_sequences:
                    return evaluate_escape_sequences(retval)
                return retval
            return get_value_from_namespaces(expr.name_or_value, namespaces, ctx)

        # ----- Index access -----
        case IndexNode():
            value = evaluate_expression(expr.value, namespaces, async_statements, when_statement_watchers, ctx)
            index = evaluate_expression(expr.index, namespaces, async_statements, when_statement_watchers, ctx)
            if not isinstance(value, GulfOfMexicoIndexable):
                raise_error_at_line(ctx.filename, ctx.code, ctx.current_line, "Attempting to index a value that is not indexable.")
            return value.access_index(index)

        # ----- Binary expressions -----
        case ExpressionNode():
            left = evaluate_expression(expr.left, namespaces, async_statements, when_statement_watchers, ctx)
            if db_to_boolean(left).value is True and expr.operator == OperatorType.OR:
                return left
            elif db_to_boolean(left).value is False and expr.operator == OperatorType.AND:
                return left
            right = evaluate_expression(expr.right, namespaces, async_statements, when_statement_watchers, ctx)
            return perform_two_value_operation(left, right, expr.operator, expr.operator_token, ctx)

        # ----- Unary expressions -----
        case SingleOperatorNode():
            single_val: GulfOfMexicoValue = evaluate_expression(expr.expression, namespaces, async_statements, when_statement_watchers, ctx)
            return perform_single_value_operation(single_val, expr.operator, ctx)

    return GulfOfMexicoUndefined()
