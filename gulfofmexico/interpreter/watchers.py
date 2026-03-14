"""
Interpreter Watchers - When Statements, Next Tracking, Name Watching

Handles the reactive programming features of Gulf of Mexico:
- ``when`` statement registration and condition evaluation
- ``next``/``previous`` value tracking across expression trees
- Name-watcher callbacks for deferred execution
"""

from __future__ import annotations

import time
from copy import deepcopy
from typing import Optional, Union

from gulfofmexico.base import (
    Token,
    TokenType,
    raise_error_at_line,
    raise_error_at_token,
)
from gulfofmexico.builtin import (
    GulfOfMexicoKeyword,
    GulfOfMexicoMutable,
    GulfOfMexicoPromise,
    GulfOfMexicoValue,
    Name,
    Variable,
)
from gulfofmexico.processor.expression_tree import (
    ExpressionNode,
    ExpressionTreeNode,
    FunctionNode,
    IndexNode,
    ListNode,
    SingleOperatorNode,
    ValueNode,
)
from gulfofmexico.processor.syntax_tree import CodeStatement

from .context import (
    AsyncStatements,
    CodeStatementWithExpression,
    InterpreterContext,
    Namespace,
    WhenStatementWatchers,
)
from .expressions import evaluate_expression
from .helpers import (
    gather_names_or_values,
    get_built_expression,
    get_modified_next_name,
    get_modified_prev_name,
)
from .namespaces import (
    get_name_and_namespace_from_namespaces,
    get_name_from_namespaces,
)


# ---------------------------------------------------------------------------
# When-statement watcher removal
# ---------------------------------------------------------------------------

def remove_from_when_statement_watchers(
    name_or_id: Union[str, int],
    watcher: tuple[ExpressionTreeNode, list[tuple[CodeStatement, ...]], list[dict[str, Variable | Name]]],
    when_statement_watchers: WhenStatementWatchers,
) -> None:
    """Remove a specific watcher entry from all watcher dicts."""
    for watcher_dict in when_statement_watchers:
        if vals := watcher_dict.get(name_or_id):
            remove = None
            for i, v in enumerate(vals):
                if v == watcher:
                    remove = i
            if remove is not None:
                del vals[remove]


def remove_from_all_when_statement_watchers(
    name_or_id: Union[str, int],
    when_statement_watchers: WhenStatementWatchers,
) -> None:
    """Remove *all* entries for *name_or_id* from every watcher dict."""
    for watcher_dict in when_statement_watchers:
        if name_or_id in watcher_dict:
            del watcher_dict[name_or_id]


# ---------------------------------------------------------------------------
# When-statement registration
# ---------------------------------------------------------------------------

def register_when_statement(
    condition: Union[list[Token], ExpressionTreeNode],
    statements_inside_scope: list[tuple[CodeStatement, ...]],
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    importable_names: dict[str, dict[str, GulfOfMexicoValue]],
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
    ctx: InterpreterContext,
) -> None:
    """Register a ``when`` statement and evaluate its condition immediately."""
    from .execution import execute_conditional  # noqa: PLC0415

    built_condition = get_built_expression(condition)
    gathered_names = gather_names_or_values(built_condition)
    caller_names = [n for name in gathered_names if (n := ".".join(name.value.split(".")[:-1]))]

    dict_keys: list[Union[str, int]] = (
        [
            (id(v) if isinstance(v := get_name_from_namespaces(name.value, namespaces), Variable) else name.value)
            for name in gathered_names
        ]
        + [
            id(v.value)
            for name in gathered_names
            if (v := get_name_from_namespaces(name.value, namespaces)) is not None
            and isinstance(v.value, GulfOfMexicoMutable)
        ]
        + [id(v) for name in caller_names if isinstance(v := get_name_from_namespaces(name, namespaces), Variable)]
        + [
            id(v.value)
            for name in caller_names
            if (v := get_name_from_namespaces(name, namespaces)) is not None
            and isinstance(v.value, GulfOfMexicoMutable)
        ]
    )

    for name in dict_keys:
        if name not in when_statement_watchers[-1]:
            when_statement_watchers[-1][name] = []
        captured_ns = deepcopy(namespaces)
        when_statement_watchers[-1][name].append((built_condition, statements_inside_scope, captured_ns))

    condition_value = evaluate_expression(built_condition, namespaces, async_statements, when_statement_watchers, ctx)

    execute_conditional(
        condition_value, statements_inside_scope, namespaces,
        when_statement_watchers, importable_names, exported_names, ctx,
    )


