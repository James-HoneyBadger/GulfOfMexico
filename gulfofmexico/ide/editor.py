"""
Code Editor widget for the Gulf of Mexico IDE.

Features:
    - Line number gutter with breakpoint support (click to toggle)
    - 3-space tab width matching GOM indentation spec
    - Auto-indent on Enter (extra indent after '{')
    - Current line highlighting
    - Matching bracket highlighting
    - Toggle comment (Ctrl+/)
    - Drag-and-drop .gom file opening
    - Font zoom (Ctrl+= / Ctrl+-)
    - Indent guide rendering
    - Configurable font / theme colors
"""

from __future__ import annotations

from gulfofmexico.ide.qt_compat import (
    QColor,
    QFont,
    QPainter,
    QPlainTextEdit,
    QRect,
    QSize,
    Qt,
    QTextEdit,
    QTextFormat,
    QTextOption,
    QWidget,
)


# ── Defaults ──────────────────────────────────────────────────────────────

GOM_INDENT = "   "  # 3 spaces per spec

_DEFAULT_THEME = {
    "bg":            "#282c34",
    "fg":            "#abb2bf",
    "selection":     "#3e4451",
    "gutter_bg":     "#282c34",
    "gutter_fg":     "#636d83",
    "gutter_active": "#abb2bf",
    "line_highlight": "#2c313a",
    "error":         "#e06c75",
    "accent":        "#61afef",
    "border":        "#181a1f",
    "indent_guide":  "#3e4451",
    "bracket_match": "#61afef",
}


def _monospace_font(family: str = "", size: int = 12) -> QFont:
    """Return a monospace font, falling back through known families."""
    candidates = [family] if family else []
    candidates += [
        "JetBrains Mono", "Fira Code", "Cascadia Code",
        "Consolas", "Source Code Pro", "monospace",
    ]
    for name in candidates:
        if not name:
            continue
        f = QFont(name, size)
        if f.exactMatch() or name == "monospace":
            return f
    return QFont("monospace", size)


# ── Line-number gutter ────────────────────────────────────────────────────

class LineNumberArea(QWidget):
    """Gutter widget: line numbers + breakpoint dots + fold margin."""

    BREAKPOINT_MARGIN = 18

    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):  # noqa: N802
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):  # noqa: N802
        self.editor.line_number_area_paint_event(event)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            block = self.editor.firstVisibleBlock()
            top = int(
                self.editor.blockBoundingGeometry(block)
                .translated(self.editor.contentOffset())
                .top()
            )
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            while block.isValid() and top <= event.pos().y():
                if block.isVisible() and bottom >= event.pos().y():
                    self.editor.toggle_breakpoint(block.blockNumber() + 1)
                    self.update()
                    return
                block = block.next()
                top = bottom
                bottom = top + int(self.editor.blockBoundingRect(block).height())
        super().mousePressEvent(event)


# ── Code editor ───────────────────────────────────────────────────────────

