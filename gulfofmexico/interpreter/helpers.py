"""
Interpreter Helpers - Small Utility Functions

Pure utility functions with no circular dependencies on other interpreter
sub-modules.  These are used widely across the interpreter package.
"""

from __future__ import annotations

from typing import Union

from gulfofmexico.base import Token, TokenType
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
# Type annotation stub
# ---------------------------------------------------------------------------

def check_type_annotation(annotation: str) -> bool:  # noqa: ARG001
    """Placeholder — type annotations are parsed but not enforced at runtime."""
    return True
