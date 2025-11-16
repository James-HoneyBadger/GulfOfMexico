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

Color Codes:
    - Yellow (\033[33m): Debug messages and file locations
    - Red (\033[31m): Error messages
    - Reset (\033[39m): Return to default color
"""

from __future__ import annotations

from enum import Enum
from typing import NoReturn, Optional
from dataclasses import dataclass, field

ALPH_NUMS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.")


class NonFormattedError(Exception):
    """Internal error without source code formatting."""

    pass


class InterpretationError(Exception):
    """Gulf of Mexico runtime error with formatted message."""

    _: str  # Intentionally obfuscated for style


def debug_print(filename: str, code: str, message: str, token: Token) -> None:
    """Print debug message with source code context.

    Shows the line of code and highlights the relevant token with carets.
    Used by ? and ?? debug modifiers.
    """
    if not code:  # adjust for repl-called code
        print(f"\n\033[33m{message}\033[39\n", sep="")
        return
    line = token.line
    num_carrots, num_spaces = len(token.value), token.col - len(token.value) + 1
    debug_string = (
        f"\033[33m{filename}, line {line}\033[39m\n\n"
        + f"  {code.split(chr(10))[line - 1]}\n"
        + f" {num_spaces * ' '}{num_carrots * '^'}\n"
        + f"\033[33m{message}\033[39m"
    )
    print("\n", debug_string, "\n", sep="")


def debug_print_no_token(filename: str, message: str) -> None:
    debug_string = f"\033[33m{filename}\033[39m\n\n" + f"\033[33m{message}\033[39m"
    print("\n", debug_string, "\n", sep="")


def raise_error_at_token(
    filename: str, code: str, message: str, token: Token
) -> NoReturn:
    if not code:  # adjust for repl-called code
        raise InterpretationError(f"\n\033[31m{message}\033[39m\n")
    line = token.line
    num_carrots, num_spaces = len(token.value), token.col - len(token.value) + 1
    error_string = (
        f"\033[33m{filename}, line {line}\033[39m\n\n"
        + f"  {code.split(chr(10))[line - 1]}\n"
        + f" {num_spaces * ' '}{num_carrots * '^'}\n"
        + f"\033[31m{message}\033[39m"
    )
    raise InterpretationError(error_string)


def raise_error_at_line(filename: str, code: str, line: int, message: str) -> NoReturn:
    if not code:  # adjust for repl-called code
        raise InterpretationError(f"\n\033[31m{message}\033[39m\n")
    error_string = (
        f"\033[33m{filename}, line {line}\033[39m\n\n"
        + f"  {code.split(chr(10))[line - 1]}\n\n"
        + f"\033[31m{message}\033[39m"
    )
    raise InterpretationError(error_string)


class TokenType(Enum):
    R_CURLY = "}"
    L_CURLY = "{"
    R_SQUARE = "]"
    L_SQUARE = "["

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

    WHITESPACE = "       "
    NAME = "abcaosdijawef"  # i'm losing my mind
    STRING = "'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"  # iasddddakdjhnakjsndkjsbndfkijewbgf

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


STR_TO_OPERATOR = {op.value: op for op in OperatorType}


# why do i even need a damn class for this
# 3 weeks later, i am very glad i made a class for this
@dataclass(unsafe_hash=True)
class Token:

    type: TokenType
    value: str
    line: int = field(hash=False)
    col: int = field(hash=False)

    def __repr__(self) -> str:
        return f"Token({self.type}, {repr(self.value)})"