class CodeEditor(QPlainTextEdit):
    """Full-featured code editor with GOM-specific behaviour."""

    def __init__(self, parent=None, *, theme: dict | None = None,
                 font_family: str = "", font_size: int = 12,
                 show_indent_guides: bool = True,
                 bracket_matching: bool = True,
                 word_wrap: bool = False,
                 show_line_numbers: bool = True) -> None:
        super().__init__(parent)

        # Settings
        self._theme = theme or dict(_DEFAULT_THEME)
        self._show_indent_guides = show_indent_guides
        self._bracket_matching = bracket_matching
        self._show_line_numbers = show_line_numbers

        # Font
        self._font_size = font_size
        self._font_family = font_family
        self._apply_font()

        # Theme
        self._apply_theme()

        # Word wrap
        self._word_wrap = word_wrap
        self._apply_word_wrap()

        # Breakpoints
        self._breakpoints: set[int] = set()

        # Line number area
        self._line_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self._on_cursor_changed)
        self.update_line_number_area_width(0)
        self._highlight_current_line()

        self.setAcceptDrops(True)

    # ── Public configuration ──────────────────────────────────────────

    def apply_settings(self, *, theme: dict | None = None,
                       font_family: str | None = None,
                       font_size: int | None = None,
                       show_indent_guides: bool | None = None,
                       bracket_matching: bool | None = None,
                       word_wrap: bool | None = None,
                       show_line_numbers: bool | None = None) -> None:
        if theme is not None:
            self._theme = dict(theme)
            self._apply_theme()
        if font_family is not None:
            self._font_family = font_family
        if font_size is not None:
            self._font_size = font_size
        if font_family is not None or font_size is not None:
            self._apply_font()
        if show_indent_guides is not None:
            self._show_indent_guides = show_indent_guides
        if bracket_matching is not None:
            self._bracket_matching = bracket_matching
        if word_wrap is not None:
            self._word_wrap = word_wrap
            self._apply_word_wrap()
        if show_line_numbers is not None:
            self._show_line_numbers = show_line_numbers
            self.update_line_number_area_width(0)
            self._line_area.setVisible(show_line_numbers)
        self._line_area.update()
        self._on_cursor_changed()

    def _apply_word_wrap(self) -> None:
        mode = QTextOption.WrapMode.WordWrap if self._word_wrap else QTextOption.WrapMode.NoWrap
        self.setWordWrapMode(mode)

    # ── Breakpoints ───────────────────────────────────────────────────

    @property
    def breakpoints(self) -> set[int]:
        return self._breakpoints

    def toggle_breakpoint(self, line: int) -> None:
        self._breakpoints.symmetric_difference_update({line})
        self._line_area.update()

    def clear_breakpoints(self) -> None:
        self._breakpoints.clear()
        self._line_area.update()

    # ── Line number area ──────────────────────────────────────────────

    def line_number_area_width(self) -> int:
        if not self._show_line_numbers:
            return 0
        digits = max(1, len(str(max(1, self.blockCount()))))
        dw = self.fontMetrics().horizontalAdvance("9") * digits
        return LineNumberArea.BREAKPOINT_MARGIN + 8 + dw + 8

    def update_line_number_area_width(self, _=0) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy) -> None:
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event) -> None:
        t = self._theme
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), QColor(t["gutter_bg"]))

        # Separator line on the right edge of the gutter
        sep_x = self._line_area.width() - 1
        painter.setPen(QColor(t.get("border", "#181a1f")))
        painter.drawLine(sep_x, event.rect().top(), sep_x, event.rect().bottom())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())
        current_block = self.textCursor().blockNumber()
        line_h = self.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = block_number + 1

                # ─ Breakpoint dot ─
                if line_num in self._breakpoints:
                    painter.setBrush(QColor(t["error"]))
                    painter.setPen(Qt.PenStyle.NoPen)
                    ds = 10
                    dx = (LineNumberArea.BREAKPOINT_MARGIN - ds) // 2
                    dy = top + (line_h - ds) // 2
                    painter.drawEllipse(dx, dy, ds, ds)

                # ─ Line number ─
                is_current = block_number == current_block
                color = t["gutter_active"] if is_current else t["gutter_fg"]
                painter.setPen(QColor(color))
                font = painter.font()
                font.setBold(is_current)
                painter.setFont(font)
                num_x = LineNumberArea.BREAKPOINT_MARGIN + 4
                num_w = self._line_area.width() - num_x - 8
                painter.drawText(
                    num_x, top, num_w, line_h,
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    str(line_num),
                )
                font.setBold(False)
                painter.setFont(font)

                # ─ Indent guides ─
                if self._show_indent_guides:
                    text = block.text()
                    indent_level = len(text) - len(text.lstrip(" "))
                    guide_color = QColor(t.get("indent_guide", "#3e4451"))
                    guide_color.setAlpha(80)
                    painter.setPen(guide_color)
                    char_w = self.fontMetrics().horizontalAdvance(" ")
                    gutter_w = self._line_area.width()
                    for g in range(3, indent_level + 1, 3):
                        gx = gutter_w + int(g * char_w) - self.horizontalScrollBar().value()
                        # Only render if it would be in the viewport
                        if gx > gutter_w:
                            pass  # guides render in paintEvent override below

            block = block.next()
            top = bottom
            if block.isValid():
                bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def paintEvent(self, event) -> None:  # noqa: N802
        """Override to draw indent guides underneath the text."""
        # Draw indent guides before the text
        if self._show_indent_guides:
            painter = QPainter(self.viewport())
            guide_color = QColor(self._theme.get("indent_guide", "#3e4451"))
            guide_color.setAlpha(60)
            painter.setPen(guide_color)
            char_w = self.fontMetrics().horizontalAdvance(" ")

            block = self.firstVisibleBlock()
            top = int(
                self.blockBoundingGeometry(block)
                .translated(self.contentOffset())
                .top()
            )
            bottom = top + int(self.blockBoundingRect(block).height())

            while block.isValid() and top <= event.rect().bottom():
                if block.isVisible() and bottom >= event.rect().top():
                    text = block.text()
                    indent_level = len(text) - len(text.lstrip(" "))
                    for g in range(3, indent_level + 1, 3):
                        gx = int(g * char_w) + self.contentOffset().x()
                        painter.drawLine(int(gx), top, int(gx), bottom)
                block = block.next()
                top = bottom
                if block.isValid():
                    bottom = top + int(self.blockBoundingRect(block).height())

            painter.end()
        super().paintEvent(event)

    # ── Cursor change → highlight current line + bracket matching ─────

    def _on_cursor_changed(self) -> None:
        self._highlight_current_line()

    def _highlight_current_line(self) -> None:
        extra: list = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor(self._theme["line_highlight"]))
            sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)

            # Bracket matching
            if self._bracket_matching:
                extra.extend(self._bracket_match_selections())

        self.setExtraSelections(extra)

    def _bracket_match_selections(self) -> list:
        """Find and highlight matching bracket pair."""
        _OPEN = "({["
        _CLOSE = ")}]"
        _PAIRS = dict(zip(_OPEN, _CLOSE))
        _RPAIRS = dict(zip(_CLOSE, _OPEN))
        sels = []

        cursor = self.textCursor()
        doc = self.document()
        pos = cursor.position()
        text = doc.toPlainText()
        if not text:
            return sels

        def _char_at(p: int) -> str:
            return text[p] if 0 <= p < len(text) else ""

        ch = _char_at(pos)
        ch_before = _char_at(pos - 1)

        match_pos = -1
        if ch and ch in _OPEN:
            # Search forward for matching close
            target = _PAIRS[ch]
            depth = 0
            for i in range(pos, len(text)):
                c = text[i]
                if c == ch:
                    depth += 1
                elif c == target:
                    depth -= 1
                    if depth == 0:
                        match_pos = i
                        break
            if match_pos >= 0:
                sels.extend(self._make_bracket_sels(pos, match_pos))
        elif ch_before and ch_before in _CLOSE:
            target = _RPAIRS[ch_before]
            depth = 0
            for i in range(pos - 1, -1, -1):
                c = text[i]
                if c == ch_before:
                    depth += 1
                elif c == target:
                    depth -= 1
                    if depth == 0:
                        match_pos = i
                        break
            if match_pos >= 0:
                sels.extend(self._make_bracket_sels(match_pos, pos - 1))

        return sels

    def _make_bracket_sels(self, pos_a: int, pos_b: int) -> list:
        color = QColor(self._theme.get("bracket_match", "#61afef"))
        color.setAlpha(50)
        border_color = QColor(self._theme.get("bracket_match", "#61afef"))
        sels = []
        for p in (pos_a, pos_b):
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(color)
            # QTextCharFormat doesn't support CSS directly; use underline as indicator
            sel.format.setFontUnderline(True)
            sel.format.setUnderlineColor(border_color)
            sel.format.setBackground(color)
            cursor = self.textCursor()
            cursor.setPosition(p)
            cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor)
            sel.cursor = cursor
            sels.append(sel)
        return sels

    # ── Key handling ──────────────────────────────────────────────────

    def keyPressEvent(self, event) -> None:  # noqa: N802
        key = event.key()
        mods = event.modifiers()

        # Tab → 3 spaces
        if key == Qt.Key.Key_Tab and not mods:
            self.insertPlainText(GOM_INDENT)
            return

        # Shift+Tab → dedent
        if key == Qt.Key.Key_Backtab:
            self._dedent_current_line()
            return

        # Ctrl+= / Ctrl+- : zoom; Ctrl+D : duplicate line
        if mods & Qt.KeyboardModifier.ControlModifier:
            if key in (Qt.Key.Key_Equal, Qt.Key.Key_Plus):
                self.zoom_in()
                return
            if key == Qt.Key.Key_Minus:
                self.zoom_out()
                return
            if key == Qt.Key.Key_0:
                self.zoom_reset()
                return
            if key == Qt.Key.Key_D:
                self.duplicate_line()
                return

        # Alt+Up / Alt+Down : move line
        if mods == Qt.KeyboardModifier.AltModifier:
            if key == Qt.Key.Key_Up:
                self.move_line_up()
                return
            if key == Qt.Key.Key_Down:
                self.move_line_down()
                return

        # Enter → auto-indent
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            line = cursor.block().text()
            stripped = line.lstrip(" ")
            indent = len(line) - len(stripped)
            base = " " * indent
            if stripped.rstrip().endswith("{"):
                base += GOM_INDENT
            cursor.insertText("\n" + base)
            self.setTextCursor(cursor)
            return

        # Auto-close brackets
        if not mods:
            _PAIRS = {"(": ")", "{": "}", "[": "]"}
            _CLOSE_CHARS = set(_PAIRS.values())
            ch = event.text()
            if ch in _PAIRS:
                cursor = self.textCursor()
                # If next char already is the closing bracket, just move past it
                doc = self.document()
                next_pos = cursor.position()
                next_ch = doc.characterAt(next_pos) if next_pos < doc.characterCount() else ""
                if next_ch == _PAIRS[ch]:
                    cursor.movePosition(cursor.MoveOperation.Right)
                    self.setTextCursor(cursor)
                    return
                cursor.insertText(ch + _PAIRS[ch])
                cursor.movePosition(cursor.MoveOperation.Left)
                self.setTextCursor(cursor)
                return
            # Skip over a closing bracket if the cursor is right before it and we type it
            if ch in _CLOSE_CHARS:
                cursor = self.textCursor()
                doc = self.document()
                next_pos = cursor.position()
                next_ch = doc.characterAt(next_pos) if next_pos < doc.characterCount() else ""
                if next_ch == ch:
                    cursor.movePosition(cursor.MoveOperation.Right)
                    self.setTextCursor(cursor)
                    return

        super().keyPressEvent(event)

    # ── Zoom ──────────────────────────────────────────────────────────

    def zoom_in(self, delta: int = 1) -> None:
        self._font_size = min(48, self._font_size + delta)
        self._apply_font()

    def zoom_out(self, delta: int = 1) -> None:
        self._font_size = max(6, self._font_size - delta)
        self._apply_font()

    def zoom_reset(self) -> None:
        self._font_size = 12
        self._apply_font()

    @property
    def current_font_size(self) -> int:
        return self._font_size

    # ── Dedent ────────────────────────────────────────────────────────

    def _dedent_current_line(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        line = cursor.block().text()
        if line.startswith(GOM_INDENT):
            cursor.movePosition(
                cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor,
                len(GOM_INDENT),
            )
            cursor.removeSelectedText()

    # ── Toggle comment ────────────────────────────────────────────────

    def toggle_comment(self) -> None:
        cursor = self.textCursor()
        cursor.beginEditBlock()

        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start)
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        first_block = cursor.blockNumber()

        cursor.setPosition(end)
        if cursor.atBlockStart() and cursor.blockNumber() > first_block:
            cursor.movePosition(cursor.MoveOperation.PreviousBlock)
        last_block = cursor.blockNumber()

        blocks = []
        cursor.setPosition(start)
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        for _ in range(last_block - first_block + 1):
            blocks.append(cursor.block())
            cursor.movePosition(cursor.MoveOperation.NextBlock)

        all_commented = all(
            b.text().lstrip().startswith("//") for b in blocks if b.text().strip()
        )

        cursor.setPosition(start)
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)

        for _ in range(last_block - first_block + 1):
            line = cursor.block().text()
            if all_commented:
                stripped_start = len(line) - len(line.lstrip())
                if line.lstrip().startswith("// "):
                    cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.MoveAnchor, stripped_start)
                    cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor, 3)
                    cursor.removeSelectedText()
                elif line.lstrip().startswith("//"):
                    cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.MoveAnchor, stripped_start)
                    cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor, 2)
                    cursor.removeSelectedText()
            else:
                cursor.insertText("// ")
            cursor.movePosition(cursor.MoveOperation.NextBlock)
            cursor.movePosition(cursor.MoveOperation.StartOfBlock)

        cursor.endEditBlock()

    # ── Duplicate / move line ─────────────────────────────────────────

    def duplicate_line(self) -> None:
        """Insert a copy of the current line below it."""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        cursor.movePosition(cursor.MoveOperation.EndOfBlock, cursor.MoveMode.KeepAnchor)
        line = cursor.selectedText()
        cursor.movePosition(cursor.MoveOperation.EndOfBlock)
        cursor.insertText("\n" + line)
        cursor.endEditBlock()

    def move_line_up(self) -> None:
        """Swap the current line with the one above it."""
        cursor = self.textCursor()
        block = cursor.block()
        if block.blockNumber() == 0:
            return
        col = cursor.positionInBlock()
        cursor.beginEditBlock()
        current_text = block.text()
        prev_block = block.previous()
        prev_text = prev_block.text()
        # Select current line and replace with prev text
        c = self.textCursor()
        c.setPosition(block.position())
        c.movePosition(c.MoveOperation.EndOfBlock, c.MoveMode.KeepAnchor)
        c.insertText(prev_text)
        # Select prev line and replace with current text
        c.setPosition(prev_block.position())
        c.movePosition(c.MoveOperation.EndOfBlock, c.MoveMode.KeepAnchor)
        c.insertText(current_text)
        # Restore cursor to same column, one block up
        c.setPosition(prev_block.position() + min(col, len(current_text)))
        cursor.endEditBlock()
        self.setTextCursor(c)

    def move_line_down(self) -> None:
        """Swap the current line with the one below it."""
        cursor = self.textCursor()
        block = cursor.block()
        next_block = block.next()
        if not next_block.isValid():
            return
        col = cursor.positionInBlock()
        cursor.beginEditBlock()
        current_text = block.text()
        next_text = next_block.text()
        c = self.textCursor()
        c.setPosition(next_block.position())
        c.movePosition(c.MoveOperation.EndOfBlock, c.MoveMode.KeepAnchor)
        c.insertText(current_text)
        c.setPosition(block.position())
        c.movePosition(c.MoveOperation.EndOfBlock, c.MoveMode.KeepAnchor)
        c.insertText(next_text)
        # Move cursor to same column in the new (next) block position
        new_pos = next_block.position() + min(col, len(current_text))
        c.setPosition(new_pos)
        cursor.endEditBlock()
        self.setTextCursor(c)

    # ── Drag & drop ───────────────────────────────────────────────────

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path.endswith(".gom"):
                    self.setProperty("_dropped_file", path)
                    event.acceptProposedAction()
                    return
        super().dropEvent(event)

    # ── Private helpers ───────────────────────────────────────────────

    def _apply_font(self) -> None:
        font = _monospace_font(self._font_family, self._font_size)
        self.setFont(font)
        self.setTabStopDistance(3 * self.fontMetrics().horizontalAdvance(" "))
        self.update_line_number_area_width()

    def _apply_theme(self) -> None:
        t = self._theme
        self.setStyleSheet(
            f"QPlainTextEdit {{"
            f"  background-color: {t['bg']};"
            f"  color: {t['fg']};"
            f"  selection-background-color: {t['selection']};"
            f"  border: none;"
            f"}}"
        )
