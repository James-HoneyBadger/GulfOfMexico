"""
Interpreter Operators - Equality, Comparison, and Arithmetic

Pure functions for Gulf of Mexico's tiered equality system and arithmetic.
Only depends on the InterpreterContext for error reporting via
``raise_error_at_token`` / ``raise_error_at_line``.
"""

from __future__ import annotations

import random

from difflib import SequenceMatcher

from gulfofmexico.base import (
    OperatorType,
    Token,
    TokenType,
    raise_error_at_line,
    raise_error_at_token,
)
from gulfofmexico.builtin import (
    FLOAT_TO_INT_PREC,
    GulfOfMexicoBoolean,
    GulfOfMexicoFunction,
    GulfOfMexicoList,
    GulfOfMexicoMap,
    GulfOfMexicoNumber,
    GulfOfMexicoObject,
    GulfOfMexicoString,
    GulfOfMexicoUndefined,
    GulfOfMexicoValue,
    db_not,
    db_to_boolean,
    db_to_number,
    db_to_string,
    is_int,
)

from .context import (
    NUM_EQUALITY_THRESHOLD,
    STRING_EQUALITY_RATIO,
    LIST_EQUALITY_RATIO,
    MAP_EQUALITY_RATIO,
    OBJECT_EQUALITY_RATIO,
    InterpreterContext,
)


# ---------------------------------------------------------------------------
# Tiered equality
# ---------------------------------------------------------------------------

