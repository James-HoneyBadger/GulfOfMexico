"""
Syntax highlighter for the Gulf of Mexico IDE.

Uses the production tokenizer and classifies tokens by ``TokenType``.
Accepts a theme dict to allow live theme switching.
"""

from __future__ import annotations

from gulfofmexico.ide.qt_compat import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
)

from gulfofmexico.base import TokenType
from gulfofmexico.processor.lexer import tokenize

import re as _re

# ── Token classification sets ─────────────────────────────────────────

_KEYWORDS = {
    "class", "className", "after", "const", "var", "when", "if", "else",
    "async", "return", "delete", "await", "previous", "next", "reverse",
    "export", "import", "to", "new", "current",
}

_FUNC_KW_PATTERN = _re.compile(r"^f?u?n?c?t?i?o?n?$")

_BUILTINS = {
    "print", "read", "readfile", "write", "exit", "sleep", "use",
    "Number", "String", "Boolean", "Map",
    "abs", "floor", "ceil", "round", "sqrt", "sin", "cos", "tan",
    "log", "exp", "degrees", "radians", "pow", "min", "max",
    "random", "randomInt",
    "regex_match", "regex_findall", "regex_replace",
}

_CONSTANTS = {"true", "false", "maybe", "undefined", "noop"}

_OPERATOR_TYPES = {
    TokenType.ADD, TokenType.SUBTRACT, TokenType.MULTIPLY, TokenType.DIVIDE,
    TokenType.CARROT, TokenType.EQUAL, TokenType.FUNC_POINT,
    TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_EQUAL,
    TokenType.GREATER_EQUAL, TokenType.NOT_EQUAL, TokenType.PIPE, TokenType.AND,
    TokenType.INCREMENT, TokenType.DECREMENT, TokenType.COMPOUND_ASSIGN,
}

_PUNCT_TYPES = {
    TokenType.L_CURLY, TokenType.R_CURLY, TokenType.L_SQUARE, TokenType.R_SQUARE,
    TokenType.COMMA, TokenType.COLON, TokenType.SEMICOLON, TokenType.DOT,
}


# ── Default One Dark palette ─────────────────────────────────────────

_DEFAULT_SYNTAX = {
    "syn_keyword":  "#c678dd",
    "syn_builtin":  "#61afef",
    "syn_string":   "#98c379",
    "syn_number":   "#d19a66",
    "syn_constant": "#d19a66",
    "syn_operator": "#56b6c2",
    "syn_comment":  "#5c6370",
    "syn_bang":     "#e06c75",
    "syn_name":     "#e5c07b",
    "syn_punct":    "#abb2bf",
    "syn_func_kw":  "#c678dd",
}


class GomHighlighter(QSyntaxHighlighter):
    """Syntax highlighter with live-switchable theme colours."""

    def __init__(self, document, *, theme: dict | None = None) -> None:
        super().__init__(document)
        self._theme = theme or dict(_DEFAULT_SYNTAX)
        self._rebuild_formats()

    # ── Theme switching ───────────────────────────────────────────────

    def set_theme(self, theme: dict) -> None:
        self._theme = dict(theme)
        self._rebuild_formats()
        self.rehighlight()

    def _rebuild_formats(self) -> None:
        t = self._theme
        self._fmt_keyword   = self._mkfmt(color=t.get("syn_keyword",  "#c678dd"), bold=True)
        self._fmt_builtin   = self._mkfmt(color=t.get("syn_builtin",  "#61afef"))
        self._fmt_constant  = self._mkfmt(color=t.get("syn_constant", "#d19a66"), bold=True)
        self._fmt_func_kw   = self._mkfmt(color=t.get("syn_func_kw",  "#c678dd"), bold=True)
        self._fmt_name      = self._mkfmt(color=t.get("syn_name",     "#e5c07b"))
        self._fmt_number    = self._mkfmt(color=t.get("syn_number",   "#d19a66"))
        self._fmt_string    = self._mkfmt(color=t.get("syn_string",   "#98c379"))
        self._fmt_op        = self._mkfmt(color=t.get("syn_operator", "#56b6c2"))
        self._fmt_punct     = self._mkfmt(color=t.get("syn_punct",    "#abb2bf"))
        self._fmt_bang      = self._mkfmt(color=t.get("syn_bang",     "#e06c75"), bold=True)
        self._fmt_comment   = self._mkfmt(color=t.get("syn_comment",  "#5c6370"), italic=True)

    @staticmethod
    def _mkfmt(*, color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    # ── Per-block highlighting ────────────────────────────────────────

    def highlightBlock(self, text: str) -> None:  # noqa: N802
        """Tokenize a single block and apply syntax formats."""
        if not text.strip():
            return
        try:
            tokens = tokenize("__ide_buffer__", text)
        except Exception:
            return
        for tok in tokens:
            try:
                col = getattr(tok, "column", None) or getattr(tok, "col", 0)
                val = getattr(tok, "value", "")
                tok_type = getattr(tok, "type", None)
                length = len(val)
                if length <= 0 or col < 0:
                    continue
                fmt = self._classify(tok_type, val)
                if fmt is None:
                    continue
                self.setFormat(col, length, fmt)
            except Exception:
                continue

    def _classify(self, tt: TokenType | None, value: str) -> QTextCharFormat | None:
        if tt is None or tt in (TokenType.WHITESPACE, TokenType.NEWLINE):
            return None
        if tt == TokenType.STRING:
            return self._fmt_string
        if tt in _OPERATOR_TYPES:
            return self._fmt_op
        if tt in (TokenType.BANG, TokenType.QUESTION):
            return self._fmt_bang
        if tt in _PUNCT_TYPES:
            return self._fmt_punct
        if tt == TokenType.NAME:
            if value in _KEYWORDS:
                return self._fmt_keyword
            if value in _BUILTINS:
                return self._fmt_builtin
            if value in _CONSTANTS:
                return self._fmt_constant
            if len(value) <= 8 and value and _FUNC_KW_PATTERN.match(value):
                return self._fmt_func_kw
            try:
                float(value)
                return self._fmt_number
            except (ValueError, TypeError):
                pass
            return self._fmt_name
        return self._fmt_name
