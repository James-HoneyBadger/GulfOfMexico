"""Utility functions for the Gulf of Mexico interpreter."""

from typing import Optional, Union
from gulfofmexico.builtin import (
    GulfOfMexicoValue,
    Variable,
    Name,
)


def get_variable_value(
    var: Union[Variable, Name, GulfOfMexicoValue],
) -> GulfOfMexicoValue:
    """Extract the underlying value from a Variable or Name object.

    Args:
        var: Variable, Name, or direct GulfOfMexicoValue

    Returns:
        The underlying GulfOfMexicoValue
    """
    if isinstance(var, Variable):
        return var.value
    elif isinstance(var, Name):
        return var.value
    else:
        return var


def is_truthy(value: GulfOfMexicoValue) -> bool:
    """Check if a value is truthy in Gulf of Mexico semantics.

    Args:
        value: The value to check

    Returns:
        True if the value is truthy, False otherwise
    """
    from gulfofmexico.builtin import (
        GulfOfMexicoBoolean,
        GulfOfMexicoNumber,
        GulfOfMexicoString,
        GulfOfMexicoList,
        GulfOfMexicoUndefined,
    )

    if isinstance(value, GulfOfMexicoBoolean):
        return value.value
    elif isinstance(value, GulfOfMexicoNumber):
        return value.value != 0
    elif isinstance(value, GulfOfMexicoString):
        return len(value.value) > 0
    elif isinstance(value, GulfOfMexicoList):
        return len(value.values) > 0
    elif isinstance(value, GulfOfMexicoUndefined):
        return False
    else:
        return True  # Objects are always truthy


def safe_int_convert(value: float) -> int:
    """Safely convert a float to int, handling precision issues.

    Args:
        value: Float value to convert

    Returns:
        Integer value
    """
    from gulfofmexico.builtin import FLOAT_TO_INT_PREC

    if abs(value - round(value)) < FLOAT_TO_INT_PREC:
        return round(value)
    return int(value)


def clone_namespaces(namespaces: list[dict]) -> list[dict]:
    """Create a deep copy of namespace stack.

    Args:
        namespaces: Stack of namespace dictionaries

    Returns:
        Deep copy of namespace stack
    """
    from copy import deepcopy

    return [deepcopy(ns) for ns in namespaces]


def find_in_namespaces(
    name: str,
    namespaces: list[dict],
) -> tuple[Optional[Union[Variable, Name]], Optional[dict]]:
    """Find a name in the namespace stack.

    Args:
        name: Name to find
        namespaces: Stack of namespace dictionaries

    Returns:
        Tuple of (Variable/Name if found, namespace dict if found)
    """
    for namespace in reversed(namespaces):
        if name in namespace:
            return namespace[name], namespace
    return None, None
