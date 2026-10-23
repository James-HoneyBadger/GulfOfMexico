"""
Interpreter Execution - Main Statement Loop

Contains ``interpret_code_statements_main_wrapper`` (the public entry point)
and ``interpret_code_statements`` (the recursive core loop), plus
``execute_conditional`` which is used by several other modules.
"""

from __future__ import annotations

import random
import os
import time as _time
from typing import Optional

from gulfofmexico.base import (
    raise_error_at_token,
)
from gulfofmexico.builtin import (
    KEYWORDS,
    GulfOfMexicoFunction,
    GulfOfMexicoNumber,
    GulfOfMexicoObject,
    GulfOfMexicoString,
    GulfOfMexicoUndefined,
    GulfOfMexicoValue,
    Name,
    Variable,
    VariableLifetime,
    db_to_number,
    db_to_boolean,
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
from .helpers import statement_expression, statement_indexes
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
    result = interpret_code_statements(
        statements, namespaces, async_statements,
        when_statement_watchers, importable_names, exported_names, ctx,
    )
    # Run any `after` blocks that are still scheduled.
    if ctx.pending_after:
        _drain_after(ctx.pending_after, ctx, wait=True)
    return result


# ---------------------------------------------------------------------------
# Core execution loop
# ---------------------------------------------------------------------------

def _drain_after(pending: list, ctx: InterpreterContext, *, wait: bool) -> None:
    """Run scheduled ``after`` blocks whose deadline has arrived.

    With ``wait=True`` (end of program) the scheduler sleeps until each
    remaining deadline, so finite timers always run and ``GULFOFMEXICO_WAIT``
    is only needed for open-ended ``when`` watchers.
    """
    while pending:
        pending.sort(key=lambda item: (item[0], item[1]))
        deadline, _seq, body, scopes = pending[0]
        remaining = deadline - _time.monotonic()
        if remaining > 0:
            if not wait:
                return
            _time.sleep(remaining)
        pending.pop(0)
        namespaces, when_statement_watchers, importable_names, exported_names = scopes
        # The body sees the current scopes plus a fresh block scope.
        interpret_code_statements(
            body,
            list(namespaces) + [{}],
            [],
            list(when_statement_watchers) + [{}],
            importable_names,
            exported_names,
            ctx,
        )


def _is_negative_lifetime(lifetime: Optional[str]) -> int:
    """Return N if the lifetime is ``<-N>`` (negative/hoisting), else 0."""
    if not lifetime or not lifetime.startswith("<") or not lifetime.endswith(">"):
        return 0
    inner = lifetime[1:-1]
    try:
        val = float(inner)
        if val < 0:
            return abs(int(val))
    except ValueError:
        pass
    return 0


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

    # ---- Pre-scan for negative lifetimes (variable hoisting per spec) ----
    # Variables with <-N> should exist N lines before their declaration.
    # We pre-declare them so earlier statements can see them.
    for stmt_idx, statement_tuple in enumerate(statements):
        for candidate in statement_tuple:
            if isinstance(candidate, VariableDeclaration) and candidate.lifetime:
                hoist_n = _is_negative_lifetime(candidate.lifetime)
                if hoist_n > 0:
                    # Evaluate the expression and pre-declare the variable
                    try:
                        pre_val = evaluate_expression(
                            candidate.expression, namespaces,
                            async_statements, when_statement_watchers, ctx,
                        )
                    except Exception:
                        continue  # can't pre-evaluate — skip hoisting
                    pre_var = Variable(candidate.name.value, [], [])
                    # Lifespan: hoist_n lines before + 1 for the decl line itself
                    pre_var.add_lifetime(
                        pre_val, candidate.confidence, hoist_n + 1,
                        "var" in [m.value for m in candidate.modifiers],
                        "const" not in [m.value for m in candidate.modifiers],
                    )
                    namespaces[-1][candidate.name.value] = pre_var
                    break  # only one candidate per statement_tuple matters

    for statement_index, statement_tuple in enumerate(statements):
        if id(statement_tuple) in ctx.tariff_skipped_statement_ids:
            ctx.tariff_skipped_statement_ids.remove(id(statement_tuple))
            continue

        statement = determine_statement_type(statement_tuple, namespaces, ctx)
        if statement is None:
            continue

        if ctx.pending_after:
            _drain_after(ctx.pending_after, ctx, wait=False)

        # Update current line for error reporting
        if hasattr(statement, "name") and hasattr(statement.name, "line"):
            ctx.current_line = statement.name.line
        elif hasattr(statement, "keyword") and hasattr(statement.keyword, "line"):
            ctx.current_line = statement.keyword.line

        match statement:
            case ExpressionStatement():
                expression = statement_expression(statement, ctx)
                result = evaluate_expression(
                    expression, namespaces,
                    async_statements, when_statement_watchers, ctx,
                )
                print_expression_debug(statement.debug, expression, result, namespaces, ctx)

            case VariableDeclaration():
                expression = statement_expression(statement, ctx)
                value = evaluate_expression(
                    expression, namespaces,
                    async_statements, when_statement_watchers, ctx,
                )
                print_expression_debug(
                    statement.debug, expression, value, namespaces, ctx,
                )
                declare_new_variable(statement, value, namespaces, async_statements, when_statement_watchers, ctx)

            case VariableAssignment():
                indexes = [
                    evaluate_expression(expr, namespaces, async_statements, when_statement_watchers, ctx)
                    for expr in statement_indexes(statement, ctx)
                ]
                new_value = evaluate_expression(
                    statement_expression(statement, ctx), namespaces,
                    async_statements, when_statement_watchers, ctx,
                )
                assign_variable(statement, indexes, new_value, namespaces, async_statements, when_statement_watchers, ctx)

            case ReturnStatement():
                expression = statement_expression(statement, ctx)
                result = evaluate_expression(
                    expression, namespaces,
                    async_statements, when_statement_watchers, ctx,
                )
                print_expression_debug(statement.debug, expression, result, namespaces, ctx)
                return ReturnSentinel(result)

            case Conditional():
                condition = evaluate_expression(
                    statement_expression(statement, ctx), namespaces,
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
                    statement_expression(statement, ctx), statement.code, namespaces,
                    async_statements, when_statement_watchers,
                    importable_names, exported_names, ctx,
                )

            case AfterStatement():
                delay_val = evaluate_expression(
                    statement_expression(statement, ctx),
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                    ctx,
                )
                delay_num = db_to_number(delay_val).value
                # `after` schedules work; it does not block the current block.
                # The queue is drained at statement boundaries and once more
                # when the program finishes.
                deadline = _time.monotonic() + max(0.0, delay_num / 1000.0)
                ctx.after_sequence += 1
                ctx.pending_after.append(
                    (
                        deadline,
                        ctx.after_sequence,
                        statement.code,
                        (namespaces, when_statement_watchers, importable_names, exported_names),
                    )
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
                class_obj.class_id = id(class_obj)
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
                            deleted_val = var.lifetimes[0].value
                            try:
                                ctx.deleted_values.add(deleted_val)
                            except TypeError:
                                pass  # unhashable values (e.g. GulfOfMexicoObject) are skipped
                            # Decrement class instance count so re-instantiation is allowed
                            if isinstance(deleted_val, GulfOfMexicoObject) and deleted_val.class_name:
                                class_key = deleted_val.class_id or deleted_val.class_name
                                count = ctx.class_instance_counts.get(class_key, 0)
                                if count > 0:
                                    ctx.class_instance_counts[class_key] = count - 1
                        elif isinstance(var, Name):
                            try:
                                ctx.deleted_values.add(var.value)
                            except TypeError:
                                pass  # unhashable values are skipped
                            # Decrement class instance count so re-instantiation is allowed
                            if isinstance(var.value, GulfOfMexicoObject) and var.value.class_name:
                                class_key = var.value.class_id or var.value.class_name
                                count = ctx.class_instance_counts.get(class_key, 0)
                                if count > 0:
                                    ctx.class_instance_counts[class_key] = count - 1
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
                    if isinstance(result, ReturnSentinel):
                        return result

            case ImportStatement():
                _time.sleep(random.uniform(0.005, 0.05))  # short random tariff delay

                if statement.source_file is not None:
                    source_name = statement.source_file.value
                    source_exports = importable_names.get(source_name)
                    if source_exports is None:
                        raise_error_at_token(
                            ctx.filename,
                            ctx.code,
                            f"Cannot find import source: {source_name}",
                            statement.source_file,
                        )
                    import_sources = [source_exports]
                else:
                    import_sources = list(importable_names.values())

                for name_token in statement.names:
                    name = name_token.value
                    found = False
                    for file_dict in import_sources:
                        if name in file_dict:
                            imported_val = file_dict[name]
                            namespaces[-1][name] = Name(name, imported_val)
                            found = True
                            break
                    if not found:
                        raise_error_at_token(ctx.filename, ctx.code, f"Cannot find imported name: {name}", name_token)

                force_remove = os.environ.get("GOM_FORCE_TARIFF_REMOVE") == "1"
                disable_tariff = os.environ.get("GOM_DISABLE_TARIFF") == "1"
                should_remove = not disable_tariff and (
                    force_remove or (random.random() < 0.25)
                )
                if should_remove:
                    future_indices = [
                        idx
                        for idx in range(statement_index + 1, len(statements))
                        if id(statements[idx]) not in ctx.tariff_skipped_statement_ids
                    ]
                    if future_indices:
                        forced_idx_raw = os.environ.get("GOM_FORCE_TARIFF_INDEX")
                        if forced_idx_raw is not None:
                            try:
                                forced_pos = int(forced_idx_raw)
                            except ValueError:
                                forced_pos = 0
                            forced_pos = max(0, min(forced_pos, len(future_indices) - 1))
                            remove_idx = future_indices[forced_pos]
                        else:
                            remove_idx = random.choice(future_indices)
                        ctx.tariff_skipped_statement_ids.add(id(statements[remove_idx]))

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
                            export_value = v.value if v.lifetimes else GulfOfMexicoUndefined()
                        else:
                            export_value = v
                        target = statement.target_file.value
                        exported_names.append((target, name, export_value))

        # Decrement line-based lifetimes. Only variables that were declared
        # with a finite lifetime are tracked, so the common case (no lifetimes)
        # costs a single falsy check per statement instead of a full scan of
        # every name in every scope.
        if ctx.ticking_lifetimes:
            for key, ticking in list(ctx.ticking_lifetimes.items()):
                for lt in ticking.lifetimes:  # type: ignore[attr-defined]
                    if lt.lines_left > 0:
                        lt.lines_left -= 1
                ticking.clear_outdated_lifetimes()  # type: ignore[attr-defined]
                if not ticking.lifetimes:  # type: ignore[attr-defined]
                    del ctx.ticking_lifetimes[key]

        # Per spec: async functions take turns with the caller line-by-line.
        # After each synchronous statement, execute one statement from each
        # queued async function (round-robin interleaving).
        if async_statements:
            next_round: AsyncStatements = []
            while async_statements:
                async_stmt = async_statements.pop(0)
                statements_list, async_namespaces, current_index, direction = async_stmt
                if current_index < len(statements_list):
                    interpret_code_statements(
                        [statements_list[current_index]],
                        async_namespaces, next_round,
                        when_statement_watchers, importable_names, exported_names, ctx,
                    )
                    new_index = current_index + (1 if direction == 1 else -1)
                    if 0 <= new_index < len(statements_list):
                        next_round.append((statements_list, async_namespaces, new_index, direction))
            async_statements.extend(next_round)

    # Drain any remaining async statements after the main loop finishes
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
