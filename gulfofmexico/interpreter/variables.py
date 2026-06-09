"""
Interpreter Variables - Declaration and Assignment

Handles ``const`` / ``var`` variable declarations (including
``const const const`` immutable globals, destructuring, lifetimes) and
variable assignment with indexed / dotted access.
"""

from __future__ import annotations

from gulfofmexico.base import (
    debug_print,
    raise_error_at_line,
    raise_error_at_token,
)
from gulfofmexico.builtin import (
    DateObject,
    GulfOfMexicoIndexable,
    GulfOfMexicoMutable,
    GulfOfMexicoNamespaceable,
    GulfOfMexicoNumber,
    GulfOfMexicoValue,
    Name,
    Variable,
    db_to_string,
)
from gulfofmexico.processor.expression_tree import ExpressionTreeNode
from gulfofmexico.processor.syntax_tree import (
    CodeStatement,
    VariableAssignment,
    VariableDeclaration,
)

from .context import (
    AsyncStatements,
    InterpreterContext,
    Namespace,
    WhenStatementWatchers,
)
from .expressions import (
    evaluate_expression,
    get_code_from_when_statement_watchers,
)
from .helpers import (
    check_type_annotation,
    gather_names_or_values,
    get_built_expression,
    get_modified_next_name,
)
from .namespaces import (
    get_name_and_namespace_from_namespaces,
    get_value_from_namespaces,
)
from .persistence import save_local_immutable_constant


# ---------------------------------------------------------------------------
# When-watcher helpers (re-exported from watchers module)
# ---------------------------------------------------------------------------

from .watchers import remove_from_when_statement_watchers  # noqa: E402


# ---------------------------------------------------------------------------
# Variable declaration
# ---------------------------------------------------------------------------

def declare_new_variable(
    statement: VariableDeclaration,
    value: GulfOfMexicoValue,
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    ctx: InterpreterContext,
) -> int:
    """Create a new variable based on a ``VariableDeclaration`` statement.

    Returns the number of lines to hoist (0 for normal declarations,
    >0 when a negative lifetime like ``<-1>`` is specified).
    """
    # Late import to break circular dependency
    from .execution import execute_conditional  # noqa: PLC0415

    name = statement.name.value
    confidence = statement.confidence
    lifetime = statement.lifetime

    can_be_reset = "var" in [mod.value for mod in statement.modifiers]
    can_edit_value = "const" not in [mod.value for mod in statement.modifiers]

    # Parse lifetime
    duration = 100_000_000_000
    is_temporal = False
    temporal_duration = 0.0
    hoist_lines = 0  # negative lifetime → hoist this many lines backward
    if lifetime:
        try:
            if lifetime.startswith("<") and lifetime.endswith(">"):
                inner = lifetime[1:-1]
                if inner.lower() == "infinity":
                    duration = 100_000_000_000
                elif inner.endswith("s"):
                    temporal_duration = float(inner[:-1])
                    duration = 100_000_000_000
                    is_temporal = True
                else:
                    val = float(inner)
                    if val < 0:
                        # Negative lifetime: variable hoisting per spec.
                        # Variable exists for abs(val) lines *before* its
                        # declaration line, then disappears after declaration.
                        hoist_lines = abs(int(val))
                        duration = 1  # expires after the declaration statement itself
                    else:
                        # Positive <N> lifetimes are statement-count based.
                        # Temporal lifetimes require an explicit seconds suffix: <Ns>
                        duration = int(val) + 1
                        is_temporal = False
            else:
                duration = int(lifetime)
        except ValueError:
            raise_error_at_token(
                ctx.filename, ctx.code,
                f"Invalid lifetime specification: {lifetime}",
                statement.name,
            )

    # Per spec: re-declaring a variable adds a new lifetime to the existing
    # Variable rather than replacing it, so that !-priority overloading works.
    existing = namespaces[-1].get(name)
    if isinstance(existing, Variable):
        var = existing
    else:
        var = Variable(name, [], [])
        namespaces[-1][name] = var
    var.add_lifetime(
        value, confidence, duration, can_be_reset, can_edit_value,
        is_temporal=is_temporal, temporal_duration=temporal_duration,
    )

    if statement.type_annotation:
        if not check_type_annotation(statement.type_annotation, value):
            type_name = "".join(
                tok.value for tok in statement.type_annotation
            ).strip()
            raise_error_at_token(
                ctx.filename, ctx.code,
                f"Type mismatch: value does not match declared type "
                f"'{type_name}'.",
                statement.name,
            )

    # const const const → save as immutable global constant
    is_triple_const = len(statement.modifiers) == 3 and all(mod.value == "const" for mod in statement.modifiers)
    if is_triple_const:
        save_local_immutable_constant(name, value, confidence)

    # Trigger when-statement watchers
    when_watchers = get_code_from_when_statement_watchers(id(var), when_statement_watchers)
    for when_watcher in when_watchers:
        condition, inside_statements, _captured_ns = when_watcher
        condition_val = evaluate_expression(condition, namespaces, async_statements, when_statement_watchers, ctx)
        if isinstance(value, GulfOfMexicoMutable):
            if id(value) not in when_statement_watchers[-1]:
                when_statement_watchers[-1][id(value)] = []
            when_statement_watchers[-1][id(value)].append(when_watcher)
        execute_conditional(
            condition_val, inside_statements, namespaces,
            when_statement_watchers, {}, [], ctx,
        )

    # Destructuring
    if statement.destructure_names and len(statement.destructure_names) > 1:
        for destr_name_token in statement.destructure_names[1:]:
            destr_var = Variable(destr_name_token.value, [], [])
            destr_var.add_lifetime(
                value, confidence, duration, can_be_reset, can_edit_value,
                is_temporal=is_temporal, temporal_duration=temporal_duration,
            )
            namespaces[-1][destr_name_token.value] = destr_var

    return hoist_lines


