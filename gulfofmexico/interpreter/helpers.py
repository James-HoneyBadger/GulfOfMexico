"""
Interpreter Helpers - Small Utility Functions

Pure utility functions with no circular dependencies on other interpreter
sub-modules.  These are used widely across the interpreter package.
"""

from __future__ import annotations

from typing import Union

from gulfofmexico.base import Token
from gulfofmexico.processor.expression_tree import (
    ExpressionNode,
    ExpressionTreeNode,
    FunctionNode,
    IndexNode,
    ListNode,
    SingleOperatorNode,
    ValueNode,
    build_expression_tree,
)


# ---------------------------------------------------------------------------
# Expression-tree helpers
# ---------------------------------------------------------------------------

def get_built_expression(expr: Union[list[Token], ExpressionTreeNode]) -> ExpressionTreeNode:
    """Ensure *expr* is an ``ExpressionTreeNode``, building one if needed."""
    if isinstance(expr, list):
        # We don't have filename/code here; callers should pass pre-built trees
        # when possible.  This fall-back keeps the original contract.
        return build_expression_tree("", expr, "")
    return expr


# ---------------------------------------------------------------------------
# Next / previous name modifiers
# ---------------------------------------------------------------------------

_NEXT_PREFIX = "__next__"
_PREV_PREFIX = "__prev__"


def get_modified_next_name(name: str, ns_id: int) -> str:
    """Return the mangled next-value name for *name* in namespace *ns_id*."""
    return f"{_NEXT_PREFIX}{name}_{ns_id}"


def get_modified_prev_name(name: str) -> str:
    """Return the mangled previous-value name."""
    return f"{_PREV_PREFIX}{name}"


# ---------------------------------------------------------------------------
# Gathering names from expression trees
# ---------------------------------------------------------------------------

def gather_names_or_values(expr: ExpressionTreeNode) -> set[Token]:
    """Collect all ``ValueNode`` tokens reachable from *expr*."""
    names: set[Token] = set()
    match expr:
        case FunctionNode():
            for arg in expr.args:
                names |= gather_names_or_values(arg)
        case ListNode():
            for val in expr.values:
                names |= gather_names_or_values(val)
        case ExpressionNode():
            names |= gather_names_or_values(expr.right) | gather_names_or_values(expr.left)
        case IndexNode():
            names |= gather_names_or_values(expr.index) | gather_names_or_values(expr.value)
        case SingleOperatorNode():
            names |= gather_names_or_values(expr.expression)
        case ValueNode():
            names.add(expr.name_or_value)
    return names


# ---------------------------------------------------------------------------
# Type annotation checking
# ---------------------------------------------------------------------------

# Map of documented annotation names to a predicate over a GulfOfMexico value.
# Unknown annotation names (e.g. user class names) are not enforced.
def _annotation_name(annotation: Union[str, list]) -> str:
    """Normalize a parsed annotation (token list or string) to a plain name."""
    if isinstance(annotation, str):
        return annotation.strip()
    # annotation is a list of Tokens
    return "".join(getattr(tok, "value", str(tok)) for tok in annotation).strip()


def check_type_annotation(
    annotation: Union[str, list],
    value: object = None,
) -> bool:
    """Validate *value* against a declared type *annotation*.

    Returns ``True`` when the value satisfies the annotation (or when the
    annotation names an unknown/custom type, which is not enforced). Returns
    ``False`` when a recognized annotation is violated. Uninitialized values
    (``undefined``) are always accepted.

    The recognized annotation names follow the language reference §3.3:
    ``Int``/``Integer``, ``Float``/``Number``/``Num``, ``String``/``Str``,
    ``Bool``/``Boolean``, ``List``/``Array``, ``Map``, ``Object``,
    ``Function``/``Func``/``Fn``.
    """
    from gulfofmexico.builtin import (  # local import avoids circular deps
        GulfOfMexicoBoolean,
        GulfOfMexicoFunction,
        GulfOfMexicoList,
        GulfOfMexicoMap,
        GulfOfMexicoNumber,
        GulfOfMexicoObject,
        GulfOfMexicoString,
        GulfOfMexicoUndefined,
        is_int,
    )

    name = _annotation_name(annotation)
    if not name or value is None:
        return True
    # Uninitialized declarations carry an undefined value; don't enforce.
    if isinstance(value, GulfOfMexicoUndefined):
        return True

    key = name.lower()
    if key in ("int", "integer"):
        return isinstance(value, GulfOfMexicoNumber) and is_int(value.value)
    if key in ("float", "number", "num"):
        return isinstance(value, GulfOfMexicoNumber)
    if key in ("string", "str"):
        return isinstance(value, GulfOfMexicoString)
    if key in ("bool", "boolean"):
        return isinstance(value, GulfOfMexicoBoolean)
    if key in ("list", "array"):
        return isinstance(value, GulfOfMexicoList)
    if key == "map":
        return isinstance(value, GulfOfMexicoMap)
    if key == "object":
        return isinstance(value, GulfOfMexicoObject)
    if key in ("function", "func", "fn"):
        return isinstance(value, GulfOfMexicoFunction)
    # Unknown / custom type names are not enforced.
    return True
