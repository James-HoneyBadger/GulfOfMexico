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

from gulfofmexico.base import Token, TokenType, is_alph_num, raise_error_at_line


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


def get_string_token(code: str, curr: int, filename: str, error_line: int) -> tuple[int, str, int]:
    """Scan a string literal using DreamBerd quote-count semantics.

    A string is opened by a run of N identical quote characters (N >= 1).
    It is closed by the next run of the same character that is at least as
    long as the opening run; the final N quotes of that run form the
    closing delimiter, and any surplus quotes belong to the string contents.
    This makes single-, triple- and quadruple-quoted strings all evaluate
    to the obvious value.

    A quote run followed by nothing is the empty string (so an empty pair
    of quotes is the empty string). Unterminated single/double-quoted
    strings are auto-closed at the end of the line (AQMI), and
    unterminated triple-quoted strings are auto-closed at end of file.

    Returns (index_of_last_string_character, string_value, newlines).
    """
    quote_char = code[curr]
    start = curr
    while curr < len(code) and code[curr] == quote_char:
        curr += 1
    open_count = curr - start

    # If an even-length quote run has no later run that could close it, the
    # run itself is an empty string (its first half opens, its second closes).
    def _has_closing_run(position: int, count: int) -> bool:
        while position < len(code):
            if code[position] == quote_char:
                end = position
                while end < len(code) and code[end] == quote_char:
                    end += 1
                if end - position >= count:
                    return True
                position = end
            else:
                position += 1
        return False

    if open_count % 2 == 0 and not _has_closing_run(curr, open_count):
        return start + open_count - 1, "", 0

    value = ""
    newlines = 0
    i = curr
    allow_multiline = open_count >= 3

    while i < len(code):
        c = code[i]
        if c == quote_char:
            j = i
            while j < len(code) and code[j] == quote_char:
                j += 1
            run = j - i
            if run >= open_count:
                # The last open_count quotes close the string; any extra
                # quotes are part of the contents.
                value += quote_char * (run - open_count)
                return j - 1, value, newlines
            value += code[i:j]
            i = j
            continue
        if c == "\\" and i + 1 < len(code):
            # Keep escape sequences intact; they are processed later.
            value += code[i : i + 2]
            i += 2
            continue
        if c == "\n" and not allow_multiline:
            break  # AQMI: close the string at the end of the line
        if c == "\n":
            newlines += 1
        value += c
        i += 1

    # Reached a line break or EOF without finding a closing run (AQMI).
    return i - 1, value, newlines


def _last_significant_token(tokens: list[Token]) -> Token | None:
    """Return the last token that is neither whitespace nor a newline."""
    for token in reversed(tokens):
        if token.type not in (TokenType.WHITESPACE, TokenType.NEWLINE):
            return token
    return None


def _needs_terminator(tokens: list[Token]) -> bool:
    """Whether AEMI should append a ! for the statement seen so far."""
    token = _last_significant_token(tokens)
    if token is None:
        return False
    return token.type not in (
        TokenType.BANG,
        TokenType.QUESTION,
        TokenType.L_CURLY,
        TokenType.R_CURLY,
    )