# ---------------------------------------------------------------------------
# Next-expression handling
# ---------------------------------------------------------------------------

def handle_next_expressions(
    expr: ExpressionTreeNode,
    namespaces: list[Namespace],
    ctx: InterpreterContext,
) -> tuple[ExpressionTreeNode, set[tuple[str, int]], set[str]]:
    """Detect ``next`` / ``await next`` in *expr*, rewrite the tree, return watched names."""
    normal_nexts: set[tuple[str, int]] = set()
    async_nexts: set[str] = set()
    inner_nexts: list[tuple[set[tuple[str, int]], set[str]]] = []

    match expr:
        case FunctionNode():
            func = get_name_from_namespaces(expr.name.value, namespaces)
            if func is None:
                raise_error_at_token(ctx.filename, ctx.code, "Attempted function call on undefined variable.", expr.name)

            is_next = is_await = False
            if isinstance(func.value, GulfOfMexicoKeyword) and (
                (is_next := func.value.value == "next") or (is_await := func.value.value == "await")
            ):
                if is_next:
                    if len(expr.args) != 1 or not isinstance(expr.args[0], ValueNode):
                        raise_error_at_token(ctx.filename, ctx.code, '"Next" keyword can only take a single value as an argument.', expr.name)
                    name = expr.args[0].name_or_value.value
                    _, ns = get_name_and_namespace_from_namespaces(name, namespaces)
                    if not ns:
                        raise_error_at_line(ctx.filename, ctx.code, ctx.current_line, "Attempted to access namespace of a value without a namespace.")
                    last_name = name.split(".")[-1]
                    normal_nexts.add((name, id(ns)))
                    expr = expr.args[0]
                    expr.name_or_value.value = get_modified_next_name(last_name, id(ns))

                elif is_await:
                    if len(expr.args) != 1 or not isinstance(expr.args[0], FunctionNode):
                        raise_error_at_token(ctx.filename, ctx.code, "Can only await a function.", expr.name)
                    inner_expr = expr.args[0]
                    func = get_name_from_namespaces(expr.args[0].name.value, namespaces)
                    if func is None:
                        raise_error_at_token(ctx.filename, ctx.code, "Attempted function call on undefined variable.", expr.name)
                    if isinstance(func.value, GulfOfMexicoKeyword) and func.value.value == "next":
                        if len(inner_expr.args) != 1 or not isinstance(inner_expr.args[0], ValueNode):
                            raise_error_at_token(ctx.filename, ctx.code, '"Next" keyword can only take a single value as an argument.', inner_expr.name)
                        name = inner_expr.args[0].name_or_value.value
                        _, ns = get_name_and_namespace_from_namespaces(name, namespaces)
                        if not ns:
                            raise_error_at_line(ctx.filename, ctx.code, ctx.current_line, "Attempted to access namespace of a value without a namespace.")
                        last_name = name.split(".")[-1]
                        async_nexts.add(name)
                        expr = inner_expr.args[0]
                        expr.name_or_value.value = get_modified_next_name(last_name, id(ns))
            else:
                replacement_args = []
                for arg in expr.args:
                    new_expr, normal_arg_nexts, async_arg_nexts = handle_next_expressions(arg, namespaces, ctx)
                    inner_nexts.append((normal_arg_nexts, async_arg_nexts))
                    replacement_args.append(new_expr)
                expr.args = replacement_args

        case ListNode():
            replacement_values = []
            for ex in expr.values:
                new_expr, nn, an = handle_next_expressions(ex, namespaces, ctx)
                inner_nexts.append((nn, an))
                replacement_values.append(new_expr)
            expr.values = replacement_values

        case IndexNode():
            new_value, nvn, avn = handle_next_expressions(expr.value, namespaces, ctx)
            new_index, nin, ain = handle_next_expressions(expr.index, namespaces, ctx)
            expr.value = new_value
            expr.index = new_index
            inner_nexts.extend([(nvn, avn), (nin, ain)])

        case ExpressionNode():
            new_left, nln, aln = handle_next_expressions(expr.left, namespaces, ctx)
            new_right, nrn, arn = handle_next_expressions(expr.right, namespaces, ctx)
            expr.left = new_left
            expr.right = new_right
            inner_nexts.extend([(nln, aln), (nrn, arn)])

        case SingleOperatorNode():
            new_expr, nen, aen = handle_next_expressions(expr.expression, namespaces, ctx)
            expr.expression = new_expr
            inner_nexts.append((nen, aen))

    for nn, an in inner_nexts:
        normal_nexts |= nn
        async_nexts |= an
    return expr, normal_nexts, async_nexts