# ---------------------------------------------------------------------------
# Variable assignment
# ---------------------------------------------------------------------------

def assign_variable(
    statement: VariableAssignment,
    indexes: list[GulfOfMexicoValue],
    new_value: GulfOfMexicoValue,
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    ctx: InterpreterContext,
) -> None:
    """Assign *new_value* to the variable described by *statement*."""
    # Late import to break circular dependency
    from .execution import execute_conditional  # noqa: PLC0415
    from .watchers import interpret_name_watching_statement  # noqa: PLC0415

    name, confidence, debug = statement.name.value, statement.confidence, statement.debug
    name_token = statement.name

    # Special case: Date.now = <value> per spec (settable clock)
    if name == "Date.now":
        if isinstance(new_value, GulfOfMexicoNumber):
            # Compute offset from current real time so Date.now() returns the requested value
            import time as _time
            desired_ms = new_value.value
            current_ms = int(_time.time() * 1000)
            DateObject.set_offset(float(desired_ms - current_ms))
        return

    var, _ns = get_name_and_namespace_from_namespaces(name, namespaces)

    # Dotted property assignment
    dotted_target = None
    if var is None and "." in name:
        parts = name.split(".")
        base_name, tail = parts[0], parts[1:]
        base_entry, _ = get_name_and_namespace_from_namespaces(base_name, namespaces)
        if base_entry is None:
            raise_error_at_token(ctx.filename, ctx.code, "Attempted to set a name that is undefined.", name_token)
        container_val = base_entry.value  # type: ignore[attr-defined]
        for seg in tail[:-1]:
            if not isinstance(container_val, GulfOfMexicoNamespaceable) or seg not in container_val.namespace:
                raise_error_at_token(ctx.filename, ctx.code, "Attempted to set a name that is undefined.", name_token)
            next_entry = container_val.namespace[seg]
            container_val = next_entry.value  # type: ignore[attr-defined]
        if not isinstance(container_val, GulfOfMexicoNamespaceable):
            raise_error_at_token(ctx.filename, ctx.code, "Attempted to set a name that is undefined.", name_token)
        dotted_target = (container_val, tail[-1])
    elif var is None:
        raise_error_at_token(ctx.filename, ctx.code, "Attempted to set a name that is undefined.", name_token)

    # Debug output
    _emit_assign_debug(debug, statement, indexes, new_value, namespaces, ctx)

    visited_whens: list[tuple[ExpressionTreeNode, list[tuple[CodeStatement, ...]], list[dict[str, Variable | Name]]]] = []

    if indexes:
        def _assign_indexed(
            value_to_modify: GulfOfMexicoValue,
            remaining_indexes: list[GulfOfMexicoValue],
        ) -> None:
            if not value_to_modify or not isinstance(value_to_modify, GulfOfMexicoIndexable):
                raise_error_at_line(ctx.filename, ctx.code, name_token.line, "Attempted to index into an un-indexable object.")
            index = remaining_indexes.pop(0)
            if not remaining_indexes:
                value_to_modify.assign_index(index, new_value)
            else:
                _assign_indexed(value_to_modify.access_index(index), remaining_indexes)
            when_watchers = get_code_from_when_statement_watchers(id(value_to_modify), when_statement_watchers)
            for when_watcher in when_watchers:
                if any(when_watcher == x for x in visited_whens):
                    continue
                condition, inside_statements, captured_namespaces = when_watcher
                condition_val = evaluate_expression(condition, namespaces, async_statements, when_statement_watchers, ctx)
                execute_conditional(condition_val, inside_statements, namespaces, when_statement_watchers, {}, [], ctx)
                visited_whens.append(when_watcher)

        if dotted_target is not None:
            container_val, key = dotted_target
            entry = container_val.namespace.get(key)
            if entry is None:
                raise_error_at_token(ctx.filename, ctx.code, "Attempted to index into an undefined property.", name_token)
            _assign_indexed(entry.value, indexes)  # type: ignore[attr-defined]
        else:
            if isinstance(var, Variable):
                _assign_indexed(var.value, indexes)
            else:
                raise_error_at_token(ctx.filename, ctx.code, "Cannot assign to an index of a non-variable name.", name_token)
    else:
        if dotted_target is not None:
            container_val, key = dotted_target
            existing = container_val.namespace.get(key)
            if existing is None:
                container_val.namespace[key] = Name(key, new_value)
            elif isinstance(existing, Variable):
                if not existing.can_be_reset:
                    raise_error_at_token(ctx.filename, ctx.code, "Attempted to set a variable that cannot be set.", name_token)
                existing.add_lifetime(new_value, confidence, 100_000_000_000, existing.can_be_reset, existing.can_edit_value, is_temporal=False, temporal_duration=0.0)
            else:
                existing.value = new_value  # type: ignore[attr-defined]
        else:
            if not isinstance(var, Variable):
                raise_error_at_token(ctx.filename, ctx.code, "Attempted to set name that is not a variable.", name_token)
            if not var.can_be_reset:
                raise_error_at_token(ctx.filename, ctx.code, "Attempted to set a variable that cannot be set.", name_token)
            var.add_lifetime(new_value, confidence, 100_000_000_000, var.can_be_reset, var.can_edit_value, is_temporal=False, temporal_duration=0.0)

    # Name watchers (next-value tracking)
    # Use the namespace where the variable was found (_ns), not the innermost scope
    watchers_key = (name, id(_ns) if _ns is not None else id(namespaces[-1]))
    if watcher := ctx.name_watchers.get(watchers_key):
        st, stored_nexts, watcher_ns, promise = watcher
        mod_name = get_modified_next_name(*watchers_key)
        watcher_ns[-1][mod_name] = Name(mod_name, new_value)
        stored_nexts.remove(watchers_key)
        # Resolve the promise with the new value
        if promise is not None:
            promise.value = new_value
        if not stored_nexts:
            interpret_name_watching_statement(st, watcher_ns, promise, async_statements, when_statement_watchers, ctx)
        del ctx.name_watchers[watchers_key]

    # When-statement watchers
    if when_watchers_list := get_code_from_when_statement_watchers(id(var), when_statement_watchers):
        for when_watcher in when_watchers_list:
            condition, inside_statements, captured_namespaces = when_watcher
            # Evaluate condition with CURRENT namespaces (not stale captured copies)
            condition_val = evaluate_expression(condition, namespaces, async_statements, when_statement_watchers, ctx)
            if isinstance(new_value, GulfOfMexicoMutable):
                if id(new_value) not in when_statement_watchers[-1]:
                    when_statement_watchers[-1][id(new_value)] = []
                if when_watcher not in when_statement_watchers[-1][id(new_value)]:
                    when_statement_watchers[-1][id(new_value)].append(when_watcher)
            if isinstance(var, Variable):
                if var.prev_values and isinstance(var.prev_values[-1], GulfOfMexicoMutable):
                    remove_from_when_statement_watchers(id(var.prev_values[-1]), when_watcher, when_statement_watchers)
            if id(var) not in when_statement_watchers[-1]:
                when_statement_watchers[-1][id(var)] = []
            if when_watcher not in when_statement_watchers[-1][id(var)]:
                when_statement_watchers[-1][id(var)].append(when_watcher)
            execute_conditional(condition_val, inside_statements, namespaces, when_statement_watchers, {}, [], ctx)


