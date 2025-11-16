from __future__ import annotations

try:
    from PySide6.QtGui import (
        QColor,
        QTextCharFormat,
        QSyntaxHighlighter,
        QFont,
    )
except ImportError:
    from PyQt5.QtGui import (
        QColor,
        QTextCharFormat,
        QSyntaxHighlighter,
        QFont,
    )

from gulfofmexico.processor.lexer import tokenize


class GomHighlighter(QSyntaxHighlighter):
    """Syntax highlighter using the production tokenizer.

    This performs whole-document tokenization on rehighlight. It's simple but
    effective for medium-sized files. Future optimization could cache lines.
    """

    def __init__(self, document):
        super().__init__(document)
        self._fmt_keyword = self._fmt(color="# C678DD", bold=True)
        self._fmt_name = self._fmt(color="# E5C07B")
        self._fmt_number = self._fmt(color="# D19A66")
        self._fmt_string = self._fmt(color="# 98C379")
        self._fmt_op = self._fmt(color="# 61AFEF")
        self._fmt_punct = self._fmt(color="# ABB2BF")

    def _fmt(self, *, color: str, bold: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        return fmt

    def highlightBlock(self, _: str) -> None:  # noqa: N802
        # We rely on whole-document pass in rehighlight. Here we do nothing
        # per-line; the work occurs in rehighlight() below.
        return

    def rehighlight(self) -> None:  # noqa: D401
        """Retokenize entire document and apply formats."""
        super().rehighlight()
        doc = self.document()
        code = doc.toPlainText()
        # Use a dummy filename for tokenizer
        filename = "__ide_buffer__"
        try:
            tokens = tokenize(filename, code)
        except (ValueError, TypeError, IndexError, RuntimeError):
            return

        # Build positions per token (start/end in chars)
        # Token has attributes: value, line, column; we need to map to offsets
        # We'll precompute line start offsets
        lines = code.splitlines(keepends=True)
        line_starts = []
        pos = 0
        for s in lines:
            line_starts.append(pos)
            pos += len(s)

        # Apply formats
        for tok in tokens:
            try:
                line = getattr(tok, "line", 1) - 1
                col = getattr(tok, "column", 0)
                val = getattr(tok, "value", "")
                start_base = line_starts[line] if 0 <= line < len(line_starts) else 0
                start = start_base + col
                length = len(val)
                if length <= 0:
                    continue
                # Determine format category
                fmt = self._classify(tok)
                if fmt is None:
                    continue
                block = self.document().findBlock(start)
                if not block.isValid():
                    continue
                layout = block.layout()
                if layout is None:
                    continue
                # Set format on the block range
                self.setFormat(start, length, fmt)
            except (ValueError, TypeError, IndexError, RuntimeError):
                continue

    def _classify(self, tok):
        # Heuristic classification based on token value
        v = getattr(tok, "value", "")
        if isinstance(v, str):
            if v in {
                "var",
                "const",
                "if",
                "else",
                "when",
                "after",
                "class",
                "return",
                "import",
                "export",
            }:
                return self._fmt_keyword
            if v.startswith('"') or v.startswith("'"):
                return self._fmt_string
            if v.isdigit():
                return self._fmt_number
            if v in {"+", "-", "*", "/", "^", "=", "==", ";=", "=>"}:
                return self._fmt_op
            if v in {
                "{",
                "}",
                "(",
                ")",
                "[",
                "]",
                ",",
                ":",
                ";",
                ".",
                "!",
                "?",
            }:
                return self._fmt_punct
            return self._fmt_name
        return None