def tokenize(filename: str, code: str) -> list[Token]:
    code += "   "  # adding a space here so i dont have to write 10 damn checks for out of bounds
    line_count = 1
    tokens: list[Token] = []
    curr, start = 0, 0
    _bracket_depth = 0  # track { } nesting for negative indentation detection
    _paren_depth = 0
    _square_depth = 0
    while curr < len(code):
        match code[curr]:
            case "\n":
                # ABI (Automatic Bracket Insertion): expressions cannot span
                # lines, so close any parentheses/square brackets left open
                # on this line.
                while _paren_depth > 0:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.R_PAREN)
                    _paren_depth -= 1
                while _square_depth > 0:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.R_SQUARE)
                    _square_depth -= 1
                # AEMI (Automatic Exclamation Mark Insertion): every statement
                # is auto-terminated at the end of its line if the author
                # forgot the !. Only applies outside of code blocks.
                if _needs_terminator(tokens):
                    add_to_tokens(tokens, line_count, curr - start, TokenType.BANG, "!")
                add_to_tokens(tokens, line_count, curr - start, TokenType.NEWLINE)
                line_count += 1
                start = curr  # at the new line to get col number
            case "}":
                # Per DreamBerd spec: leading } on a line = negative indentation (cosmetic, skip).
                # Only cosmetic if bracket_depth == 0 (no open blocks to close) AND at line start.
                _at_line_start = (
                    not tokens
                    or tokens[-1].type == TokenType.NEWLINE
                    or (tokens[-1].type == TokenType.WHITESPACE and len(tokens) >= 2 and tokens[-2].type == TokenType.NEWLINE)
                )
                if _at_line_start and _bracket_depth == 0:
                    pass  # discard cosmetic negative-indent brace
                else:
                    _bracket_depth -= 1
                    add_to_tokens(tokens, line_count, curr - start, TokenType.R_CURLY)
            case "{":
                _bracket_depth += 1
                add_to_tokens(tokens, line_count, curr - start, TokenType.L_CURLY)
            case "[":
                _square_depth += 1
                add_to_tokens(tokens, line_count, curr - start, TokenType.L_SQUARE)
            case "]":
                _square_depth = max(0, _square_depth - 1)
                add_to_tokens(tokens, line_count, curr - start, TokenType.R_SQUARE)
            case ".":
                add_to_tokens(tokens, line_count, curr - start, TokenType.DOT)
            case ":":
                add_to_tokens(tokens, line_count, curr - start, TokenType.COLON)
                if _bracket_depth == 0 and _paren_depth == 0 and _square_depth == 0:
                    # A top-level colon starts a type annotation. Capture the
                    # whole annotation as one name token so that quotes,
                    # operators, and '=' signs inside a generic annotation
                    # (for example RegExp<...>) cannot confuse the lexer.
                    j = curr + 1
                    angle_depth = 0
                    while j < len(code):
                        ch = code[j]
                        if ch == "\n":
                            break
                        if ch == "<":
                            angle_depth += 1
                        elif ch == ">":
                            angle_depth = max(0, angle_depth - 1)
                        elif ch == "=" and angle_depth == 0:
                            break
                        j += 1
                    annotation = code[curr + 1 : j].strip()
                    if annotation:
                        add_to_tokens(tokens, line_count, curr - start, TokenType.NAME, annotation)
                    curr = j - 1
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
                elif code[curr + 1] == "=":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.COMPOUND_ASSIGN, "+=")
                    curr += 1
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.ADD)
            case "-":
                if code[curr + 1] == "-":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.DECREMENT)
                    curr += 1
                elif code[curr + 1] == "=":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.COMPOUND_ASSIGN, "-=")
                    curr += 1
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.SUBTRACT)
            case "*":
                if code[curr + 1] == "=":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.COMPOUND_ASSIGN, "*=")
                    curr += 1
                else:
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
                elif code[curr + 1] == "=":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.COMPOUND_ASSIGN, "/=")
                    curr += 1
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.DIVIDE)
            case "^":
                if code[curr + 1] == "=":
                    add_to_tokens(tokens, line_count, curr - start, TokenType.COMPOUND_ASSIGN, "^=")
                    curr += 1
                else:
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
            case "¡":
                # Inverted exclamation mark — negative priority per spec
                value = "¡"
                while curr + 1 < len(code) and code[curr + 1] == "¡":
                    value += "¡"
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
            case "~":
                # Tilde-equality operators: ~=, ~==, ~===
                value = "~"
                if code[curr + 1] == "=":
                    value += "="
                    curr += 1
                    while code[curr + 1] == "=":
                        value += "="
                        curr += 1
                    add_to_tokens(tokens, line_count, curr - start, TokenType.EQUAL, value)
                else:
                    add_to_tokens(tokens, line_count, curr - start, TokenType.NAME, value)
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
            case "(":
                if curr + 1 < len(code) and code[curr + 1] == ")":
                    # The empty value () is represented as a blank name.
                    add_to_tokens(tokens, line_count, curr - start, TokenType.WHITESPACE, "")
                    add_to_tokens(tokens, line_count, curr - start, TokenType.NAME, "")
                    add_to_tokens(tokens, line_count, curr - start, TokenType.WHITESPACE, "")
                    curr += 1
                else:
                    _paren_depth += 1
                    add_to_tokens(tokens, line_count, curr - start, TokenType.L_PAREN)
            case ")":
                _paren_depth = max(0, _paren_depth - 1)
                add_to_tokens(tokens, line_count, curr - start, TokenType.R_PAREN)
            case " " | "\t":
                value = get_effective_whitespace_value(code[curr])
                while curr + 1 < len(code) and code[curr + 1] in " \t":
                    value += get_effective_whitespace_value(code[curr + 1])
                    curr += 1
                add_to_tokens(tokens, line_count, curr - start, TokenType.WHITESPACE, value)
            case c:
                value = c
                while is_alph_num(code[curr + 1]):
                    curr += 1
                    value += code[curr]
                add_to_tokens(tokens, line_count, curr - start, TokenType.NAME, value)
        curr += 1

    # Keep trailing whitespace/newlines aside so ABI/AEMI insertions end up
    # inside the final statement rather than after its line break.
    trailing: list[Token] = []
    while tokens and tokens[-1].type in (TokenType.NEWLINE, TokenType.WHITESPACE):
        trailing.insert(0, tokens.pop())

    # ABI (Automatic Bracket Insertion): close any brackets left open.
    while _paren_depth > 0:
        add_to_tokens(tokens, line_count, curr - start, TokenType.R_PAREN)
        _paren_depth -= 1
    while _square_depth > 0:
        add_to_tokens(tokens, line_count, curr - start, TokenType.R_SQUARE)
        _square_depth -= 1
    while _bracket_depth > 0:
        add_to_tokens(tokens, line_count, curr - start, TokenType.R_CURLY)
        _bracket_depth -= 1

    # AEMI at end of file.
    if _needs_terminator(tokens):
        add_to_tokens(tokens, line_count, curr - start, TokenType.BANG, "!")

    tokens.extend(trailing)
    return tokens
