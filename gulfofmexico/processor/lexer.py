"""
Lexical Analyzer (Tokenizer) for Gulf of Mexico

Converts source code into tokens for parsing. Implements Gulf of Mexico's unique
string quoting system where matching quote counts determine string boundaries.

Key Features:
    - Flexible quoting: "" or '"' both create strings
    - Quote count matching: equal counts on both sides define string boundaries
    - Single-line comments with //
    - Whitespace preservation for indentation enforcement
    - Special empty value () tokenized as blank name

Token Types Generated:
    - Names (variables/keywords): alphanumeric sequences
    - Strings: quoted sequences with count matching
    - Numbers: handled during parsing, not lexing
    - Operators: +, -, *, /, ^, ==, ===, ====, etc.
    - Delimiters: {}, [], (), :, ;, |, &

Inspired by: https://craftinginterpreters.com/scanning.html
"""  # noqa: PLW0120

from __future__ import annotations

from typing import Optional

from gulfofmexico.base import ALPH_NUMS, Token, TokenType, raise_error_at_line


def add_to_tokens(
    token_list: list[Token],
    line: int,
    col: int,
    token: TokenType,
    value: Optional[str] = None,
):
    token_list.append(Token(token, value if value is not None else token.value, line, col))


def get_effective_whitespace_value(char: str) -> str:
    match char:
        case " " | "(":
            return " "
        case "\t":
            return char
    return ""


def get_quote_count(quote_value: str) -> int:
    return sum(2 if c == '"' else 1 for c in quote_value)


def process_escape_sequences(value: str) -> str:
    """Process escape sequences in string values."""
    result = ""
    i = 0
    while i < len(value):
        if value[i] == "\\" and i + 1 < len(value):
            next_char = value[i + 1]
            if next_char == "n":
                result += "\n"
                i += 2
            elif next_char == "t":
                result += "\t"
                i += 2
            elif next_char == "r":
                result += "\r"
                i += 2
            elif next_char == "\\":
                result += "\\"
                i += 2
            elif next_char == '"':
                result += '"'
                i += 2
            elif next_char == "'":
                result += "'"
                i += 2
            elif next_char == "0":
                result += "\0"
                i += 2
            elif next_char == "b":
                result += "\b"
                i += 2
            elif next_char == "f":
                result += "\f"
                i += 2
            elif next_char == "v":
                result += "\v"
                i += 2
            else:
                # Unknown escape, keep the backslash
                result += value[i]
                i += 1
        else:
            result += value[i]
            i += 1
    return result


def is_matching_pair(quote_value: str) -> bool:
    """
    Finds a pair of quote groups that have the same count of quotes.
    Returns an integer index where the second group begins if found, else -1.
    """
    total_sum = get_quote_count(quote_value)
    if total_sum % 2:
        return False
    for i in range(len(quote_value)):
        if get_quote_count(quote_value[:i]) == total_sum // 2:
            return True
    return False


def get_string_token(code: str, curr: int, filename: str, error_line: int) -> tuple[int, str, int]:
    """
    Scans the code for the shortest possible string and returns it.
    Returns as soon as a pair of quote groups is found that is equal in terms of quote count on both sides.
    For example, "" (space) "" reads the two first double quotes, detects that there is a pair, and returns the empty string.
    To have more sequences of quotes, one can do the following:
        '""hello world"'"  <-- this is interpreted as the string "hello world"
    Therefore, to avoid premature returns of quotes, simply preface your quotes with a single ' and the rest "
    This guarantees that no pair of quotes will be found in the starting quote because it will have an odd number of quotes.
    
    Also handles multi-line strings with triple quotes.
    Returns (end_position, string_value, newlines_encountered)
    """

    quote_value = ""
    while code[curr] in """"'""":  # lmaoo
        quote_value += code[curr]
        if is_matching_pair(quote_value):
            return curr, "", 0
        curr += 1
    
    # Check for triple quotes (multi-line strings)
    is_triple_quote = len(quote_value) >= 3 and (quote_value.startswith('"' * 3) or quote_value.startswith("'" * 3))
    
    quote_count = get_quote_count(quote_value)
    newlines = 0

    value = ""
    while curr < len(code):
        if is_triple_quote:
            # For triple-quoted strings, look for matching triple quotes
            if (code[curr:curr+3] == quote_value[0]*3):
                return curr + 2, value, newlines
            if code[curr] == "\n":
                newlines += 1
                value += code[curr]
                curr += 1
            else:
                value += code[curr]
                curr += 1
        else:
            # Original logic for regular strings
            running_count, quote_start = 0, curr
            while code[curr] in """"'""":
                running_count += 2 if code[curr] == '"' else 1
                if running_count == quote_count:
                    return curr, value, newlines
                curr += 1
            value += code[quote_start : curr + 1]
            if code[quote_start] == "\n":
                newlines += 1
            curr += 1
    else:  # type: ignore
        raise_error_at_line(
            filename,
            code,
            error_line,
            "Invalid string. Starting quotes do not match opening quotes.",
        )