def save_previous_values_next_expr(
    expr_to_modify: ExpressionTreeNode,
    nexts: set[str],
    namespaces: list[Namespace],
    ctx: InterpreterContext,
) -> Namespace:
    """Save current values of names referenced by ``next`` for later comparison."""
    from .namespaces import determine_non_name_value  # noqa: PLC0415

    saved_namespace: Namespace = {}
    match expr_to_modify:
        case ValueNode():
            if expr_to_modify.name_or_value.type == TokenType.STRING:
                return {}
            name = expr_to_modify.name_or_value.value
            if name not in nexts:
                return {}
            val = get_name_from_namespaces(name, namespaces)
            if not val:
                val = Name("", determine_non_name_value(expr_to_modify.name_or_value, ctx))
            mod_name = get_modified_prev_name(name)
            expr_to_modify.name_or_value.value = mod_name
            return {mod_name: Name(mod_name, val.value)}

        case ExpressionNode():
            left_ns = save_previous_values_next_expr(expr_to_modify.left, nexts, namespaces, ctx)
            right_ns = save_previous_values_next_expr(expr_to_modify.right, nexts, namespaces, ctx)
            return left_ns | right_ns

        case IndexNode():
            value_ns = save_previous_values_next_expr(expr_to_modify.value, nexts, namespaces, ctx)
            index_ns = save_previous_values_next_expr(expr_to_modify.index, nexts, namespaces, ctx)
            return value_ns | index_ns

        case ListNode():
            for ex in expr_to_modify.values:
                saved_namespace |= save_previous_values_next_expr(ex, nexts, namespaces, ctx)
            return saved_namespace

        case FunctionNode():
            for arg in expr_to_modify.args:
                saved_namespace |= save_previous_values_next_expr(arg, nexts, namespaces, ctx)
            return saved_namespace

        case SingleOperatorNode():
            return save_previous_values_next_expr(expr_to_modify.expression, nexts, namespaces, ctx)

    return saved_namespace


# ---------------------------------------------------------------------------
# Next-value adjustment at execution time
# ---------------------------------------------------------------------------

