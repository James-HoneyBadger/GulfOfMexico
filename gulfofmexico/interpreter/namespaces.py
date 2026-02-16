"""
Interpreter Namespaces - Scope Lookup and Value Resolution

Functions for searching through nested namespaces to find variables and
names, plus fallback literal-value resolution (zero-quote strings, numbers,
booleans).
"""

from __future__ import annotations

from typing import Optional, Union

from gulfofmexico.base import (
    Token,
    TokenType,
    raise_error_at_token,
)
from gulfofmexico.builtin import (
    GulfOfMexicoBoolean,
    GulfOfMexicoNamespaceable,
    GulfOfMexicoNumber,
    GulfOfMexicoString,
    GulfOfMexicoUndefined,
    GulfOfMexicoValue,
    Name,
    Variable,
)

from .context import InterpreterContext, Namespace


# ---------------------------------------------------------------------------
# Namespace lookup
# ---------------------------------------------------------------------------

def get_name_from_namespaces(name: str, namespaces: list[Namespace]) -> Optional[Union[Variable, Name]]:
    """Look up *name* across namespaces (most-local scope first).

    Supports dotted access for namespaceable values (objects, lists, strings).
    """
    # Fast path for simple names
    if "." not in name:
        for namespace in reversed(namespaces):
            if name in namespace:
                return namespace[name]
        return None

    parts = name.split(".")
    base_entry: Optional[Union[Variable, Name]] = None
    for namespace in reversed(namespaces):
        if parts[0] in namespace:
            base_entry = namespace[parts[0]]
            break
    if base_entry is None:
        return None

    current_value: GulfOfMexicoValue = base_entry.value  # type: ignore[attr-defined]
    current_entry: Optional[Union[Variable, Name]] = base_entry
    for seg in parts[1:]:
        if not isinstance(current_value, GulfOfMexicoNamespaceable):
            return None
        if seg not in current_value.namespace:
            return None
        current_entry = current_value.namespace[seg]
        current_value = current_entry.value  # type: ignore[attr-defined]
    return current_entry


def get_name_and_namespace_from_namespaces(
    name: str, namespaces: list[Namespace]
) -> tuple[Optional[Union[Variable, Name]], Optional[Namespace]]:
    """Return ``(entry, containing_namespace)`` for *name*."""
    for namespace in reversed(namespaces):
        if name in namespace:
            return namespace[name], namespace
    return None, None


# ---------------------------------------------------------------------------
# Literal-value resolution (for tokens not found in namespaces)
# ---------------------------------------------------------------------------

def determine_non_name_value(name_or_value: Token, ctx: InterpreterContext) -> GulfOfMexicoValue:
    """Resolve a token to a literal value when it has no namespace binding."""
    match name_or_value.type:
        case TokenType.STRING:
            return GulfOfMexicoString(name_or_value.value)
        case TokenType.NAME:
            try:
                if "." not in name_or_value.value and "e" not in name_or_value.value.lower():
                    return GulfOfMexicoNumber(int(name_or_value.value))
                else:
                    return GulfOfMexicoNumber(float(name_or_value.value))
            except ValueError:
                if name_or_value.value in ("true", "false", "maybe", "undefined"):
                    match name_or_value.value:
                        case "true":
                            return GulfOfMexicoBoolean(True)
                        case "false":
                            return GulfOfMexicoBoolean(False)
                        case "maybe":
                            return GulfOfMexicoBoolean(None)
                        case "undefined":
                            return GulfOfMexicoUndefined()
                # Zero-quote string per spec: bare words become strings
                return GulfOfMexicoString(name_or_value.value)
        case _:
            raise_error_at_token(
                ctx.filename, ctx.code,
                f"Unexpected token type: {name_or_value.type}",
                name_or_value,
            )


def get_value_from_namespaces(
    name_or_value: Token,
    namespaces: list[Namespace],
    ctx: InterpreterContext,
) -> GulfOfMexicoValue:
    """Resolve a token to its value, checking namespaces first then literals."""
    from gulfofmexico.builtin import GulfOfMexicoPromise  # avoid top-level circular

    if v := get_name_from_namespaces(name_or_value.value, namespaces):
        if isinstance(v.value, GulfOfMexicoPromise):
            from copy import deepcopy
            promise_value = deepcopy(v.value.value)
            if promise_value is not None:
                return promise_value
            return GulfOfMexicoUndefined()
        return v.value
    return determine_non_name_value(name_or_value, ctx)