# ---------------------------------------------------------------------------
# Assignment debug helper
# ---------------------------------------------------------------------------

def _emit_assign_debug(
    debug: int,
    statement: VariableAssignment,
    indexes: list[GulfOfMexicoValue],
    new_value: GulfOfMexicoValue,
    namespaces: list[Namespace],
    ctx: InterpreterContext,
) -> None:
    """Emit debug output for variable assignment based on *debug* level."""
    if debug == 0:
        return

    idx_str = "".join(f"[{db_to_string(val).value}]" for val in indexes)
    base_msg = f"Setting {statement.name.value}{idx_str} to {db_to_string(new_value).value}"

    if debug == 1:
        debug_print(ctx.filename, ctx.code, base_msg, statement.name)
        return

    expr = get_built_expression(statement.expression)
    names = gather_names_or_values(expr)

    name_values = "\n".join(
        f"  {name}: {db_to_string(get_value_from_namespaces(name, namespaces, ctx)).value}"
        for name in names
    )
    msg = f"{base_msg}\nThe value of each name in the expression is the following: \n{name_values}"

    if debug >= 3:
        msg += f"\nThe expression used to get this value is: \n{expr.to_string()}"

    if debug >= 4:
        index_exprs = [get_built_expression(ex) for ex in statement.indexes]
        for ex in index_exprs:
            names |= gather_names_or_values(ex)
        msg += "\nThe expression used to get the indexes are as follows: \n" + "\n\n".join(
            ex.to_string(1) for ex in index_exprs
        )

    debug_print(ctx.filename, ctx.code, msg, statement.name)
