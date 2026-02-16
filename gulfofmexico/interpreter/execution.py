"""
Interpreter Execution - Main Statement Loop

Contains ``interpret_code_statements_main_wrapper`` (the public entry point)
and ``interpret_code_statements`` (the recursive core loop), plus
``execute_conditional`` which is used by several other modules.
"""

from __future__ import annotations

import random
import re
import time as _time
from typing import Optional, Union

from gulfofmexico.base import (
    Token,
    raise_error_at_line,
    raise_error_at_token,
)
from gulfofmexico.builtin import (
    KEYWORDS,
    GulfOfMexicoFunction,
    GulfOfMexicoMutable,
    GulfOfMexicoNumber,
    GulfOfMexicoObject,
    GulfOfMexicoString,
    GulfOfMexicoUndefined,
    GulfOfMexicoValue,
    Name,
    Variable,
    VariableLifetime,
    db_to_boolean,
    db_to_string,
)
from gulfofmexico.processor.syntax_tree import (
    AfterStatement,
    ClassDeclaration,
    CodeStatement,
    Conditional,
    DeleteStatement,
    ExportStatement,
    ExpressionStatement,
    FunctionDefinition,
    ImportStatement,
    ReturnStatement,
    ReverseStatement,
    VariableAssignment,
    VariableDeclaration,
    WhenStatement,
)

from .context import (
    AsyncStatements,
    InterpreterContext,
    Namespace,
    ReturnSentinel,
    WhenStatementWatchers,
)
from .dispatch import determine_statement_type
from .expressions import evaluate_expression, print_expression_debug
from .namespaces import get_name_from_namespaces
from .variables import assign_variable, declare_new_variable
from .watchers import register_when_statement


# ---------------------------------------------------------------------------
# Conditional execution helper
# ---------------------------------------------------------------------------

def execute_conditional(
    condition: GulfOfMexicoValue,
    statements_inside_scope: list[tuple[CodeStatement, ...]],
    namespaces: list[Namespace],
    when_statement_watchers: WhenStatementWatchers,
    importable_names: dict[str, dict[str, GulfOfMexicoValue]],
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
    ctx: InterpreterContext,
) -> Optional[GulfOfMexicoValue]:
    """Execute *statements_inside_scope* in a new scope if *condition* is truthy."""
    condition = db_to_boolean(condition)
    execute = condition.value is True if condition.value is not None else random.random() < 0.50
    if execute:
        return interpret_code_statements(
            statements_inside_scope,
            namespaces + [{}],
            [],
            when_statement_watchers + [{}],
            importable_names,
            exported_names,
            ctx,
        )
    return None


# ---------------------------------------------------------------------------
# All-keyword set (for delete-keyword checking)
# ---------------------------------------------------------------------------

KEYWORDS_SET = set(KEYWORDS.keys())


# ---------------------------------------------------------------------------
# Main wrapper (resets mutable state between runs)
# ---------------------------------------------------------------------------

def interpret_code_statements_main_wrapper(
    statements: list[tuple[CodeStatement, ...]],
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    importable_names: dict[str, dict[str, GulfOfMexicoValue]],
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
    ctx: Optional[InterpreterContext] = None,
) -> Optional[GulfOfMexicoValue]:
    """Entry point for interpretation — resets mutable state then delegates."""
    if ctx is None:
        ctx = InterpreterContext()
    ctx.reset()
    return interpret_code_statements(
        statements, namespaces, async_statements,
        when_statement_watchers, importable_names, exported_names, ctx,
    )


# ---------------------------------------------------------------------------
# Core execution loop
# ---------------------------------------------------------------------------

