"""
Base Types and Utilities for Gulf of Mexico

Defines core types used throughout the interpreter.

Core Types:
    - Token: Lexer output representing code elements
    - TokenType: Enum of all token types
    - OperatorType: Enum of binary operators

Error Handling:
    - InterpretationError: Raised for Gulf of Mexico runtime errors
    - NonFormattedError: Raised for internal errors
    - raise_error_at_token(): Display error with source location
    - raise_error_at_line(): Display error at line number
    - debug_print(): Print debug messages with source context

Constants:
    - ALPH_NUMS: Valid characters in names (includes dots for namespaces)
    - STR_TO_OPERATOR: Maps operator strings to OperatorType

Presentation:
    Diagnostics and debug output are rendered by :mod:`gulfofmexico.ui`, which
    owns the colour policy (NO_COLOR / FORCE_COLOR / TTY detection) and the
    compiler-style message layout.
"""

from __future__ import annotations

import os
import sys
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from typing import NoReturn, Optional

from gulfofmexico.ui import Diagnostic, render_diagnostic

# ASCII fast-path set for performance
_ASCII_ALPH_NUMS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.")


#: Recursion ceiling for executing Gulf of Mexico programs. Deep enough for
#: realistic recursive algorithms while staying inside CPython's C stack, so a
#: runaway recursion raises RecursionError instead of crashing the process.
DEFAULT_RECURSION_LIMIT = 10_000


def configure_recursion_limit() -> int:
    """Raise the interpreter's recursion ceiling for nested GOM calls.

    Overridable with ``GOM_RECURSION_LIMIT`` for programs that legitimately
    recurse deeper (the only iteration mechanism the language has).
    """
    limit = DEFAULT_RECURSION_LIMIT
    raw = os.environ.get("GOM_RECURSION_LIMIT")
    if raw:
        try:
            limit = max(1_000, int(raw))
        except ValueError:
            pass
    if limit > sys.getrecursionlimit():
        sys.setrecursionlimit(limit)
    return limit


#: Memoised results of the (comparatively expensive) Unicode category lookup.
_NAME_CHAR_CACHE: dict[str, bool] = {}
_NAME_CHAR_CATEGORIES = frozenset({"Pc", "So", "Mn", "Me", "Cf"})


def is_alph_num(c: str) -> bool:
    """Check if a character is valid in a name (supports Unicode letters/digits/emoji per spec)."""
    if c in _ASCII_ALPH_NUMS:
        return True
    cached = _NAME_CHAR_CACHE.get(c)
    if cached is not None:
        return cached
    cat = unicodedata.category(c)
    # L* = letters, N* = numbers, Pc = connector punctuation (e.g. _),
    # So = Symbol other (emoji), Mn/Me = combining marks (e.g. keycap emoji
    # like 1️⃣), Cf = format characters (e.g. zero-width joiner in emoji
    # sequences) per DreamBerd's "any Unicode character" naming rule.
    result = cat[0] in ("L", "N") or cat in _NAME_CHAR_CATEGORIES
    if len(_NAME_CHAR_CACHE) < 65_536:
        _NAME_CHAR_CACHE[c] = result
    return result


# Keep ALPH_NUMS as alias for backward compatibility in imports
ALPH_NUMS = _ASCII_ALPH_NUMS


class NonFormattedError(Exception):
    """Internal error without source code formatting."""


class InterpretationError(Exception):
    """Gulf of Mexico runtime error with formatted message."""

    _: str  # Intentionally obfuscated for style


def _source_line(code: str, line: int) -> Optional[str]:
    """Return 1-based *line* from *code*, or ``None`` when out of range."""
    if not code or line < 1:
        return None
    lines = code.split("\n")
    return lines[line - 1] if line <= len(lines) else None


def _token_column(token: Token) -> int:
    """1-based start column of *token*."""
    return max(1, token.col - len(token.value) + 1)