def adjust_for_normal_nexts(
    statement: CodeStatementWithExpression,
    async_nexts: set[str],
    normal_nexts: set[tuple[str, int]],
    promise: Optional[GulfOfMexicoPromise],
    namespaces: list[Namespace],
    prev_namespace: Namespace,
    ctx: InterpreterContext,
) -> None:
    """Wait for async nexts and set up watchers for normal nexts."""

    def _get_state_watcher(val: object) -> Optional[int]:
        return None if not val else len(v) if (v := getattr(val, "prev_values")) else 0

    old_async_vals = [_get_state_watcher(get_name_from_namespaces(name, namespaces)) for name in async_nexts]
    old_normal_vals = [_get_state_watcher(get_name_from_namespaces(name, namespaces)) for name, _ in normal_nexts]

    # Wait for async nexts
    for name, start_len in zip(async_nexts, old_async_vals):
        curr_len = _get_state_watcher(get_name_from_namespaces(name, namespaces))
        while start_len == curr_len:
            time.sleep(0.01)
            curr_len = _get_state_watcher(get_name_from_namespaces(name, namespaces))

    # Build namespace for resolved async nexts
    new_namespace: Namespace = {}
    for name, old_len in zip(async_nexts, old_async_vals):
        v, ns = get_name_and_namespace_from_namespaces(name, namespaces)
        if not v or not ns or (old_len is not None and not isinstance(v, Variable)):
            raise_error_at_line(ctx.filename, ctx.code, ctx.current_line, "Something went wrong with accessing the next value of a variable.")
        mod_name = get_modified_next_name(name, id(ns))
        match old_len:
            case None:
                new_namespace[mod_name] = Name(mod_name, v.value if isinstance(v, Name) else v.prev_values[0])
            case i:
                if not isinstance(v, Variable):
                    raise_error_at_line(ctx.filename, ctx.code, ctx.current_line, "Something went wrong.")
                new_namespace[mod_name] = Name(mod_name, v.prev_values[i])

    # Adjust for normal nexts that may have already resolved
    for (name, ns_id), old_len in zip(list(normal_nexts), old_normal_vals):
        new_len = _get_state_watcher(v := get_name_from_namespaces(name, namespaces))
        if v is None or new_len == old_len:
            continue
        mod_name = get_modified_next_name(name, ns_id)
        normal_nexts.remove((name, ns_id))
        match old_len:
            case None:
                new_namespace[mod_name] = Name(mod_name, v.value if isinstance(v, Name) else v.prev_values[0])
            case i:
                if not isinstance(v, Variable):
                    raise_error_at_line(ctx.filename, ctx.code, ctx.current_line, "Something went wrong.")
                new_namespace[mod_name] = Name(mod_name, v.prev_values[i])

    # Set up watchers for remaining normal nexts
    for name, ns_id in normal_nexts:
        ctx.name_watchers[(name.split(".")[-1], ns_id)] = (
            statement,
            normal_nexts,
            namespaces + [new_namespace | prev_namespace],
            promise,
        )


def wait_for_async_nexts(
    async_nexts: set[str],
    namespaces: list[Namespace],
    ctx: InterpreterContext,
) -> Namespace:
    """Block until all async nexts resolve, return namespace with resolved values."""

    def _get_state_watcher(val: object) -> Optional[int]:
        return None if not val else len(v) if (v := getattr(val, "prev_values")) else 0

    old_async_vals = [_get_state_watcher(get_name_from_namespaces(name, namespaces)) for name in async_nexts]

    for name, start_len in zip(async_nexts, old_async_vals):
        curr_len = _get_state_watcher(get_name_from_namespaces(name, namespaces))
        while start_len == curr_len:
            time.sleep(0.01)
            curr_len = _get_state_watcher(get_name_from_namespaces(name, namespaces))

    new_namespace: Namespace = {}
    for name, old_len in zip(async_nexts, old_async_vals):
        v, ns = get_name_and_namespace_from_namespaces(name, namespaces)
        if not v or not ns or (old_len is not None and not isinstance(v, Variable)):
            raise_error_at_line(ctx.filename, ctx.code, ctx.current_line, "Something went wrong with accessing the next value of a variable.")
        mod_name = get_modified_next_name(name, id(ns))
        new_namespace[mod_name] = Name(mod_name, v.value)
    return new_namespace


# ---------------------------------------------------------------------------
# Name-watching statement execution
# ---------------------------------------------------------------------------

def interpret_name_watching_statement(
    _statement: CodeStatementWithExpression,
    namespaces: list[Namespace],
    _promise: Optional[GulfOfMexicoPromise],
    _async_statements: AsyncStatements,
    _when_statement_watchers: WhenStatementWatchers,
    _ctx: InterpreterContext,
) -> None:
    """Execute a statement triggered by a name-watcher."""
    namespaces.pop()  # remove expired namespace — critical


# ---------------------------------------------------------------------------
# Temp-namespace cleanup
# ---------------------------------------------------------------------------

def clear_temp_namespace(namespaces: list[Namespace], temp_namespace: Namespace) -> None:
    """Remove keys from the top namespace that were added temporarily."""
    for key in temp_namespace:
        del namespaces[-1][key]