def is_approx_equal(left: GulfOfMexicoValue, right: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    """Approximate equality with fuzzy matching based on ratios."""
    if not isinstance(left, type(right)):
        return GulfOfMexicoBoolean(False)

    match left:
        case GulfOfMexicoNumber():
            if not isinstance(right, GulfOfMexicoNumber):
                return GulfOfMexicoBoolean(False)
            if left.value == right.value:
                return GulfOfMexicoBoolean(True)
            if abs(left.value) < FLOAT_TO_INT_PREC and abs(right.value) < FLOAT_TO_INT_PREC:
                return GulfOfMexicoBoolean(True)
            return GulfOfMexicoBoolean(abs(left.value - right.value) <= NUM_EQUALITY_THRESHOLD)

        case GulfOfMexicoString():
            if not isinstance(right, GulfOfMexicoString):
                return GulfOfMexicoBoolean(False)
            if left.value == right.value:
                return GulfOfMexicoBoolean(True)
            ratio = SequenceMatcher(None, left.value, right.value).ratio()
            return GulfOfMexicoBoolean(ratio >= STRING_EQUALITY_RATIO)

        case GulfOfMexicoList():
            if not isinstance(right, GulfOfMexicoList):
                return GulfOfMexicoBoolean(False)
            if len(left.values) != len(right.values):
                return GulfOfMexicoBoolean(False)
            if len(left.values) == 0:
                return GulfOfMexicoBoolean(True)
            equal_count = sum(
                1 for l_val, r_val in zip(left.values, right.values)
                if is_approx_equal(l_val, r_val).value
            )
            ratio = equal_count / len(left.values)
            return GulfOfMexicoBoolean(ratio >= LIST_EQUALITY_RATIO)

        case GulfOfMexicoMap():
            if not isinstance(right, GulfOfMexicoMap):
                return GulfOfMexicoBoolean(False)
            if len(left.self_dict) != len(right.self_dict):
                return GulfOfMexicoBoolean(False)
            if len(left.self_dict) == 0:
                return GulfOfMexicoBoolean(True)
            equal_count = sum(
                1 for key in left.self_dict
                if key in right.self_dict
                and is_approx_equal(left.self_dict[key], right.self_dict[key]).value
            )
            ratio = equal_count / len(left.self_dict)
            return GulfOfMexicoBoolean(ratio >= MAP_EQUALITY_RATIO)

        case GulfOfMexicoFunction():
            if not isinstance(right, GulfOfMexicoFunction):
                return GulfOfMexicoBoolean(False)
            if left.args == right.args and left.code == right.code and left.is_async == right.is_async:
                return GulfOfMexicoBoolean(True)
            return GulfOfMexicoBoolean(False)

        case GulfOfMexicoObject():
            if not isinstance(right, GulfOfMexicoObject):
                return GulfOfMexicoBoolean(False)
            if left.class_name != right.class_name:
                return GulfOfMexicoBoolean(False)
            total_count = len(left.namespace)
            if total_count == 0:
                return GulfOfMexicoBoolean(True)
            equal_count = sum(
                1 for key in left.namespace
                if key in right.namespace
                and is_approx_equal(left.namespace[key].value, right.namespace[key].value).value
            )
            ratio = equal_count / total_count
            return GulfOfMexicoBoolean(ratio >= OBJECT_EQUALITY_RATIO)

        case _:
            return GulfOfMexicoBoolean(left == right)


def is_equal(left: GulfOfMexicoValue, right: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    """Regular equality — stricter than approximate."""
    if not isinstance(left, type(right)):
        return GulfOfMexicoBoolean(False)

    match left:
        case GulfOfMexicoNumber():
            if not isinstance(right, GulfOfMexicoNumber):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(abs(left.value - right.value) < FLOAT_TO_INT_PREC)

        case GulfOfMexicoString():
            if not isinstance(right, GulfOfMexicoString):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(left.value == right.value)

        case GulfOfMexicoList():
            if not isinstance(right, GulfOfMexicoList):
                return GulfOfMexicoBoolean(False)
            if len(left.values) != len(right.values):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(
                all(is_equal(l_val, r_val).value for l_val, r_val in zip(left.values, right.values))
            )

        case GulfOfMexicoMap():
            if not isinstance(right, GulfOfMexicoMap):
                return GulfOfMexicoBoolean(False)
            if len(left.self_dict) != len(right.self_dict):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(
                all(
                    key in right.self_dict and is_equal(left.self_dict[key], right.self_dict[key]).value
                    for key in left.self_dict
                )
            )

        case GulfOfMexicoFunction():
            if not isinstance(right, GulfOfMexicoFunction):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(
                left.args == right.args and left.code == right.code and left.is_async == right.is_async
            )

        case GulfOfMexicoObject():
            if not isinstance(right, GulfOfMexicoObject):
                return GulfOfMexicoBoolean(False)
            if left.class_name != right.class_name:
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(
                all(
                    key in right.namespace
                    and is_equal(left.namespace[key].value, right.namespace[key].value).value
                    for key in left.namespace
                )
            )

        case _:
            return GulfOfMexicoBoolean(left == right)


def is_really_equal(left: GulfOfMexicoValue, right: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    """Really equal — checks identity for mutable objects."""
    if not isinstance(left, type(right)):
        return GulfOfMexicoBoolean(False)

    if isinstance(left, (GulfOfMexicoList, GulfOfMexicoMap, GulfOfMexicoObject)):
        return GulfOfMexicoBoolean(left is right)

    return is_equal(left, right)


def is_really_really_equal(left: GulfOfMexicoValue, right: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    """Really really equal — strictest equality, always checks identity."""
    return GulfOfMexicoBoolean(left is right)


# ---------------------------------------------------------------------------
# Tilde-equality: AEMI / ABI / AQMI  (per DreamBerd spec)
# ---------------------------------------------------------------------------

def is_aemi_equal(left: GulfOfMexicoValue, right: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    """~= AEMI (Assume Equal if Missing Information).

    Returns true unless there is clear evidence the values differ.
    Mismatched types => maybe (None).
    """
    if not isinstance(left, type(right)):
        # Different types — not enough info to decide
        return GulfOfMexicoBoolean(None)

    match left:
        case GulfOfMexicoNumber():
            assert isinstance(right, GulfOfMexicoNumber)
            if left.value == right.value:
                return GulfOfMexicoBoolean(True)
            # If either is zero and the other isn't, still "maybe"
            if left.value == 0 or right.value == 0:
                return GulfOfMexicoBoolean(None)
            return GulfOfMexicoBoolean(True)

        case GulfOfMexicoString():
            assert isinstance(right, GulfOfMexicoString)
            if left.value == right.value:
                return GulfOfMexicoBoolean(True)
            # If one is a substring of the other — maybe
            if left.value in right.value or right.value in left.value:
                return GulfOfMexicoBoolean(None)
            return GulfOfMexicoBoolean(True)

        case GulfOfMexicoBoolean():
            assert isinstance(right, GulfOfMexicoBoolean)
            if left.value is None or right.value is None:
                return GulfOfMexicoBoolean(None)
            return GulfOfMexicoBoolean(left.value == right.value)

        case _:
            return GulfOfMexicoBoolean(True)


def is_abi_equal(left: GulfOfMexicoValue, right: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    """~== ABI (Assume Better Interpretation).

    Coerces both values to the same type with the most favorable
    interpretation, then compares.
    """
    # Same types — use normal equality
    if isinstance(left, type(right)):
        # For strings, use case-insensitive comparison
        if isinstance(left, GulfOfMexicoString) and isinstance(right, GulfOfMexicoString):
            return GulfOfMexicoBoolean(left.value.lower() == right.value.lower())
        return is_equal(left, right)

    # Cross-type: coerce both to strings and compare case-insensitively
    left_str = db_to_string(left).value
    right_str = db_to_string(right).value
    return GulfOfMexicoBoolean(left_str.lower() == right_str.lower())


def is_aqmi_equal(left: GulfOfMexicoValue, right: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    """~=== AQMI (Assume Quantitative Match if Insignificant).

    For numbers: close enough (within 1% or 0.001 absolute).
    For strings: case-insensitive + whitespace-normalized exact match.
    Otherwise: strict equality.
    """
    if isinstance(left, GulfOfMexicoNumber) and isinstance(right, GulfOfMexicoNumber):
        if left.value == right.value:
            return GulfOfMexicoBoolean(True)
        diff = abs(left.value - right.value)
        # Absolute tolerance for small numbers
        if diff <= 0.001:
            return GulfOfMexicoBoolean(True)
        # Relative tolerance (1%)
        denom = max(abs(left.value), abs(right.value))
        if denom > 0 and diff / denom <= 0.01:
            return GulfOfMexicoBoolean(True)
        return GulfOfMexicoBoolean(False)

    if isinstance(left, GulfOfMexicoString) and isinstance(right, GulfOfMexicoString):
        return GulfOfMexicoBoolean(
            " ".join(left.value.lower().split()) == " ".join(right.value.lower().split())
        )

    # Fallback: coerce to numbers if possible, else strict equal
    try:
        left_n = db_to_number(left)
        right_n = db_to_number(right)
        return is_aqmi_equal(left_n, right_n)
    except Exception:
        return is_equal(left, right)


def is_less_than(left: GulfOfMexicoValue, right: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    """Less-than comparison."""
    if not isinstance(left, type(right)):
        return GulfOfMexicoBoolean(False)

    match left:
        case GulfOfMexicoNumber():
            if not isinstance(right, GulfOfMexicoNumber):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(left.value < right.value)

        case GulfOfMexicoString():
            if not isinstance(right, GulfOfMexicoString):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(left.value < right.value)

        case GulfOfMexicoList():
            if not isinstance(right, GulfOfMexicoList):
                return GulfOfMexicoBoolean(False)
            for l_val, r_val in zip(left.values, right.values):
                if is_really_equal(l_val, r_val).value:
                    continue
                return is_less_than(l_val, r_val)
            return GulfOfMexicoBoolean(len(left.values) < len(right.values))

        case _:
            return GulfOfMexicoBoolean(False)


# ---------------------------------------------------------------------------
# Two-value operations
# ---------------------------------------------------------------------------

def perform_two_value_operation(
    left: GulfOfMexicoValue,
    right: GulfOfMexicoValue,
    operator: OperatorType,
    operator_token: Token,
    ctx: InterpreterContext,
) -> GulfOfMexicoValue:
    """Apply a binary operator to *left* and *right*."""
    match operator:
        case OperatorType.ADD:
            if isinstance(left, GulfOfMexicoList) and isinstance(right, GulfOfMexicoList):
                return GulfOfMexicoList(left.values + right.values)
            if isinstance(left, GulfOfMexicoString) or isinstance(right, GulfOfMexicoString):
                return GulfOfMexicoString(db_to_string(left).value + db_to_string(right).value)
            left_num = db_to_number(left)
            right_num = db_to_number(right)
            return GulfOfMexicoNumber(left_num.value + right_num.value)

        case OperatorType.SUB | OperatorType.MUL | OperatorType.DIV | OperatorType.EXP:
            left_num = db_to_number(left)
            right_num = db_to_number(right)
            if operator == OperatorType.DIV and abs(right_num.value) < FLOAT_TO_INT_PREC:
                return GulfOfMexicoUndefined()
            elif operator == OperatorType.EXP and left_num.value < -FLOAT_TO_INT_PREC and not is_int(right_num.value):
                raise_error_at_line(
                    ctx.filename, ctx.code, ctx.current_line,
                    "Cannot raise a negative base to a non-integer exponent.",
                )
            match operator:
                case OperatorType.SUB:
                    result = left_num.value - right_num.value
                case OperatorType.MUL:
                    result = left_num.value * right_num.value
                case OperatorType.DIV:
                    result = left_num.value / right_num.value
                case OperatorType.EXP:
                    result = pow(left_num.value, right_num.value)
            return GulfOfMexicoNumber(result)

        case OperatorType.OR:
            left_bool = db_to_boolean(left)
            right_bool = db_to_boolean(right)
            match left_bool.value, right_bool.value:
                case True, _:
                    return left
                case False, _:
                    return right
                case None, True:
                    return right
                case None, False:
                    return left
                case None, None:
                    return left if random.random() < 0.50 else right

        case OperatorType.AND:
            left_bool = db_to_boolean(left)
            right_bool = db_to_boolean(right)
            match left_bool.value, right_bool.value:
                case True, _:
                    return right
                case False, _:
                    return left
                case None, True:
                    return left
                case None, False:
                    return right
                case None, None:
                    return left if random.random() < 0.50 else right

        case OperatorType.E:
            return is_approx_equal(left, right)

        case OperatorType.EE | OperatorType.NE:
            if operator == OperatorType.EE:
                return is_equal(left, right)
            return db_not(is_equal(left, right))

        case OperatorType.EEE | OperatorType.NEE:
            if operator == OperatorType.EEE:
                return is_really_equal(left, right)
            return db_not(is_really_equal(left, right))

        case OperatorType.EEEE | OperatorType.NEEE:
            if operator == OperatorType.EEEE:
                return is_really_really_equal(left, right)
            return db_not(is_really_really_equal(left, right))

        case OperatorType.TE:
            return is_aemi_equal(left, right)

        case OperatorType.TEE:
            return is_abi_equal(left, right)

        case OperatorType.TEEE:
            return is_aqmi_equal(left, right)

        case OperatorType.GT | OperatorType.LE:
            is_eq = is_really_equal(left, right)
            is_less = is_less_than(left, right)
            is_le: bool | None = False
            match is_eq.value, is_less.value:
                case (True, _) | (_, True):
                    is_le = True
                case (None, _) | (_, None):
                    is_le = None
            if operator == OperatorType.LE:
                return GulfOfMexicoBoolean(is_le)
            return db_not(GulfOfMexicoBoolean(is_le))

        case OperatorType.LT | OperatorType.GE:
            if operator == OperatorType.LT:
                return is_less_than(left, right)
            return db_not(is_less_than(left, right))

    raise_error_at_token(ctx.filename, ctx.code, "Something went wrong here.", operator_token)


# ---------------------------------------------------------------------------
# Single-value operations
# ---------------------------------------------------------------------------

def perform_single_value_operation(
    val: GulfOfMexicoValue,
    operator_token: Token,
    ctx: InterpreterContext,
) -> GulfOfMexicoValue:
    """Apply a unary operator to *val*."""
    match operator_token.type:
        case TokenType.SUBTRACT:
            match val:
                case GulfOfMexicoNumber():
                    return GulfOfMexicoNumber(-val.value)
                case GulfOfMexicoList():
                    return GulfOfMexicoList(val.values[::-1])
                case GulfOfMexicoString():
                    return GulfOfMexicoString(val.value[::-1])
                case _:
                    raise_error_at_token(
                        ctx.filename, ctx.code,
                        f"Cannot negate a value of type {type(val).__name__}",
                        operator_token,
                    )
        case TokenType.SEMICOLON:
            val_bool = db_to_boolean(val)
            return db_not(val_bool)
        case TokenType.INCREMENT:
            match val:
                case GulfOfMexicoNumber():
                    return GulfOfMexicoNumber(val.value + 1)
                case _:
                    raise_error_at_token(
                        ctx.filename, ctx.code,
                        f"Cannot increment a value of type {type(val).__name__}",
                        operator_token,
                    )
        case TokenType.DECREMENT:
            match val:
                case GulfOfMexicoNumber():
                    return GulfOfMexicoNumber(val.value - 1)
                case _:
                    raise_error_at_token(
                        ctx.filename, ctx.code,
                        f"Cannot decrement a value of type {type(val).__name__}",
                        operator_token,
                    )

    raise_error_at_token(ctx.filename, ctx.code, "Something went wrong. My bad.", operator_token)