def tokenize(filename: str, code: str) -> list[Token]:
    code += "   "  # adding a space here so i dont have to write 10 damn checks for out of bounds
    line_count = 1
    tokens: list[Token] = []
    curr, start = 0, 0
    while curr < len(code):
        match code[curr]:
            case "\n":
                line_count += 1
                start = curr  # at the new line to get col number
                add_to_tokens(tokens, line_count, curr - start, TokenType.NEWLINE)
            case "}":
                add_to_tokens(tokens, line_count, curr - start, TokenType.R_CURLY)
            case "{":
                add_to_tokens(tokens, line_count, curr - start, TokenType.L_CURLY)
            case "[":
                add_to_tokens(tokens, line_count, curr - start, TokenType.L_SQUARE)
            case "]":
                add_to_tokens(tokens, line_count, curr - start, TokenType.R_SQUARE)
            case ".":
                add_to_tokens(tokens, line_count, curr - start, TokenType.DOT)
            case ":":
                add_to_tokens(tokens, line_count, curr - start, TokenType.COLON)
            case "|":
                add_to_tokens(tokens, line_count, curr - start, TokenType.PIPE)
            case "&":
                add_to_tokens(tokens, line_count, curr - start, TokenType.AND)
            case ";":
                value = ";"
                while code[curr + 1] == "=":
                    value += "="
                    curr += 1
                if len(value) == 1:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.SEMICOLON)
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.NOT_EQUAL, value)
            case ",":
                add_to_tokens(tokens, line_count, curr - start, TokenType.COMMA)
            case "+":
                if code[curr + 1] == "+":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.INCREMENT)
                    curr += 1
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.ADD)  # YOU NEVER SAID I HAD TO DO +=
            case "-":
                if code[curr + 1] == "-":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.DECREMENT)
                    curr += 1
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.SUBTRACT)
            case "*":
                add_to_tokens(tokens, line_count, curr - start, TokenType.MULTIPLY)
            case "/":
                if code[curr + 1] == "/":
                    # Skip single-line comment until end of line
                    while curr < len(code) and code[curr] != "\n":
                        curr += 1
                    # Don't add curr += 1 at end, let next iteration handle the \n
                    continue
                elif code[curr + 1] == "*":
                    # Skip multi-line comment until */
                    curr += 2  # Skip /*
                    while curr < len(code) - 1:
                        if code[curr] == "*" and code[curr + 1] == "/":
                            curr += 2  # Skip past */ (1 for *, 1 for /)
                            break
                        if code[curr] == "\n":
                            line_count += 1
                            start = curr + 1  # Set start to char after newline for correct column tracking
                        curr += 1
                    continue
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.DIVIDE)
            case "^":
                add_to_tokens(tokens, line_count, curr - start, TokenType.CARROT)
            case ">":
                if code[curr + 1] == "=":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.GREATER_EQUAL)
                    curr += 1
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.GREATER_THAN)
            case "<":
                if code[curr + 1] == "=":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.LESS_EQUAL)
                    curr += 1
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.LESS_THAN)
            case "!":
                value = "!"
                while code[curr + 1] == "!":
                    value += "!"
                    curr += 1
                add_to_tokens(tokens, line_count, curr - start, TokenType.BANG, value)
            case "?":
                value = "?"
                while code[curr + 1] == "?":
                    value += "?"
                    curr += 1
                if len(value) > 4:
                    raise_error_at_line(
                        filename,
                        code,
                        line_count,
                        "User is too confused. Aborting due to trust issues.",
                    )  # heheheheheheh
                add_to_tokens(tokens, line_count, curr - start, TokenType.QUESTION, value)
            case "=":
                value = "="
                if code[curr + 1] == ">":
                    curr += 1
                    add_to_tokens(tokens, line_count, curr - start, TokenType.FUNC_POINT)
                else:
                    while code[curr + 1] == "=":
                        value += "="
                        curr += 1
                    add_to_tokens(tokens, line_count, curr - start, TokenType.EQUAL, value)
            case '"' | "'":
                curr, value, newlines = get_string_token(code, curr, filename, line_count)
                line_count += newlines
                value = process_escape_sequences(value)
                add_to_tokens(tokens, line_count, curr - start, TokenType.STRING, value)
            case " " | "\t" | "(" | ")":
                if code[curr] == "(" and curr + 1 < len(code) and code[curr + 1] == ")":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.WHITESPACE, "")
                    add_to_tokens(tokens, line_count, curr - start, TokenType.NAME, "")  # please please please work
                    add_to_tokens(tokens, line_count, curr - start, TokenType.WHITESPACE, "")
                    curr += 1
                else:
                    value = get_effective_whitespace_value(code[curr])
                    while curr + 1 < len(code) and code[curr + 1] in " ()\t":
                        value += get_effective_whitespace_value(code[curr + 1])
                        curr += 1
                    add_to_tokens(tokens, line_count, curr - start, TokenType.WHITESPACE, value)
            case c:
                value = c
                while code[curr + 1] in ALPH_NUMS:
                    curr += 1
                    value += code[curr]
                add_to_tokens(tokens, line_count, curr - start, TokenType.NAME, value)
        curr += 1
    return tokens
