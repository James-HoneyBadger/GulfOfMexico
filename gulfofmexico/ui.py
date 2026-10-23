"""Terminal presentation layer for the Gulf of Mexico toolchain.

Everything users see in a terminal (diagnostics, banners, tables, prompts)
is rendered here so the CLI and REPL share one visual language.

Design rules
------------
* Colour is opt-out and environment-aware. ``NO_COLOR`` always wins,
  ``FORCE_COLOR`` always forces, and otherwise colour is only emitted when the
  target stream is a TTY. Piped and CI output therefore stays plain text.
* Diagnostics follow a stable, compiler-style layout::

      error: '<message>'
        --> file.gom:2:3
         |
       2 | class Zed {
         | ^^^^^
         = hint: <optional suggestion>

* Nothing in this module imports the interpreter, so it can be used by the
  lexer, the CLI, and the REPL without circular-import risk.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import TextIO

__all__ = [
    "VERSION",
    "ColorPolicy",
    "Diagnostic",
    "banner",
    "bullet_list",
    "color_enabled",
    "heading",
    "hint",
    "kv_block",
    "label",
    "paint",
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    "render_diagnostic",
    "rule",
    "table",
]

#: Single source of truth for the version. Installed metadata wins; the
#: fallback keeps source-tree runs working and must match pyproject.toml.
_FALLBACK_VERSION = "1.2.0"

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _pkg_version
except ImportError:  # pragma: no cover - Python without importlib.metadata
    VERSION = _FALLBACK_VERSION
else:
    try:
        VERSION = _pkg_version("gulfofmexico")
    except PackageNotFoundError:  # pragma: no cover - running from a source tree
        VERSION = _FALLBACK_VERSION


# ---------------------------------------------------------------------------
# Colour policy
# ---------------------------------------------------------------------------

#: Semantic colour names mapped to SGR codes.
_CODES: dict[str, str] = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "grey": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_cyan": "\033[96m",
}


@dataclass(frozen=True)
class ColorPolicy:
    """How much colour to emit for a given stream."""

    enabled: bool

    @classmethod
    def detect(cls, stream: TextIO | None = None) -> ColorPolicy:
        stream = stream if stream is not None else sys.stdout
        if os.environ.get("NO_COLOR"):
            return cls(False)
        if os.environ.get("CLICOLOR", "") == "0":
            return cls(False)
        force = os.environ.get("FORCE_COLOR")
        if force and force != "0":
            return cls(True)
        if os.environ.get("TERM", "") == "dumb":
            return cls(False)
        try:
            return cls(bool(stream.isatty()))
        except (AttributeError, ValueError):  # pragma: no cover - closed streams
            return cls(False)


def color_enabled(stream: TextIO | None = None) -> bool:
    """Whether ANSI colour should be written to *stream*."""
    return ColorPolicy.detect(stream).enabled


def paint(text: str, *styles: str, stream: TextIO | None = None) -> str:
    """Wrap *text* in the requested SGR *styles* when colour is enabled."""
    if not styles or not text:
        return text
    if not color_enabled(stream):
        return text
    prefix = "".join(_CODES[s] for s in styles if s in _CODES)
    if not prefix:
        return text
    return f"{prefix}{text}{_CODES['reset']}"


def label(kind: str, stream: TextIO | None = None) -> str:
    """Return a coloured semantic label such as ``error`` or ``warning``."""
    styles = {
        "error": ("bold", "bright_red"),
        "warning": ("bold", "bright_yellow"),
        "info": ("bold", "bright_blue"),
        "success": ("bold", "bright_green"),
        "hint": ("bold", "bright_cyan"),
    }.get(kind, ("bold",))
    return paint(kind, *styles, stream=stream)


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def _emit(message: str, stream: TextIO) -> None:
    print(message, file=stream)
    try:
        stream.flush()
    except (AttributeError, ValueError):  # pragma: no cover
        pass


def print_error(message: str, *, hint: str | None = None,
                stream: TextIO | None = None) -> None:
    """Print ``error: <message>`` (plus an optional hint) to stderr."""
    stream = stream if stream is not None else sys.stderr
    _emit(f"{label('error', stream)}: {message}", stream)
    if hint:
        _emit(f"  {paint('= hint:', 'bright_cyan', stream=stream)} {hint}", stream)


def print_warning(message: str, *, hint: str | None = None,
                  stream: TextIO | None = None) -> None:
    stream = stream if stream is not None else sys.stderr
    _emit(f"{label('warning', stream)}: {message}", stream)
    if hint:
        _emit(f"  {paint('= hint:', 'bright_cyan', stream=stream)} {hint}", stream)


def print_info(message: str, *, stream: TextIO | None = None) -> None:
    stream = stream if stream is not None else sys.stdout
    _emit(f"{label('info', stream)}: {message}", stream)


def print_success(message: str, *, stream: TextIO | None = None) -> None:
    stream = stream if stream is not None else sys.stdout
    _emit(f"{label('success', stream)}: {message}", stream)


def hint(message: str, *, stream: TextIO | None = None) -> str:
    """Format a standalone hint line."""
    return f"{paint('= hint:', 'bright_cyan', stream=stream)} {message}"


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Diagnostic:
    """A diagnosable problem anchored to a source location."""

    message: str
    filename: str = ""
    line: int | None = None
    column: int | None = None
    length: int = 1
    kind: str = "error"
    hint: str | None = None
    source_line: str | None = None


def render_diagnostic(diag: Diagnostic, *, stream: TextIO | None = None) -> str:
    """Render *diag* in the compiler-style layout used across the toolchain.

    ```text
    error: 'class' has been deleted.
     --> demo.gom:2:3
      |
    2 | class Zed {
      | ^^^^^
      = hint: remove the delete statement or use another keyword
    ```
    """
    stream = stream if stream is not None else sys.stderr
    bar = paint("|", "grey", stream=stream)
    arrow = paint("-->", "grey", stream=stream)
    number = str(diag.line) if diag.line is not None else ""
    pad = " " * len(number)

    lines = [f"{label(diag.kind, stream)}: {paint(diag.message, 'bold', stream=stream)}"]

    if diag.line is not None or diag.filename:
        where = diag.filename or "<input>"
        if diag.line is not None:
            where += f":{diag.line}"
            if diag.column is not None:
                where += f":{diag.column}"
        lines.append(f"{pad} {arrow} {paint(where, 'cyan', stream=stream)}")

    if diag.source_line is not None:
        lines.append(f"{pad} {bar}")
        if diag.line is not None:
            lines.append(f"{paint(number, 'grey', stream=stream)} {bar} {diag.source_line}")
            if diag.column is not None and diag.column > 0:
                caret = " " * (diag.column - 1) + "^" * max(1, diag.length)
                lines.append(f"{pad} {bar} {paint(caret, 'bright_red', stream=stream)}")
        else:
            lines.append(f"{pad} {bar} {diag.source_line}")

    if diag.hint:
        lines.append(f"{pad} {paint('=', 'grey', stream=stream)} "
                     f"{paint('hint:', 'bright_cyan', stream=stream)} {diag.hint}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Structure: rules, headings, tables, banners
# ---------------------------------------------------------------------------

def rule(width: int = 72, char: str = "─", *, stream: TextIO | None = None) -> str:
    return paint(char * width, "grey", stream=stream)


def heading(text: str, *, subtitle: str | None = None,
            width: int = 72, stream: TextIO | None = None) -> str:
    """A section heading with an underline rule and optional subtitle."""
    out = [paint(text, "bold", "bright_blue", stream=stream)]
    if subtitle:
        out.append(paint(subtitle, "dim", stream=stream))
    out.append(rule(width, stream=stream))
    return "\n".join(out)


def kv_block(pairs: Iterable[tuple[str, str]], *, indent: int = 2,
             key_width: int | None = None,
             stream: TextIO | None = None) -> str:
    """Render aligned ``key   value`` lines."""
    items = [(str(k), str(v)) for k, v in pairs]
    if not items:
        return ""
    width = key_width or max(len(k) for k, _ in items)
    pad = " " * indent
    return "\n".join(
        f"{pad}{paint(k.ljust(width), 'bold', stream=stream)}  {v}"
        for k, v in items
    )


def table(
    rows: Sequence[Sequence[str]],
    *,
    header: Sequence[str] | None = None,
    aligns: Sequence[str] | None = None,
    indent: int = 0,
    stream: TextIO | None = None,
) -> str:
    """Render a compact left-aligned text table with a header rule."""
    body = [list(map(str, row)) for row in rows]
    head = [str(cell) for cell in header] if header else None
    columns = max([len(head or [])] + [len(r) for r in body] + [1])
    widths = [0] * columns
    for row in ([head] if head else []) + body:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], _visible_len_trim(cell))
    aligns = aligns or ["l"] * columns
    pad = " " * indent

    def _fmt(row: Sequence[str], *, is_header: bool) -> str:
        cells: list[str] = []
        for i in range(columns):
            raw = row[i] if i < len(row) else ""
            extra = widths[i] - _visible_len_trim(raw)
            align = aligns[i] if i < len(aligns) else "l"
            if align == "r":
                cell = raw.rjust(len(raw) + extra)
            else:
                cell = raw.ljust(len(raw) + extra)
            if is_header:
                cell = paint(cell, "bold", stream=stream)
            cells.append(cell)
        return pad + "  ".join(cells).rstrip()

    out: list[str] = []
    if head:
        out.append(_fmt(head, is_header=True))
        total = sum(widths) + 2 * (columns - 1)
        out.append(pad + rule(total, stream=stream))
    out.extend(_fmt(row, is_header=False) for row in body)
    return "\n".join(out)


def _visible_len_trim(text: str) -> int:
    """Length of *text* ignoring ANSI escapes."""
    length = 0
    i = 0
    while i < len(text):
        if text[i] == "\033":
            while i < len(text) and text[i] != "m":
                i += 1
            i += 1
            continue
        length += 1
        i += 1
    return length


def bullet_list(items: Iterable[str], *, indent: int = 2,
                stream: TextIO | None = None) -> str:
    pad = " " * indent
    dot = paint("•", "grey", stream=stream)
    return "\n".join(f"{pad}{dot} {item}" for item in items)


def banner(*, width: int = 72, stream: TextIO | None = None) -> str:
    """The product banner shared by the REPL and ``--version`` output."""
    title = paint("Gulf of Mexico", "bold", "bright_cyan", stream=stream)
    version = paint(f"v{VERSION}", "dim", stream=stream)
    tagline = paint(
        "an esoteric language where arrays start at -1", "dim", stream=stream
    )
    return "\n".join(
        [
            rule(width, "━", stream=stream),
            f"{title}  {version}",
            tagline,
            rule(width, "━", stream=stream),
        ]
    )
