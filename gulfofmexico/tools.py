"""
Static Tooling for Gulf of Mexico Sources

Two helpers power ``gom --check`` and ``gom --fmt``:

``check_source``   parses a program (and compiles every statement's expression
                   tree) without executing it.
``format_source``  rewrites a program in a canonical layout.

The formatter is deliberately conservative, because Gulf of Mexico is
whitespace-sensitive in two different ways:

* indentation selects blocks, and must be a multiple of three spaces;
* the spacing *within* a line breaks operator-precedence ties, so it is never
  touched.

Formatting therefore only changes leading indentation, trailing whitespace,
runs of blank lines and the final newline, and it leaves any line that sits
inside a multi-line (triple-quoted) string exactly as written. Indentation is
re-mapped rather than snapped: distinct levels keep their relative order and
become 0, 3, 6, ... spaces, which preserves block structure even for source
that currently uses non-standard widths.
"""

from __future__ import annotations

import re

from gulfofmexico.base import InterpretationError, TokenType
from gulfofmexico.interpreter.helpers import statement_expression, statement_indexes
from gulfofmexico.processor.lexer import tokenize
from gulfofmexico.processor.syntax_tree import generate_syntax_tree
from gulfofmexico.sections import split_sections

__all__ = ["INDENT_UNIT", "check_source", "format_source", "parse_source"]

INDENT_UNIT = 3


class _SourceView:
    """Minimal stand-in for an interpreter context.

    Compiling an expression tree only reads ``filename`` and ``code``, so the
    checker does not need a full :class:`~gulfofmexico.interpreter.InterpreterContext`.
    """

    __slots__ = ("filename", "code")

    def __init__(self, filename: str, code: str) -> None:
        self.filename = filename
        self.code = code


def parse_source(filename: str, code: str):
    """Tokenize and parse *code*, returning the list of statements."""
    return generate_syntax_tree(filename, tokenize(filename, code), code)


def check_source(filename: str, code: str) -> int:
    """Validate *filename*/*code* without running it.

    Files split into ``===== name =====`` sections are checked section by
    section, exactly as :func:`gulfofmexico.run_file` would run them.

    Parsing is lazy for expressions -- the interpreter compiles a statement's
    expression tree the first time that statement runs -- so checking also
    compiles every alternative interpretation of every statement. Errors that
    would otherwise only surface mid-run are reported up front.

    Returns the number of top-level statements and raises
    :class:`~gulfofmexico.base.InterpretationError` on the first real problem.
    """
    total = 0
    for section_name, section_code in split_sections(code):
        name = f"{filename}:{section_name}" if section_name else filename
        statements = parse_source(name, section_code)
        _check_statements(statements, _SourceView(name, section_code))
        total += len(statements)
    return total


def _check_statements(statements, view: _SourceView) -> None:
    for alternatives in statements:
        failure: InterpretationError | None = None
        for statement in alternatives:
            try:
                statement_expression(statement, view)
                statement_indexes(statement, view)
                nested = getattr(statement, "code", None)
                if isinstance(nested, list):
                    _check_statements(nested, view)
            except InterpretationError as exc:
                if failure is None:
                    failure = exc
                continue
            except Exception:  # noqa: BLE001 - an interpretation that was not chosen
                # Alternative interpretations share the same tokens and are only
                # valid for some of them; anything else means "not this one".
                continue
            failure = None
            break
        if failure is not None:
            raise failure


def _split_indent(line: str) -> tuple[int, str]:
    """Split *line* into ``(indent_width, rest)``, counting a tab as one indent."""
    width = 0
    index = 0
    while index < len(line) and line[index] in " \t":
        width += INDENT_UNIT if line[index] == "\t" else 1
        index += 1
    return width, line[index:]


def _string_lines(filename: str, code: str) -> tuple[set[int], set[int]]:
    """Locate the lines touched by multi-line string literals.

    Returns ``(verbatim, starts)``. ``verbatim`` holds the lines that live
    wholly inside a string and must not be touched at all; ``starts`` holds the
    lines where a string opens, which may be re-indented but must keep their
    trailing characters.
    """
    verbatim: set[int] = set()
    starts: set[int] = set()
    try:
        tokens = tokenize(filename, code)
    except Exception:  # noqa: BLE001 - unparsable input still formats as text
        return verbatim, starts
    for token in tokens:
        if token.type is not TokenType.STRING or not token.value or "\n" not in token.value:
            continue
        # A token records the line it ends on, so walk back over its newlines.
        span = token.value.count("\n")
        end = token.line or 1
        start = end - span
        starts.add(start)
        verbatim.update(range(start + 1, end + 1))
    return verbatim, starts


def format_source(filename: str, code: str) -> str:
    """Return *code* in canonical layout.

    Idempotent: formatting an already-formatted program returns it unchanged.
    """
    text = re.sub(r"\r\n?", "\n", code)
    verbatim, starts = _string_lines(filename, text)
    lines = text.split("\n")

    widths = {
        _split_indent(line)[0]
        for index, line in enumerate(lines, start=1)
        if index not in verbatim and line.strip()
    }
    levels = {width: rank * INDENT_UNIT for rank, width in enumerate(sorted(widths))}

    formatted: list[str] = []
    previous_blank = True
    for index, line in enumerate(lines, start=1):
        if index in verbatim:
            formatted.append(line)
            previous_blank = False
            continue
        if not line.strip():
            if previous_blank:
                continue
            formatted.append("")
            previous_blank = True
            continue
        width, rest = _split_indent(line)
        content = rest if index in starts else rest.rstrip()
        formatted.append(" " * levels[width] + content)
        previous_blank = False

    while formatted and not formatted[-1]:
        formatted.pop()
    return "\n".join(formatted) + "\n" if formatted else ""