def _diagnostic(
    filename: str,
    code: str,
    message: str,
    token: Optional[Token],
    kind: str = "error",
) -> str:
    """Build the rendered diagnostic string for *message*."""
    if token is None:
        return render_diagnostic(
            Diagnostic(message=message, filename=filename, kind=kind)
        )
    return render_diagnostic(
        Diagnostic(
            message=message,
            filename=filename,
            line=token.line,
            column=_token_column(token),
            length=max(1, len(token.value)),
            kind=kind,
            source_line=_source_line(code, token.line),
        )
    )


def debug_print(filename: str, code: str, message: str, token: Token) -> None:
    """Print debug information with source context.

    Used by the `?` and `??` debug modifiers. The message and code frame are
    rendered by :func:`gulfofmexico.ui.render_diagnostic` so debug output
    matches the rest of the toolchain's visual language.
    """
    print()
    print(_diagnostic(filename, code, message, token, kind="info"))
    print()


def debug_print_no_token(filename: str, message: str) -> None:
    print()
    print(_diagnostic(filename, "", message, None, kind="info"))
    print()


def raise_error_at_token(filename: str, code: str, message: str, token: Token) -> NoReturn:
    """Raise an :class:`InterpretationError` pointing at *token*."""
    raise InterpretationError(_diagnostic(filename, code, message, token))


def raise_error_at_line(filename: str, code: str, line: int, message: str) -> NoReturn:
    """Raise an :class:`InterpretationError` for a whole source *line*."""
    raise InterpretationError(
        render_diagnostic(
            Diagnostic(
                message=message,
                filename=filename,
                line=line,
                kind="error",
                source_line=_source_line(code, line),
            )
        )
    )


class TokenType(Enum):
    R_CURLY = "}"
    L_CURLY = "{"
    R_SQUARE = "]"
    L_SQUARE = "["
    L_PAREN = "("
    R_PAREN = ")"
    # Synthetic token produced when parenthesised expressions are grouped.
    # It carries the already-built expression tree (see Token.tree).
    PAREN_GROUP = "paren_group"

    DOT = "."
    ADD = "+"
    INCREMENT = "++"
    DECREMENT = "--"
    EQUAL = "="
    DIVIDE = "/"
    MULTIPLY = "*"
    SUBTRACT = "-"

    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"
    BANG = "!"
    QUESTION = "?"
    CARROT = "^"
    FUNC_POINT = "=>"

    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    NOT_EQUAL = ";="  # !@# !@# !@#
    PIPE = "|"
    AND = "&"
    COMPOUND_ASSIGN = "compound_assign"  # +=, -=, *=, /=, ^=

    WHITESPACE = "       "
    NAME = "abcaosdijawef"  # i'm losing my mind
    STRING = "'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"

    NEWLINE = "\n"
    SINGLE_QUOTE = "'"  # this is ugly as hell
    DOUBLE_QUOTE = '"'

    @classmethod
    def from_val(cls, val: str) -> Optional[TokenType]:
        return {v.value: v for v in list(cls)}.get(val)


class OperatorType(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    EXP = "^"
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    OR = "|"
    AND = "&"
    COM = ","  # this is just here to separate variables in a function
    E = "="
    EE = "=="
    EEE = "==="
    EEEE = "===="
    NE = ";="
    NEE = ";=="
    NEEE = ";==="
    TE = "~="
    TEE = "~=="
    TEEE = "~==="


STR_TO_OPERATOR = {op.value: op for op in OperatorType}


# why do i even need a damn class for this
# 3 weeks later, i am very glad i made a class for this
@dataclass(unsafe_hash=True)
class Token:
    type: TokenType
    value: str
    line: int = field(hash=False)
    col: int = field(hash=False)
    # Only used by PAREN_GROUP tokens: the expression tree that the
    # parenthesised group (or the call it formed) evaluates to.
    tree: object | None = field(default=None, hash=False, compare=False, repr=False)

    def __repr__(self) -> str:
        return f"Token({self.type}, {repr(self.value)})"