def interpret_code_statements(
    statements: list[tuple[CodeStatement, ...]],
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    importable_names: dict[str, dict[str, GulfOfMexicoValue]],
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
    ctx: InterpreterContext,
) -> Optional[GulfOfMexicoValue]:
    """Interpret a list of statement tuples sequentially."""
    result = None

    for statement_tuple in statements:
        statement = determine_statement_type(statement_tuple, namespaces, ctx)
        if statement is None:
            continue

        # Update current line for error reporting
        if hasattr(statement, "name") and hasattr(statement.name, "line"):
            ctx.current_line = statement.name.line
        elif hasattr(statement, "keyword") and hasattr(statement.keyword, "line"):
            ctx.current_line = statement.keyword.line

        match statement:
            case ExpressionStatement():
                result = evaluate_expression(
                    statement.expression, namespaces,
                    async_statements, when_statement_watchers, ctx,
                )
                print_expression_debug(statement.debug, statement.expression, result, namespaces, ctx)

            case VariableDeclaration():
                value = evaluate_expression(
                    statement.expression, namespaces,
                    async_statements, when_statement_watchers, ctx,
                )
                declare_new_variable(statement, value, namespaces, async_statements, when_statement_watchers, ctx)

            case VariableAssignment():
                indexes = [
                    evaluate_expression(expr, namespaces, async_statements, when_statement_watchers, ctx)
                    for expr in statement.indexes
                ]
                new_value = evaluate_expression(
                    statement.expression, namespaces,
                    async_statements, when_statement_watchers, ctx,
                )
                assign_variable(statement, indexes, new_value, namespaces, async_statements, when_statement_watchers, ctx)

            case ReturnStatement():
                result = evaluate_expression(
                    statement.expression, namespaces,
                    async_statements, when_statement_watchers, ctx,
                )
                print_expression_debug(statement.debug, statement.expression, result, namespaces, ctx)
                return ReturnSentinel(result)

            case Conditional():
                condition = evaluate_expression(
                    statement.expression, namespaces,
                    async_statements, when_statement_watchers, ctx,
                )
                result = execute_conditional(
                    condition, statement.code, namespaces,
                    when_statement_watchers, importable_names, exported_names, ctx,
                )
                if isinstance(result, ReturnSentinel):
                    return result

            case WhenStatement():
                register_when_statement(
                    statement.expression, statement.code, namespaces,
                    async_statements, when_statement_watchers,
                    importable_names, exported_names, ctx,
                )

            case AfterStatement():
                raise_error_at_line(
                    ctx.filename, ctx.code, ctx.current_line,
                    '"after" with mouse/keyboard events is not supported.',
                )

            case FunctionDefinition():
                func = GulfOfMexicoFunction(
                    [arg.value for arg in statement.args],
                    statement.code,
                    statement.is_async,
                )
                namespaces[-1][statement.name.value] = Variable(
                    statement.name.value,
                    [VariableLifetime(func, 100_000_000_000, 0, True, True)],
                    [],
                )

            case ClassDeclaration():
                class_obj = GulfOfMexicoObject(statement.name.value, {})
                class_namespace: Namespace = {statement.name.value: Name(statement.name.value, class_obj)}
                interpret_code_statements(
                    statement.code,
                    namespaces + [class_namespace],
                    async_statements,
                    when_statement_watchers + [{}],
                    importable_names,
                    exported_names,
                    ctx,
                )
                for k, v in class_namespace.items():
                    if k == statement.name.value:
                        continue
                    class_obj.namespace[k] = v
                namespaces[-1][statement.name.value] = Name(statement.name.value, class_obj)

            case DeleteStatement():
                name = statement.name.value
                if "delete" in ctx.deleted_keywords:
                    raise_error_at_token(ctx.filename, ctx.code, "Error: delete was deleted", statement.keyword)
                if name == "delete":
                    ctx.deleted_keywords.add("delete")
                elif name in KEYWORDS_SET:
                    ctx.deleted_keywords.add(name)
                    for ns in namespaces:
                        if name in ns:
                            del ns[name]
                else:
                    from .namespaces import get_name_and_namespace_from_namespaces  # noqa: PLC0415
                    var, ns = get_name_and_namespace_from_namespaces(name, namespaces)
                    if var:
                        if isinstance(var, Variable) and var.lifetimes:
                            ctx.deleted_values.add(var.lifetimes[0].value)
                        elif isinstance(var, Name):
                            ctx.deleted_values.add(var.value)
                        if ns:
                            del ns[name]
                    else:
                        try:
                            val = float(name)
                            if val == int(val):
                                ctx.deleted_values.add(GulfOfMexicoNumber(int(val)))
                            else:
                                ctx.deleted_values.add(GulfOfMexicoNumber(val))
                        except ValueError:
                            ctx.deleted_values.add(GulfOfMexicoString(name))

            case ReverseStatement():
                current_idx = statements.index(statement_tuple)
                remaining = statements[:current_idx]
                remaining.reverse()
                for rev_stmt_tuple in remaining:
                    rev_stmt = determine_statement_type(rev_stmt_tuple, namespaces, ctx)
                    if rev_stmt is None:
                        continue
                    result = interpret_code_statements(
                        [rev_stmt_tuple], namespaces, async_statements,
                        when_statement_watchers, importable_names, exported_names, ctx,
                    )
                return result

            case ImportStatement():
                _time.sleep(0.025)  # 25% tariff per spec
                for name_token in statement.names:
                    name = name_token.value
                    found = False
                    for file_dict in importable_names.values():
                        if name in file_dict:
                            imported_val = file_dict[name]
                            if isinstance(imported_val, GulfOfMexicoFunction):
                                tariffed_code = [
                                    stmt for stmt in imported_val.code
                                    if random.random() > 0.25
                                ]
                                imported_val = GulfOfMexicoFunction(
                                    imported_val.args, tariffed_code, imported_val.is_async,
                                )
                            namespaces[-1][name] = Name(name, imported_val)
                            found = True
                            break
                    if not found:
                        raise_error_at_token(ctx.filename, ctx.code, f"Cannot find imported name: {name}", name_token)

            case ExportStatement():
                for name_token in statement.names:
                    name = name_token.value
                    v_result = get_name_from_namespaces(name, namespaces)
                    if not v_result:
                        raise_error_at_token(ctx.filename, ctx.code, f"Cannot export undefined name: {name}", name_token)
                    else:
                        v: Variable | Name = v_result  # type: ignore
                        export_value: GulfOfMexicoValue
                        if isinstance(v, Name):
                            export_value = v.value
                        elif isinstance(v, Variable):
                            export_value = v.lifetimes[-1].value if v.lifetimes else GulfOfMexicoUndefined()
                        else:
                            export_value = v
                        target = statement.target_file.value
                        exported_names.append((target, name, export_value))

        # Decrement line-based lifetimes
        for ns in namespaces:
            for entry in ns.values():
                if isinstance(entry, Variable):
                    for lt in entry.lifetimes:
                        if lt.lines_left > 0:
                            lt.lines_left -= 1
                    entry.clear_outdated_lifetimes()

    # Process async statements
    while async_statements:
        async_stmt = async_statements.pop(0)
        statements_list, async_namespaces, current_index, direction = async_stmt
        if current_index < len(statements_list):
            result = interpret_code_statements(
                [statements_list[current_index]],
                async_namespaces, async_statements,
                when_statement_watchers, importable_names, exported_names, ctx,
            )
            new_index = current_index + (1 if direction == 1 else -1)
            if 0 <= new_index < len(statements_list):
                async_statements.append((statements_list, async_namespaces, new_index, direction))

    return result
