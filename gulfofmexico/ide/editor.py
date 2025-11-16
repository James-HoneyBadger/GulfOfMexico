from __future__ import annotations

from gulfofmexico.ide.qt_compat import Qt, QWidget, QTextEdit

try:
    from PySide6.QtCore import QRect, QSize
    from PySide6.QtGui import QColor, QPainter, QTextFormat
    from PySide6.QtWidgets import QPlainTextEdit
except ImportError:
    from PyQt5.QtCore import QRect, QSize
    from PyQt5.QtGui import QColor, QPainter, QTextFormat
    from PyQt5.QtWidgets import QPlainTextEdit


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):  # noqa: D401, N802
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):  # noqa: N802
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._line_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

    def line_number_area_width(self) -> int:
        digits = 1
        max_count = max(1, self.blockCount())
        while max_count >= 10:
            max_count //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), QColor("# 2b2b2b"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("# aaaaaa"))
                painter.drawText(
                    0,
                    top,
                    self._line_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            line_color = QColor("# 31363b")
            sel.format.setBackground(line_color)
            sel.format.setProperty(QTextFormat.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)
