"""
Gulf of Mexico IDE — Main Application

A polished, configurable IDE for the GOM language featuring:
    - Multiple colour themes (One Dark, Dracula, Nord, Solarized Dark, GitHub Light)
    - Settings dialog (Editor, Appearance, Execution)
    - Toolbar with Run / Stop / New / Open / Save / Settings
    - Multi-tab editor with syntax highlighting
    - Find/Replace bar (Ctrl+F / Ctrl+H)
    - Toggle comment (Ctrl+/)
    - Code auto-completion
    - Bracket matching & indent guides
    - Font zoom (Ctrl+= / Ctrl+-)
    - Line/column status indicator
    - Variable inspector dock
    - Console output with error highlighting
    - Breakpoint gutter (click line numbers)
    - Welcome tab for new users
    - Drag-and-drop .gom file opening
    - Session persistence (geometry, open tabs, settings)
    - Recent files menu
    - Subprocess-based execution with reliable Stop
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from functools import partial
from html import escape as _html_escape
from pathlib import Path

try:
    from gulfofmexico.ide.qt_compat import (
        QAction, QApplication, QCheckBox, QColor, QComboBox, QCompleter,
        QDialog, QDialogButtonBox, QDockWidget, QFileDialog, QFont,
        QFontDatabase, QFormLayout, QFrame, QGuiApplication,
        QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
        QMenu, QMessageBox, QObject, QPushButton, QShortcut, QSizePolicy,
        QSpinBox, QSplitter, Qt, QTabWidget, QTextEdit, QThread,
        QTimer, QToolBar, QToolButton, QTreeWidget, QTreeWidgetItem,
        QVBoxLayout, QWidget, Signal,
    )
    PYSIDE_AVAILABLE = True
except ImportError as _e:
    PYSIDE_AVAILABLE = False
    print(f"Qt not available: {_e}")
    print("Install with: pip install PySide6")

from gulfofmexico.ide.runner import ExecutionSession

# ══════════════════════════════════════════════════════════════════════
# Theme definitions
# ══════════════════════════════════════════════════════════════════════

THEMES: dict[str, dict[str, str]] = {
    "One Dark": {
        "bg":           "#282c34",  "bg_darker":    "#21252b",
        "bg_lighter":   "#2c313a",  "bg_highlight": "#323842",
        "fg":           "#abb2bf",  "fg_dim":       "#636d83",
        "fg_bright":    "#dcdfe4",
        "accent":       "#61afef",  "accent2":      "#c678dd",
        "border":       "#181a1f",  "border_light": "#3e4451",
        "selection":    "#3e4451",
        "error":        "#e06c75",  "warning":      "#d19a66",
        "success":      "#98c379",  "info":         "#56b6c2",
        "gutter_bg":    "#282c34",  "gutter_fg":    "#636d83",
        "gutter_active":"#abb2bf",  "line_highlight":"#2c313a",
        "scrollbar_bg": "#21252b",  "scrollbar_fg": "#3e4451",
        "scrollbar_hover":"#4b5263",
        "indent_guide": "#3e4451",  "bracket_match":"#61afef",
        "syn_keyword":  "#c678dd",  "syn_builtin":  "#61afef",
        "syn_string":   "#98c379",  "syn_number":   "#d19a66",
        "syn_constant": "#d19a66",  "syn_operator": "#56b6c2",
        "syn_comment":  "#5c6370",  "syn_bang":     "#e06c75",
        "syn_name":     "#e5c07b",  "syn_punct":    "#abb2bf",
        "syn_func_kw":  "#c678dd",
    },
    "Dracula": {
        "bg":           "#282a36",  "bg_darker":    "#21222c",
        "bg_lighter":   "#44475a",  "bg_highlight": "#373a49",
        "fg":           "#f8f8f2",  "fg_dim":       "#6272a4",
        "fg_bright":    "#ffffff",
        "accent":       "#bd93f9",  "accent2":      "#ff79c6",
        "border":       "#191a21",  "border_light": "#44475a",
        "selection":    "#44475a",
        "error":        "#ff5555",  "warning":      "#ffb86c",
        "success":      "#50fa7b",  "info":         "#8be9fd",
        "gutter_bg":    "#282a36",  "gutter_fg":    "#6272a4",
        "gutter_active":"#f8f8f2",  "line_highlight":"#2e303e",
        "scrollbar_bg": "#21222c",  "scrollbar_fg": "#44475a",
        "scrollbar_hover":"#6272a4",
        "indent_guide": "#44475a",  "bracket_match":"#bd93f9",
        "syn_keyword":  "#ff79c6",  "syn_builtin":  "#8be9fd",
        "syn_string":   "#f1fa8c",  "syn_number":   "#bd93f9",
        "syn_constant": "#bd93f9",  "syn_operator": "#ff79c6",
        "syn_comment":  "#6272a4",  "syn_bang":     "#ff5555",
        "syn_name":     "#50fa7b",  "syn_punct":    "#f8f8f2",
        "syn_func_kw":  "#ff79c6",
    },
    "Nord": {
        "bg":           "#2e3440",  "bg_darker":    "#242933",
        "bg_lighter":   "#3b4252",  "bg_highlight": "#434c5e",
        "fg":           "#d8dee9",  "fg_dim":       "#616e88",
        "fg_bright":    "#eceff4",
        "accent":       "#88c0d0",  "accent2":      "#b48ead",
        "border":       "#1d2128",  "border_light": "#434c5e",
        "selection":    "#434c5e",
        "error":        "#bf616a",  "warning":      "#d08770",
        "success":      "#a3be8c",  "info":         "#88c0d0",
        "gutter_bg":    "#2e3440",  "gutter_fg":    "#616e88",
        "gutter_active":"#d8dee9",  "line_highlight":"#353c4a",
        "scrollbar_bg": "#242933",  "scrollbar_fg": "#434c5e",
        "scrollbar_hover":"#4c566a",
        "indent_guide": "#434c5e",  "bracket_match":"#88c0d0",
        "syn_keyword":  "#b48ead",  "syn_builtin":  "#88c0d0",
        "syn_string":   "#a3be8c",  "syn_number":   "#b48ead",
        "syn_constant": "#d08770",  "syn_operator": "#81a1c1",
        "syn_comment":  "#616e88",  "syn_bang":     "#bf616a",
        "syn_name":     "#ebcb8b",  "syn_punct":    "#d8dee9",
        "syn_func_kw":  "#b48ead",
    },
    "Solarized Dark": {
        "bg":           "#002b36",  "bg_darker":    "#001e26",
        "bg_lighter":   "#073642",  "bg_highlight": "#0a4050",
        "fg":           "#839496",  "fg_dim":       "#586e75",
        "fg_bright":    "#fdf6e3",
        "accent":       "#268bd2",  "accent2":      "#d33682",
        "border":       "#001920",  "border_light": "#073642",
        "selection":    "#073642",
        "error":        "#dc322f",  "warning":      "#cb4b16",
        "success":      "#859900",  "info":         "#2aa198",
        "gutter_bg":    "#002b36",  "gutter_fg":    "#586e75",
        "gutter_active":"#93a1a1",  "line_highlight":"#073642",
        "scrollbar_bg": "#001e26",  "scrollbar_fg": "#073642",
        "scrollbar_hover":"#586e75",
        "indent_guide": "#073642",  "bracket_match":"#268bd2",
        "syn_keyword":  "#859900",  "syn_builtin":  "#268bd2",
        "syn_string":   "#2aa198",  "syn_number":   "#d33682",
        "syn_constant": "#cb4b16",  "syn_operator": "#859900",
        "syn_comment":  "#586e75",  "syn_bang":     "#dc322f",
        "syn_name":     "#b58900",  "syn_punct":    "#839496",
        "syn_func_kw":  "#859900",
    },
    "GitHub Light": {
        "bg":           "#ffffff",  "bg_darker":    "#f6f8fa",
        "bg_lighter":   "#f0f2f5",  "bg_highlight": "#e8eaed",
        "fg":           "#24292e",  "fg_dim":       "#6a737d",
        "fg_bright":    "#000000",
        "accent":       "#0366d6",  "accent2":      "#6f42c1",
        "border":       "#e1e4e8",  "border_light": "#d1d5da",
        "selection":    "#c8e1ff",
        "error":        "#d73a49",  "warning":      "#e36209",
        "success":      "#28a745",  "info":         "#005cc5",
        "gutter_bg":    "#fafbfc",  "gutter_fg":    "#babbbd",
        "gutter_active":"#24292e",  "line_highlight":"#f6f8fa",
        "scrollbar_bg": "#f6f8fa",  "scrollbar_fg": "#d1d5da",
        "scrollbar_hover":"#959da5",
        "indent_guide": "#e1e4e8",  "bracket_match":"#0366d6",
        "syn_keyword":  "#d73a49",  "syn_builtin":  "#005cc5",
        "syn_string":   "#032f62",  "syn_number":   "#005cc5",
        "syn_constant": "#e36209",  "syn_operator": "#d73a49",
        "syn_comment":  "#6a737d",  "syn_bang":     "#d73a49",
        "syn_name":     "#6f42c1",  "syn_punct":    "#24292e",
        "syn_func_kw":  "#d73a49",
    },
}

DEFAULT_THEME = "One Dark"

# ── Default settings ──────────────────────────────────────────────────

_DEFAULT_SETTINGS: dict[str, object] = {
    "theme":              DEFAULT_THEME,
    "font_family":        "",
    "font_size":          12,
    "tab_width":          3,
    "word_wrap":          False,
    "show_indent_guides": True,
    "bracket_matching":   True,
    "auto_complete":      True,
    "console_font_size":  11,
    "show_toolbar":       True,
    "show_line_numbers":  True,
    "run_timeout":        30,
    "show_traceback":     False,
}


# ══════════════════════════════════════════════════════════════════════
# Stylesheet generator
# ══════════════════════════════════════════════════════════════════════

def _generate_stylesheet(t: dict[str, str]) -> str:
    """Build the full application QSS from a theme dict."""
    return f"""
/* ── Window ────────────────────────────────────────────────────── */
QMainWindow {{
    background-color: {t['bg_darker']};
}}

/* ── Menu bar ──────────────────────────────────────────────────── */
QMenuBar {{
    background-color: {t['bg_darker']};
    color: {t['fg']};
    border-bottom: 1px solid {t['border']};
    padding: 2px 0;
    font-size: 13px;
}}
QMenuBar::item {{
    padding: 5px 12px;
    border-radius: 4px;
    margin: 1px 2px;
}}
QMenuBar::item:selected {{
    background-color: {t['bg_lighter']};
}}
QMenu {{
    background-color: {t['bg_darker']};
    color: {t['fg']};
    border: 1px solid {t['border_light']};
    border-radius: 8px;
    padding: 6px 0;
}}
QMenu::item {{
    padding: 6px 30px 6px 20px;
    border-radius: 4px;
    margin: 1px 6px;
}}
QMenu::item:selected {{
    background-color: {t['accent']};
    color: {t['fg_bright']};
}}
QMenu::separator {{
    height: 1px;
    background: {t['border_light']};
    margin: 4px 14px;
}}

/* ── Tab bar ───────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: none;
    background: {t['bg']};
}}
QTabBar {{
    background: {t['bg_darker']};
    qproperty-drawBase: 0;
}}
QTabBar::tab {{
    background: {t['bg_darker']};
    color: {t['fg_dim']};
    padding: 8px 22px;
    border: none;
    border-bottom: 2px solid transparent;
    min-width: 100px;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background: {t['bg']};
    color: {t['fg']};
    border-bottom: 2px solid {t['accent']};
}}
QTabBar::tab:hover:!selected {{
    background: {t['bg_lighter']};
    color: {t['fg']};
}}
QTabBar::close-button {{
    image: none;
    subcontrol-position: right;
    padding: 4px;
}}

/* ── Buttons ───────────────────────────────────────────────────── */
QPushButton {{
    background-color: {t['bg_lighter']};
    color: {t['fg']};
    border: 1px solid {t['border_light']};
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 12px;
    min-width: 64px;
}}
QPushButton:hover {{
    background-color: {t['bg_highlight']};
    border-color: {t['accent']};
}}
QPushButton:pressed {{
    background-color: {t['selection']};
}}
QPushButton:disabled {{
    color: {t['fg_dim']};
    background-color: {t['bg_darker']};
    border-color: {t['border']};
}}

/* ── Text areas ────────────────────────────────────────────────── */
QTextEdit, QPlainTextEdit {{
    background-color: {t['bg']};
    color: {t['fg']};
    border: none;
    selection-background-color: {t['selection']};
}}

/* ── Line edit ─────────────────────────────────────────────────── */
QLineEdit {{
    background-color: {t['bg']};
    color: {t['fg']};
    border: 1px solid {t['border_light']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}
QLineEdit:focus {{
    border-color: {t['accent']};
}}

/* ── Dock widgets ──────────────────────────────────────────────── */
QDockWidget {{
    color: {t['fg']};
    font-size: 12px;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}
QDockWidget::title {{
    background: {t['bg_darker']};
    padding: 8px 12px;
    border-bottom: 1px solid {t['border']};
    font-size: 11px;
    font-weight: bold;
}}

/* ── Status bar ────────────────────────────────────────────────── */
QStatusBar {{
    background: {t['bg_darker']};
    color: {t['fg_dim']};
    border-top: 1px solid {t['border']};
    font-size: 12px;
    padding: 2px 0;
    min-height: 24px;
}}
QStatusBar QLabel {{
    padding: 0 8px;
    font-size: 12px;
}}
QStatusBar::item {{
    border: none;
}}

/* ── Tree widget ───────────────────────────────────────────────── */
QTreeWidget {{
    background-color: {t['bg']};
    color: {t['fg']};
    border: none;
    outline: none;
    font-size: 12px;
}}
QTreeWidget::item {{
    padding: 4px 2px;
    border-radius: 4px;
}}
QTreeWidget::item:selected {{
    background-color: {t['selection']};
}}
QTreeWidget::item:hover {{
    background-color: {t['bg_lighter']};
}}
QHeaderView::section {{
    background-color: {t['bg_darker']};
    color: {t['fg_dim']};
    border: none;
    border-right: 1px solid {t['border']};
    border-bottom: 1px solid {t['border']};
    padding: 6px 8px;
    font-weight: bold;
    font-size: 11px;
}}

/* ── Splitter ──────────────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {t['border']};
    width: 1px;
    height: 1px;
}}

/* ── Scrollbars ────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {t['scrollbar_bg']};
    width: 10px;
    border: none;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {t['scrollbar_fg']};
    min-height: 30px;
    border-radius: 5px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: {t['scrollbar_hover']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
QScrollBar:horizontal {{
    background: {t['scrollbar_bg']};
    height: 10px;
    border: none;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal {{
    background: {t['scrollbar_fg']};
    min-width: 30px;
    border-radius: 5px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {t['scrollbar_hover']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* ── Labels ────────────────────────────────────────────────────── */
QLabel {{
    color: {t['fg']};
}}

/* ── Autocomplete popup ────────────────────────────────────────── */
QCompleter QAbstractItemView {{
    background-color: {t['bg_darker']};
    color: {t['fg']};
    selection-background-color: {t['accent']};
    selection-color: {t['fg_bright']};
    border: 1px solid {t['border_light']};
    border-radius: 6px;
    padding: 2px;
    outline: none;
}}

/* ── Toolbar ───────────────────────────────────────────────────── */
QToolBar {{
    background: {t['bg_darker']};
    border-bottom: 1px solid {t['border']};
    padding: 4px 8px;
    spacing: 2px;
}}
QToolBar::separator {{
    width: 1px;
    background: {t['border_light']};
    margin: 4px 6px;
}}
QToolButton {{
    background: transparent;
    color: {t['fg']};
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    min-width: 28px;
}}
QToolButton:hover {{
    background: {t['bg_lighter']};
    border-color: {t['border_light']};
}}
QToolButton:pressed {{
    background: {t['selection']};
}}

/* ── Tooltips ──────────────────────────────────────────────────── */
QToolTip {{
    background-color: {t['bg_lighter']};
    color: {t['fg']};
    border: 1px solid {t['border_light']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ── Dialog ────────────────────────────────────────────────────── */
QDialog {{
    background-color: {t['bg_darker']};
}}
QGroupBox {{
    color: {t['fg']};
    border: 1px solid {t['border_light']};
    border-radius: 8px;
    margin-top: 14px;
    padding: 18px 12px 10px 12px;
    font-weight: bold;
    font-size: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
}}
QCheckBox {{
    color: {t['fg']};
    spacing: 8px;
    font-size: 12px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {t['border_light']};
    border-radius: 4px;
    background: {t['bg']};
}}
QCheckBox::indicator:hover {{
    border-color: {t['accent']};
}}
QCheckBox::indicator:checked {{
    background: {t['accent']};
    border-color: {t['accent']};
}}
QComboBox {{
    background-color: {t['bg']};
    color: {t['fg']};
    border: 1px solid {t['border_light']};
    border-radius: 6px;
    padding: 6px 10px;
    min-width: 160px;
    font-size: 12px;
}}
QComboBox:hover {{
    border-color: {t['accent']};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {t['bg_darker']};
    color: {t['fg']};
    selection-background-color: {t['accent']};
    selection-color: {t['fg_bright']};
    border: 1px solid {t['border_light']};
    border-radius: 6px;
    outline: none;
}}
QSpinBox {{
    background-color: {t['bg']};
    color: {t['fg']};
    border: 1px solid {t['border_light']};
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
    min-width: 80px;
}}
QSpinBox:hover {{
    border-color: {t['accent']};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    border: none;
    width: 16px;
}}
QDialogButtonBox QPushButton {{
    min-width: 90px;
}}
QFormLayout {{
    margin: 16px;
}}

/* ── Find bar (custom styling) ─────────────────────────────────── */
QWidget#findBar {{
    background: {t['bg_darker']};
    border-bottom: 1px solid {t['border']};
}}
QWidget#findBar QLineEdit {{
    min-width: 200px;
    padding: 5px 10px;
}}
QWidget#findBar QPushButton {{
    min-width: 44px;
    padding: 5px 10px;
    font-size: 11px;
}}
QWidget#findBar QLabel {{
    font-size: 11px;
    color: {t['fg_dim']};
    font-weight: bold;
}}
"""


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _format_error_html(err: str, theme: dict[str, str]) -> str:
    color = theme.get("error", "#e06c75")
    return (
        f"<pre style='color:{color}; font-family:monospace; "
        f"white-space: pre-wrap; margin: 4px 0;'>{_html_escape(err)}</pre>"
    )


def _monospace_fonts() -> list[str]:
    """Return a sorted list of available monospace font families."""
    try:
        db = QFontDatabase()
        all_fams = QFontDatabase.families()
        monospace = []
        for fam in all_fams:
            if QFontDatabase.isFixedPitch(fam):
                monospace.append(fam)
        return sorted(set(monospace)) if monospace else ["monospace"]
    except Exception:
        return ["JetBrains Mono", "Fira Code", "Consolas", "Source Code Pro", "monospace"]


# ══════════════════════════════════════════════════════════════════════
# Guard: everything below requires Qt
# ══════════════════════════════════════════════════════════════════════

if PYSIDE_AVAILABLE:
    from gulfofmexico.ide.editor import CodeEditor
    from gulfofmexico.ide.highlighter import GomHighlighter

    # ──────────────────────────────────────────────────────────────
    # Auto-completion word list
    # ──────────────────────────────────────────────────────────────
    _COMPLETION_WORDS = sorted(set([
        "var", "const", "if", "else", "when", "after", "class", "return",
        "delete", "async", "await", "previous", "next", "reverse",
        "export", "import", "to", "new", "current", "function", "fn", "func",
        "print", "read", "readfile", "write", "exit", "sleep", "use",
        "Number", "String", "Boolean", "Map",
        "abs", "floor", "ceil", "round", "sqrt", "sin", "cos", "tan",
        "log", "exp", "degrees", "radians", "pow", "min", "max",
        "random", "randomInt",
        "regex_match", "regex_findall", "regex_replace",
        "true", "false", "maybe", "undefined", "noop", "Date",
        "zero", "one", "two", "three", "four", "five", "six", "seven",
        "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
        "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
        "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
        "eighty", "ninety", "hundred", "thousand", "million",
        "half", "third", "quarter",
    ]))

    # ──────────────────────────────────────────────────────────────
    # Settings dialog
    # ──────────────────────────────────────────────────────────────
    class SettingsDialog(QDialog):
        """Modal settings dialog with Editor / Appearance / Execution tabs."""

        def __init__(self, settings: dict, parent=None) -> None:
            super().__init__(parent)
            self.setWindowTitle("  Settings")
            self.setMinimumSize(520, 440)
            self._settings = dict(settings)

            root = QVBoxLayout(self)
            root.setContentsMargins(0, 0, 0, 0)
            root.setSpacing(0)

            # Header
            header = QLabel("  Settings")
            header.setStyleSheet(
                "font-size: 16px; font-weight: bold; padding: 16px 20px;"
            )
            root.addWidget(header)

            # Separator
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: palette(mid);")
            root.addWidget(sep)

            tabs = QTabWidget()
            tabs.setDocumentMode(True)
            root.addWidget(tabs, 1)

            # ── Editor tab ─────────────────────────────────────
            editor_page = QWidget()
            ef = QFormLayout(editor_page)
            ef.setContentsMargins(24, 20, 24, 16)
            ef.setSpacing(14)
            ef.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

            self.font_combo = QComboBox()
            self.font_combo.setEditable(True)
            for fam in _monospace_fonts():
                self.font_combo.addItem(fam)
            ef.addRow("Font Family", self.font_combo)

            self.font_size = QSpinBox()
            self.font_size.setRange(8, 36)
            ef.addRow("Font Size", self.font_size)

            self.tab_width = QSpinBox()
            self.tab_width.setRange(1, 8)
            ef.addRow("Tab Width", self.tab_width)

            self.word_wrap = QCheckBox("Enable word wrap")
            ef.addRow("Word Wrap", self.word_wrap)

            self.indent_guides = QCheckBox("Show indent guide lines")
            ef.addRow("Indent Guides", self.indent_guides)

            self.bracket_match = QCheckBox("Highlight matching brackets")
            ef.addRow("Bracket Match", self.bracket_match)

            self.autocomplete = QCheckBox("Show code completions")
            ef.addRow("Auto-Complete", self.autocomplete)

            tabs.addTab(editor_page, "  Editor  ")

            # ── Appearance tab ─────────────────────────────────
            appearance_page = QWidget()
            af = QFormLayout(appearance_page)
            af.setContentsMargins(24, 20, 24, 16)
            af.setSpacing(14)
            af.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

            self.theme_combo = QComboBox()
            for name in THEMES:
                self.theme_combo.addItem(name)
            af.addRow("Theme", self.theme_combo)

            self.console_font_size = QSpinBox()
            self.console_font_size.setRange(8, 24)
            af.addRow("Console Font Size", self.console_font_size)

            self.show_toolbar = QCheckBox("Show toolbar")
            af.addRow("Toolbar", self.show_toolbar)

            tabs.addTab(appearance_page, "  Appearance  ")

            # ── Execution tab ──────────────────────────────────
            exec_page = QWidget()
            xf = QFormLayout(exec_page)
            xf.setContentsMargins(24, 20, 24, 16)
            xf.setSpacing(14)
            xf.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

            self.run_timeout = QSpinBox()
            self.run_timeout.setRange(5, 300)
            self.run_timeout.setSuffix(" seconds")
            xf.addRow("Run Timeout", self.run_timeout)

            self.show_traceback = QCheckBox("Show Python traceback on error")
            xf.addRow("Traceback", self.show_traceback)

            tabs.addTab(exec_page, "  Execution  ")

            # ── Button box ─────────────────────────────────────
            sep2 = QFrame()
            sep2.setFrameShape(QFrame.Shape.HLine)
            sep2.setStyleSheet("color: palette(mid);")
            root.addWidget(sep2)

            btn_row = QHBoxLayout()
            btn_row.setContentsMargins(16, 12, 16, 12)
            btn_row.addStretch()
            btn_cancel = QPushButton("Cancel")
            btn_cancel.clicked.connect(self.reject)
            btn_ok = QPushButton("Apply")
            btn_ok.setDefault(True)
            btn_ok.clicked.connect(self.accept)
            btn_row.addWidget(btn_cancel)
            btn_row.addWidget(btn_ok)
            root.addLayout(btn_row)

            self._populate()

        def _populate(self) -> None:
            s = self._settings
            idx = self.font_combo.findText(str(s.get("font_family", "")))
            if idx >= 0:
                self.font_combo.setCurrentIndex(idx)
            else:
                self.font_combo.setEditText(str(s.get("font_family", "")))
            self.font_size.setValue(int(s.get("font_size", 12)))
            self.tab_width.setValue(int(s.get("tab_width", 3)))
            self.word_wrap.setChecked(bool(s.get("word_wrap", False)))
            self.indent_guides.setChecked(bool(s.get("show_indent_guides", True)))
            self.bracket_match.setChecked(bool(s.get("bracket_matching", True)))
            self.autocomplete.setChecked(bool(s.get("auto_complete", True)))
            idx = self.theme_combo.findText(str(s.get("theme", DEFAULT_THEME)))
            if idx >= 0:
                self.theme_combo.setCurrentIndex(idx)
            self.console_font_size.setValue(int(s.get("console_font_size", 11)))
            self.show_toolbar.setChecked(bool(s.get("show_toolbar", True)))
            self.run_timeout.setValue(int(s.get("run_timeout", 30)))
            self.show_traceback.setChecked(bool(s.get("show_traceback", False)))

        def result_settings(self) -> dict:
            return {
                "font_family":        self.font_combo.currentText(),
                "font_size":          self.font_size.value(),
                "tab_width":          self.tab_width.value(),
                "word_wrap":          self.word_wrap.isChecked(),
                "show_indent_guides": self.indent_guides.isChecked(),
                "bracket_matching":   self.bracket_match.isChecked(),
                "auto_complete":      self.autocomplete.isChecked(),
                "theme":              self.theme_combo.currentText(),
                "console_font_size":  self.console_font_size.value(),
                "show_toolbar":       self.show_toolbar.isChecked(),
                "run_timeout":        self.run_timeout.value(),
                "show_traceback":     self.show_traceback.isChecked(),
            }

    # ──────────────────────────────────────────────────────────────
    # Find / Replace bar
    # ──────────────────────────────────────────────────────────────
    class FindReplaceBar(QWidget):
        def __init__(self, parent: "MainWindow") -> None:
            super().__init__(parent)
            self.setObjectName("findBar")
            self.main_win = parent
            layout = QHBoxLayout(self)
            layout.setContentsMargins(12, 6, 12, 6)
            layout.setSpacing(6)

            self.find_input = QLineEdit()
            self.find_input.setPlaceholderText("Find…")
            self.find_input.returnPressed.connect(self._find_next)

            self.replace_input = QLineEdit()
            self.replace_input.setPlaceholderText("Replace…")
            self.replace_input.returnPressed.connect(self._replace_next)

            btn_prev = QPushButton("◀")
            btn_prev.setToolTip("Find Previous")
            btn_prev.setMaximumWidth(44)
            btn_prev.clicked.connect(self._find_prev)

            btn_next = QPushButton("▶")
            btn_next.setToolTip("Find Next")
            btn_next.setMaximumWidth(44)
            btn_next.clicked.connect(self._find_next)

            btn_replace = QPushButton("Replace")
            btn_replace.setMaximumWidth(70)
            btn_replace.clicked.connect(self._replace_next)

            btn_all = QPushButton("All")
            btn_all.setToolTip("Replace All")
            btn_all.setMaximumWidth(50)
            btn_all.clicked.connect(self._replace_all)

            btn_close = QPushButton("✕")
            btn_close.setToolTip("Close find bar")
            btn_close.setMaximumWidth(32)
            btn_close.setStyleSheet("border: none; font-size: 14px;")
            btn_close.clicked.connect(self.hide)

            lbl_find = QLabel("FIND")
            lbl_find.setStyleSheet("font-weight: bold;")

            layout.addWidget(lbl_find)
            layout.addWidget(self.find_input, 1)
            layout.addWidget(btn_prev)
            layout.addWidget(btn_next)
            layout.addSpacing(12)
            layout.addWidget(QLabel("REPLACE"))
            layout.addWidget(self.replace_input, 1)
            layout.addWidget(btn_replace)
            layout.addWidget(btn_all)
            layout.addSpacing(8)
            layout.addWidget(btn_close)

            self.setVisible(False)

        def show_find(self) -> None:
            self.setVisible(True)
            self.find_input.setFocus()
            self.find_input.selectAll()

        def show_replace(self) -> None:
            self.setVisible(True)
            self.replace_input.setFocus()

        def _editor(self):
            return self.main_win._current_editor()

        def _find_next(self) -> None:
            ed = self._editor()
            if not ed:
                return
            text = self.find_input.text()
            if not text:
                return
            if not ed.find(text):
                cursor = ed.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                ed.setTextCursor(cursor)
                ed.find(text)

        def _find_prev(self) -> None:
            ed = self._editor()
            if not ed:
                return
            text = self.find_input.text()
            if not text:
                return
            try:
                flag = QTextEdit.FindFlag.FindBackward
            except AttributeError:
                flag = 1
            if not ed.find(text, flag):
                cursor = ed.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                ed.setTextCursor(cursor)
                ed.find(text, flag)

        def _replace_next(self) -> None:
            ed = self._editor()
            if not ed:
                return
            if ed.textCursor().selectedText() == self.find_input.text():
                ed.textCursor().insertText(self.replace_input.text())
            self._find_next()

        def _replace_all(self) -> None:
            ed = self._editor()
            if not ed:
                return
            text = self.find_input.text()
            repl = self.replace_input.text()
            if not text:
                return
            content = ed.toPlainText()
            new = content.replace(text, repl)
            if new != content:
                ed.setPlainText(new)

    # ──────────────────────────────────────────────────────────────
    # Worker — subprocess execution
    # ──────────────────────────────────────────────────────────────
    class Worker(QObject):
        finished = Signal(str, str)

        def __init__(self, code: str, filename: str, *, timeout: int = 30) -> None:
            super().__init__()
            self.code = code
            self.filename = filename
            self.timeout = timeout
            self._process: subprocess.Popen | None = None

        def run(self) -> None:
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".gom", delete=False, encoding="utf-8"
                ) as tmp:
                    tmp.write(self.code)
                    tmp_path = tmp.name

                self._process = subprocess.Popen(
                    [sys.executable, "-m", "gulfofmexico", tmp_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                try:
                    stdout, stderr = self._process.communicate(timeout=self.timeout)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    stdout, stderr = self._process.communicate()
                    stderr = (stderr or "") + f"\n[Execution timed out after {self.timeout}s]"
                finally:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass

                if self._process.returncode != 0 and stderr:
                    self.finished.emit(stdout or "", stderr)
                else:
                    self.finished.emit(stdout or "", "")
            except Exception as e:
                self.finished.emit("", str(e))

        def kill(self) -> None:
            if self._process and self._process.poll() is None:
                try:
                    self._process.kill()
                except OSError:
                    pass

    # ──────────────────────────────────────────────────────────────
    # Variable inspector
    # ──────────────────────────────────────────────────────────────
    class VariableInspector(QDockWidget):
        def __init__(self, parent=None) -> None:
            super().__init__("  Variables", parent)
            self.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable
                | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )
            self.tree = QTreeWidget()
            self.tree.setHeaderLabels(["Name", "Type", "Value"])
            self.tree.setColumnCount(3)
            self.tree.setRootIsDecorated(False)
            self.tree.setAlternatingRowColors(False)
            header = self.tree.header()
            header.setStretchLastSection(True)
            try:
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            except Exception:
                pass
            self.setWidget(self.tree)

        def update_variables(self, session: ExecutionSession) -> None:
            self.tree.clear()
            if not session.namespaces:
                return
            from gulfofmexico.builtin import (
                GulfOfMexicoKeyword, Name, Variable, db_to_string,
            )
            seen: set[str] = set()
            for ns in reversed(session.namespaces):
                for name, entry in sorted(ns.items()):
                    if name in seen:
                        continue
                    seen.add(name)
                    if isinstance(entry, (Variable, Name)):
                        val = (
                            entry.value if isinstance(entry, Name)
                            else (entry.lifetimes[0].value if entry.lifetimes else None)
                        )
                        if val is None or isinstance(val, GulfOfMexicoKeyword):
                            continue
                        type_name = type(val).__name__.replace("GulfOfMexico", "")
                        try:
                            vs = db_to_string(val).value
                            if len(vs) > 80:
                                vs = vs[:77] + "…"
                        except Exception:
                            vs = "…"
                        self.tree.addTopLevelItem(QTreeWidgetItem([name, type_name, vs]))

    # ──────────────────────────────────────────────────────────────
    # Console widget (output panel)
    # ──────────────────────────────────────────────────────────────
    class ConsoleOutput(QTextEdit):
        """Read-only console with configurable font size and monospace font."""

        def __init__(self, parent=None, *, font_size: int = 11) -> None:
            super().__init__(parent)
            self.setReadOnly(True)
            self._font_size = font_size
            self._apply_font()

        def set_font_size(self, size: int) -> None:
            self._font_size = size
            self._apply_font()

        def _apply_font(self) -> None:
            font = QFont("monospace", self._font_size)
            for fam in ("JetBrains Mono", "Fira Code", "Consolas", "Source Code Pro"):
                f = QFont(fam, self._font_size)
                if f.exactMatch():
                    font = f
                    break
            self.setFont(font)

    # ──────────────────────────────────────────────────────────────
    # Main window
    # ──────────────────────────────────────────────────────────────
    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Gulf of Mexico IDE")
            self.resize(1280, 900)

            self.session = ExecutionSession()
            self.thread: QThread | None = None
            self.worker: Worker | None = None

            # ── Settings ───────────────────────────────────────
            self._settings_path = Path.home() / ".config" / "gom-ide" / "settings.json"
            self._recent_path = Path.home() / ".config" / "gom-ide" / "recent.json"
            self._settings: dict = dict(_DEFAULT_SETTINGS)
            self.recent_files: list[str] = []
            self._load_settings_from_disk()
            self._load_recent_from_disk()
            self._current_theme_name: str = str(self._settings.get("theme", DEFAULT_THEME))
            self._theme: dict[str, str] = THEMES.get(self._current_theme_name, THEMES[DEFAULT_THEME])

            # ── Central layout ─────────────────────────────────
            self.tabs = QTabWidget()
            self.tabs.setTabsClosable(True)
            self.tabs.setMovable(True)
            self.tabs.setDocumentMode(True)
            self.tabs.tabCloseRequested.connect(self._close_tab)
            self.tabs.currentChanged.connect(self._on_tab_changed)

            self.find_bar = FindReplaceBar(self)

            central = QWidget()
            vbox = QVBoxLayout(central)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(0)
            vbox.addWidget(self.find_bar)
            vbox.addWidget(self.tabs, 1)
            self.setCentralWidget(central)

            # ── Console dock ───────────────────────────────────
            self.console = ConsoleOutput(
                font_size=int(self._settings.get("console_font_size", 11))
            )
            self.console.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.console.customContextMenuRequested.connect(self._console_ctx_menu)
            self._console_dock = QDockWidget("  Console", self)
            self._console_dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable
                | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )
            self._console_dock.setWidget(self.console)
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._console_dock)

            # ── Variable inspector dock ────────────────────────
            self.var_inspector = VariableInspector(self)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.var_inspector)

            # ── Status bar ─────────────────────────────────────
            self._status_pos = QLabel("Ln 1, Col 1")
            self._status_pos.setMinimumWidth(100)
            self._status_lang = QLabel("GOM")
            self._status_lang.setMinimumWidth(40)
            self._status_theme = QLabel(self._current_theme_name)
            self._status_encoding = QLabel("UTF-8")
            self._status_zoom = QLabel("100%")
            self._status_zoom.setMinimumWidth(50)

            sb = self.statusBar()
            sb.addPermanentWidget(self._build_status_sep())
            sb.addPermanentWidget(self._status_pos)
            sb.addPermanentWidget(self._build_status_sep())
            sb.addPermanentWidget(self._status_encoding)
            sb.addPermanentWidget(self._build_status_sep())
            sb.addPermanentWidget(self._status_zoom)
            sb.addPermanentWidget(self._build_status_sep())
            sb.addPermanentWidget(self._status_theme)
            sb.addPermanentWidget(self._build_status_sep())
            sb.addPermanentWidget(self._status_lang)
            sb.showMessage("Ready")

            # ── Toolbar ────────────────────────────────────────
            self._toolbar = self.addToolBar("Main")
            self._toolbar.setMovable(False)
            self._toolbar.setFloatable(False)
            self._build_toolbar()

            # ── Menus ──────────────────────────────────────────
            self._open_recent_menu: QMenu | None = None
            self._build_menus()

            # ── Initial tab ────────────────────────────────────
            self._new_tab()
            self._show_welcome()

            # ── Apply saved window geometry + open files ───────
            self._restore_session()

            # ── Apply theme ────────────────────────────────────
            self._apply_full_theme()

        # ── Status bar helpers ────────────────────────────────

        @staticmethod
        def _build_status_sep() -> QFrame:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setFixedWidth(1)
            sep.setStyleSheet("color: #3e4451;")
            return sep

        # ── Theme application ─────────────────────────────────

        def _apply_full_theme(self) -> None:
            """Apply the current theme to the entire application."""
            t = self._theme
            app = QApplication.instance()
            if app:
                app.setStyleSheet(_generate_stylesheet(t))

            # Update all editors
            for i in range(self.tabs.count()):
                ed = self.tabs.widget(i)
                if isinstance(ed, CodeEditor):
                    ed.apply_settings(theme=t)
                    hl = ed.findChild(GomHighlighter)
                    if hl:
                        hl.set_theme(t)
                    else:
                        # Rehighlight via document highlighters
                        pass

            # Console font
            self.console.set_font_size(int(self._settings.get("console_font_size", 11)))

            # Theme label
            self._status_theme.setText(self._current_theme_name)

            # Toolbar visibility
            self._toolbar.setVisible(bool(self._settings.get("show_toolbar", True)))

        # ── Settings ──────────────────────────────────────────

        def _open_settings(self) -> None:
            dlg = SettingsDialog(self._settings, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                new = dlg.result_settings()
                old_theme = self._settings.get("theme")
                self._settings.update(new)
                self._current_theme_name = str(new.get("theme", DEFAULT_THEME))
                self._theme = THEMES.get(self._current_theme_name, THEMES[DEFAULT_THEME])
                self._apply_settings_to_editors()
                self._apply_full_theme()
                self._save_settings_to_disk()

        def _apply_settings_to_editors(self) -> None:
            s = self._settings
            for i in range(self.tabs.count()):
                ed = self.tabs.widget(i)
                if isinstance(ed, CodeEditor):
                    ed.apply_settings(
                        theme=self._theme,
                        font_family=str(s.get("font_family", "")),
                        font_size=int(s.get("font_size", 12)),
                        show_indent_guides=bool(s.get("show_indent_guides", True)),
                        bracket_matching=bool(s.get("bracket_matching", True)),
                    )
                    hl = ed.document().findChild(GomHighlighter)
                    if hl:
                        hl.set_theme(self._theme)
            self.console.set_font_size(int(s.get("console_font_size", 11)))

        # ── Welcome ───────────────────────────────────────────

        def _show_welcome(self) -> None:
            ed = self._current_editor()
            if not ed or ed.toPlainText().strip() or (ed.property("path") or ""):
                return
            t = self._current_theme_name
            welcome = (
                "// ╔═══════════════════════════════════════════════════════╗\n"
                "// ║       Welcome to the Gulf of Mexico IDE              ║\n"
                "// ╚═══════════════════════════════════════════════════════╝\n"
                "//\n"
                "// An experimental language featuring:\n"
                "//   • -1 based indexing\n"
                "//   • Three-valued booleans (true / false / maybe)\n"
                "//   • Significant whitespace for operator precedence\n"
                "//   • No loops — recursion only\n"
                "//   • Statement terminators: !  !!  !!!  ?\n"
                "//   • Emoji identifiers  🎉\n"
                "//\n"
                "// Shortcuts:\n"
                "//   F5          Run code\n"
                "//   Ctrl+N      New file\n"
                "//   Ctrl+O      Open file\n"
                "//   Ctrl+S      Save\n"
                "//   Ctrl+,      Settings\n"
                "//   Ctrl+=/-    Zoom in/out\n"
                "//   Ctrl+F      Find\n"
                "//   Ctrl+H      Find & Replace\n"
                "//   Ctrl+/      Toggle comment\n"
                "//\n"
                f"// Theme: {t}\n"
                "//\n\n"
                'print "Hello, Gulf of Mexico"!\n'
            )
            ed.setPlainText(welcome)
            ed.document().setModified(False)

        # ── Tab management ────────────────────────────────────

        def _new_tab(self, path: str | None = None,
                     content: str | None = None) -> "CodeEditor":
            s = self._settings
            editor = CodeEditor(
                theme=self._theme,
                font_family=str(s.get("font_family", "")),
                font_size=int(s.get("font_size", 12)),
                show_indent_guides=bool(s.get("show_indent_guides", True)),
                bracket_matching=bool(s.get("bracket_matching", True)),
            )
            hl = GomHighlighter(editor.document(), theme=self._theme)
            if content:
                editor.setPlainText(content)
            tab_name = Path(path).name if path else "untitled.gom"
            idx = self.tabs.addTab(editor, tab_name)
            self.tabs.setCurrentIndex(idx)
            editor.setProperty("path", path or "")
            self._connect_editor(editor)
            if bool(s.get("auto_complete", True)):
                self._setup_completer(editor)
            return editor

        def _setup_completer(self, editor: CodeEditor) -> None:
            completer = QCompleter(_COMPLETION_WORDS, editor)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setWidget(editor)
            popup = completer.popup()
            popup.setStyleSheet(
                f"QListView {{ background: {self._theme['bg_darker']}; "
                f"color: {self._theme['fg']}; border: 1px solid {self._theme['border_light']}; "
                f"border-radius: 6px; font-family: monospace; padding: 2px; }}"
            )
            editor.setProperty("_completer", completer)

            def _on_text():
                cursor = editor.textCursor()
                cursor.movePosition(cursor.MoveOperation.StartOfWord,
                                    cursor.MoveMode.KeepAnchor)
                prefix = cursor.selectedText()
                if len(prefix) < 2:
                    completer.popup().hide()
                    return
                completer.setCompletionPrefix(prefix)
                if completer.completionCount() == 0:
                    completer.popup().hide()
                    return
                cr = editor.cursorRect()
                cr.setWidth(
                    completer.popup().sizeHintForColumn(0)
                    + (completer.popup().verticalScrollBar().sizeHint().width()
                       if completer.popup().verticalScrollBar() else 0)
                )
                completer.complete(cr)

            def _insert(text: str):
                cursor = editor.textCursor()
                cursor.movePosition(cursor.MoveOperation.StartOfWord,
                                    cursor.MoveMode.KeepAnchor)
                cursor.insertText(text)

            editor.textChanged.connect(_on_text)
            completer.activated.connect(_insert)

        def _connect_editor(self, editor: CodeEditor) -> None:
            editor.document().modificationChanged.connect(
                lambda m: self._on_modified(editor, m)
            )
            editor.cursorPositionChanged.connect(
                lambda: self._update_cursor_pos(editor)
            )

        def _current_editor(self) -> CodeEditor | None:
            w = self.tabs.currentWidget()
            return w if isinstance(w, CodeEditor) else None

        def _on_tab_changed(self, _idx: int) -> None:
            ed = self._current_editor()
            if ed:
                self._update_cursor_pos(ed)
                self._update_zoom_label(ed)

        def _update_cursor_pos(self, ed: CodeEditor) -> None:
            if ed != self._current_editor():
                return
            c = ed.textCursor()
            self._status_pos.setText(f"Ln {c.blockNumber()+1}, Col {c.columnNumber()+1}")

        def _update_zoom_label(self, ed: CodeEditor) -> None:
            pct = round(ed.current_font_size / 12 * 100)
            self._status_zoom.setText(f"{pct}%")

        def _close_tab(self, index: int) -> None:
            w = self.tabs.widget(index)
            if isinstance(w, CodeEditor) and not self._maybe_save(w):
                return
            self.tabs.removeTab(index)
            if self.tabs.count() == 0:
                self._new_tab()

        # ── File operations ───────────────────────────────────

        def _open_file(self) -> None:
            path, _ = QFileDialog.getOpenFileName(
                self, "Open .gom", os.getcwd(),
                "Gulf of Mexico (*.gom);;All Files (*)",
            )
            if not path:
                return
            try:
                text = Path(path).read_text(encoding="utf-8")
            except OSError as e:
                QMessageBox.critical(self, "Error", str(e))
                return
            single = self._single_untitled()
            if single:
                self._load_into(single, path, text)
            else:
                self._new_tab(path, text)
            self._add_recent(path)

        def open_file(self, path: str, content: str | None = None) -> None:
            if content is None:
                try:
                    content = Path(path).read_text(encoding="utf-8")
                except OSError:
                    content = None
            self._new_tab(path, content)
            self._add_recent(path)

        def _save_file(self) -> None:
            ed = self._current_editor()
            if ed and self._save_ed(ed):
                p = ed.property("path") or ""
                if p:
                    self._add_recent(str(p))

        def _save_file_as(self) -> None:
            ed = self._current_editor()
            if ed:
                self._save_ed(ed, save_as=True)

        def _save_ed(self, ed: CodeEditor, save_as: bool = False) -> bool:
            path = ed.property("path") or ""
            if not path or save_as:
                path, _ = QFileDialog.getSaveFileName(
                    self, "Save .gom", os.getcwd(),
                    "Gulf of Mexico (*.gom);;All Files (*)",
                )
                if not path:
                    return False
                ed.setProperty("path", path)
                self.tabs.setTabText(self.tabs.indexOf(ed), Path(path).name)
            try:
                Path(path).write_text(ed.toPlainText(), encoding="utf-8")
                ed.document().setModified(False)
                self._on_modified(ed, False)
                return True
            except OSError as e:
                QMessageBox.critical(self, "Error", str(e))
                return False

        # ── Execution ─────────────────────────────────────────

        def _run_current(self) -> None:
            ed = self._current_editor()
            if not ed:
                return
            code = ed.toPlainText()
            path = ed.property("path") or "__ide_buffer__"
            timeout = int(self._settings.get("run_timeout", 30))
            self.console.clear()
            self.thread = QThread(self)
            self.worker = Worker(code, str(path), timeout=timeout)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self._run_done)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.statusBar().showMessage("⏳ Running…")
            self.thread.start()

        def _run_done(self, out: str, err: str) -> None:
            if out:
                self.console.append(out.rstrip("\n"))
            if err:
                self.console.append(_format_error_html(err, self._theme))
            self.statusBar().showMessage("✓ Ready")
            self.var_inspector.update_variables(self.session)

        def _stop_current(self) -> None:
            if self.worker:
                self.worker.kill()
                self.statusBar().showMessage("■ Stopped")

        def run_current(self) -> None:
            self._run_current()

        # ── Modified indicator ────────────────────────────────

        def _on_modified(self, ed: CodeEditor, modified: bool) -> None:
            idx = self.tabs.indexOf(ed)
            if idx == -1:
                return
            path = ed.property("path") or "untitled.gom"
            name = Path(path).name
            self.tabs.setTabText(idx, ("● " + name) if modified else name)

        # ── Toolbar ───────────────────────────────────────────

        def _build_toolbar(self) -> None:
            tb = self._toolbar

            def _tb_btn(text: str, tip: str, slot, obj_name: str = "") -> QToolButton:
                btn = QToolButton()
                btn.setText(text)
                btn.setToolTip(tip)
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
                if obj_name:
                    btn.setObjectName(obj_name)
                btn.clicked.connect(slot)
                return btn

            tb.addWidget(_tb_btn("  New  ", "New File  (Ctrl+N)", lambda: self._new_tab()))
            tb.addWidget(_tb_btn("  Open  ", "Open File  (Ctrl+O)", self._open_file))
            tb.addWidget(_tb_btn("  Save  ", "Save  (Ctrl+S)", self._save_file))
            tb.addSeparator()

            run_btn = _tb_btn("  ▶ Run  ", "Run Code  (F5)", self._run_current, "runButton")
            run_btn.setStyleSheet(
                f"QToolButton {{ background: {self._theme['success']}; color: #fff; "
                f"font-weight: bold; border-radius: 6px; padding: 6px 16px; border: none; }}"
                f"QToolButton:hover {{ background: {self._theme['success']}; opacity: 0.9; }}"
            )
            tb.addWidget(run_btn)

            stop_btn = _tb_btn("  ■ Stop  ", "Stop Execution  (Shift+F5)", self._stop_current, "stopButton")
            stop_btn.setStyleSheet(
                f"QToolButton {{ background: {self._theme['error']}; color: #fff; "
                f"font-weight: bold; border-radius: 6px; padding: 6px 16px; border: none; }}"
                f"QToolButton:hover {{ background: {self._theme['error']}; opacity: 0.9; }}"
            )
            tb.addWidget(stop_btn)

            tb.addSeparator()
            tb.addWidget(_tb_btn("  ⚙ Settings  ", "Settings  (Ctrl+,)", self._open_settings))

        # ── Menu construction ─────────────────────────────────

        def _build_menus(self) -> None:
            mb = self.menuBar()

            # ── File ──
            fm = mb.addMenu("File")
            self._open_recent_menu = fm.addMenu("Open Recent")

            self._add_action(fm, "New",       "Ctrl+N",       lambda: self._new_tab())
            self._add_action(fm, "Open…",     "Ctrl+O",       self._open_file)
            fm.addSeparator()
            self._add_action(fm, "Save",      "Ctrl+S",       self._save_file)
            self._add_action(fm, "Save As…",  "Ctrl+Shift+S", self._save_file_as)
            fm.addSeparator()
            self._add_action(fm, "Settings…", "Ctrl+,",       self._open_settings)
            fm.addSeparator()
            self._add_action(fm, "Exit",      "Ctrl+Q",       self.close)
            self._refresh_recent_menu()

            # ── Edit ──
            em = mb.addMenu("Edit")
            self._add_action(em, "Undo",           "Ctrl+Z",       self._undo)
            self._add_action(em, "Redo",           "Ctrl+Shift+Z", self._redo)
            em.addSeparator()
            self._add_action(em, "Cut",            "Ctrl+X",       self._cut)
            self._add_action(em, "Copy",           "Ctrl+C",       self._copy)
            self._add_action(em, "Paste",          "Ctrl+V",       self._paste)
            self._add_action(em, "Select All",     "Ctrl+A",       self._select_all)
            em.addSeparator()
            self._add_action(em, "Find…",          "Ctrl+F",       self.find_bar.show_find)
            self._add_action(em, "Replace…",       "Ctrl+H",       self.find_bar.show_replace)
            em.addSeparator()
            self._add_action(em, "Toggle Comment", "Ctrl+/",       self._toggle_comment)

            # ── View ──
            vm = mb.addMenu("View")
            self._add_action(vm, "Zoom In",        "Ctrl+=", self._zoom_in)
            self._add_action(vm, "Zoom Out",       "Ctrl+-", self._zoom_out)
            self._add_action(vm, "Reset Zoom",     "Ctrl+0", self._zoom_reset)
            vm.addSeparator()
            act_tb = QAction("Toolbar", self)
            act_tb.setCheckable(True)
            act_tb.setChecked(self._toolbar.isVisible())
            act_tb.triggered.connect(lambda v: self._toolbar.setVisible(v))
            vm.addAction(act_tb)
            act_console = QAction("Console", self)
            act_console.setCheckable(True)
            act_console.setChecked(True)
            act_console.triggered.connect(lambda v: self._console_dock.setVisible(v))
            vm.addAction(act_console)
            act_vars = QAction("Variables", self)
            act_vars.setCheckable(True)
            act_vars.setChecked(True)
            act_vars.triggered.connect(lambda v: self.var_inspector.setVisible(v))
            vm.addAction(act_vars)

            # ── Run ──
            rm = mb.addMenu("Run")
            self._add_action(rm, "Run",           "F5",       self._run_current)
            self._add_action(rm, "Stop",          "Shift+F5", self._stop_current)
            rm.addSeparator()
            self._add_action(rm, "Clear Console", "Ctrl+L",   self._clear_console)

            # ── Help ──
            hm = mb.addMenu("Help")
            self._add_action(hm, "Keyboard Shortcuts", "", self._show_shortcuts)
            self._add_action(hm, "About",              "", self._show_about)

        def _add_action(self, menu, text, shortcut, slot) -> QAction:
            act = QAction(text, self)
            if shortcut:
                act.setShortcut(shortcut)
            act.triggered.connect(slot)
            menu.addAction(act)
            return act

        # ── Edit actions ──────────────────────────────────────

        def _undo(self):
            ed = self._current_editor()
            if ed: ed.undo()

        def _redo(self):
            ed = self._current_editor()
            if ed: ed.redo()

        def _cut(self):
            ed = self._current_editor()
            if ed: ed.cut()

        def _copy(self):
            ed = self._current_editor()
            if ed: ed.copy()

        def _paste(self):
            ed = self._current_editor()
            if ed: ed.paste()

        def _select_all(self):
            ed = self._current_editor()
            if ed: ed.selectAll()

        def _toggle_comment(self):
            ed = self._current_editor()
            if ed: ed.toggle_comment()

        # ── Zoom ──────────────────────────────────────────────

        def _zoom_in(self):
            ed = self._current_editor()
            if ed:
                ed.zoom_in()
                self._update_zoom_label(ed)

        def _zoom_out(self):
            ed = self._current_editor()
            if ed:
                ed.zoom_out()
                self._update_zoom_label(ed)

        def _zoom_reset(self):
            ed = self._current_editor()
            if ed:
                ed.zoom_reset()
                self._update_zoom_label(ed)

        # ── Save prompts ──────────────────────────────────────

        def _maybe_save(self, ed: CodeEditor) -> bool:
            if not ed.document().isModified():
                return True
            name = Path(ed.property("path") or "untitled.gom").name
            mb = QMessageBox(self)
            mb.setIcon(QMessageBox.Icon.Warning)
            mb.setText(f"Save changes to {name}?")
            mb.setStandardButtons(
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel
            )
            choice = mb.exec()
            if choice == QMessageBox.StandardButton.Save:
                return self._save_ed(ed)
            return choice == QMessageBox.StandardButton.Discard

        def closeEvent(self, event) -> None:  # noqa: N802
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, CodeEditor) and not self._maybe_save(w):
                    event.ignore()
                    return
            self._save_session()
            super().closeEvent(event)

        def _clear_console(self) -> None:
            self.console.clear()

        # ── Console context menu ──────────────────────────────

        def _console_ctx_menu(self, pos) -> None:
            menu = QMenu(self)
            self._add_action(menu, "Copy All",       "", self._console_copy_all)
            self._add_action(menu, "Save Output…",   "", self._console_save)
            menu.addSeparator()
            self._add_action(menu, "Clear",           "", self._clear_console)
            menu.exec(self.console.mapToGlobal(pos))

        def _console_copy_all(self) -> None:
            QGuiApplication.clipboard().setText(self.console.toPlainText())

        def _console_save(self) -> None:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Output", os.getcwd(),
                "Text Files (*.txt);;All Files (*)",
            )
            if path:
                try:
                    Path(path).write_text(self.console.toPlainText(), encoding="utf-8")
                except OSError as e:
                    QMessageBox.critical(self, "Error", str(e))

        # ── Recent files ──────────────────────────────────────

        def _add_recent(self, path: str) -> None:
            try:
                p = str(Path(path).resolve())
            except (OSError, RuntimeError, ValueError):
                p = path
            if p in self.recent_files:
                self.recent_files.remove(p)
            self.recent_files.insert(0, p)
            self.recent_files = self.recent_files[:10]
            self._refresh_recent_menu()
            self._save_recent_to_disk()

        def _refresh_recent_menu(self) -> None:
            if not self._open_recent_menu:
                return
            self._open_recent_menu.clear()
            if not self.recent_files:
                act = QAction("(empty)", self)
                act.setEnabled(False)
                self._open_recent_menu.addAction(act)
                return
            for p in self.recent_files:
                act = QAction(Path(p).name, self)
                act.setToolTip(p)
                act.triggered.connect(partial(self._open_recent, p))
                self._open_recent_menu.addAction(act)
            self._open_recent_menu.addSeparator()
            clr = QAction("Clear List", self)
            clr.triggered.connect(self._clear_recent)
            self._open_recent_menu.addAction(clr)

        def _clear_recent(self) -> None:
            self.recent_files.clear()
            self._refresh_recent_menu()
            self._save_recent_to_disk()

        def _open_recent(self, path: str) -> None:
            try:
                text = Path(path).read_text(encoding="utf-8")
            except OSError as e:
                QMessageBox.critical(self, "Error", str(e))
                return
            single = self._single_untitled()
            if single:
                self._load_into(single, path, text)
            else:
                self._new_tab(path, text)

        def _single_untitled(self) -> CodeEditor | None:
            if self.tabs.count() != 1:
                return None
            w = self.tabs.currentWidget()
            if not isinstance(w, CodeEditor):
                return None
            if (w.property("path") or "") or w.document().isModified():
                return None
            return w

        def _load_into(self, ed: CodeEditor, path: str, text: str) -> None:
            ed.setPlainText(text)
            ed.setProperty("path", path)
            idx = self.tabs.indexOf(ed)
            if idx != -1:
                self.tabs.setTabText(idx, Path(path).name)
            ed.document().setModified(False)
            self._on_modified(ed, False)

        # ── Help dialogs ──────────────────────────────────────

        def _show_shortcuts(self) -> None:
            text = (
                "<h3>Keyboard Shortcuts</h3>"
                "<table cellpadding='4'>"
                "<tr><td><b>F5</b></td><td>Run code</td></tr>"
                "<tr><td><b>Shift+F5</b></td><td>Stop execution</td></tr>"
                "<tr><td><b>Ctrl+N</b></td><td>New file</td></tr>"
                "<tr><td><b>Ctrl+O</b></td><td>Open file</td></tr>"
                "<tr><td><b>Ctrl+S</b></td><td>Save</td></tr>"
                "<tr><td><b>Ctrl+Shift+S</b></td><td>Save As</td></tr>"
                "<tr><td><b>Ctrl+,</b></td><td>Settings</td></tr>"
                "<tr><td><b>Ctrl+F</b></td><td>Find</td></tr>"
                "<tr><td><b>Ctrl+H</b></td><td>Find & Replace</td></tr>"
                "<tr><td><b>Ctrl+/</b></td><td>Toggle comment</td></tr>"
                "<tr><td><b>Ctrl+=</b></td><td>Zoom in</td></tr>"
                "<tr><td><b>Ctrl+-</b></td><td>Zoom out</td></tr>"
                "<tr><td><b>Ctrl+0</b></td><td>Reset zoom</td></tr>"
                "<tr><td><b>Ctrl+L</b></td><td>Clear console</td></tr>"
                "<tr><td><b>Ctrl+Q</b></td><td>Quit</td></tr>"
                "</table>"
            )
            QMessageBox.information(self, "Keyboard Shortcuts", text)

        def _show_about(self) -> None:
            QMessageBox.about(
                self,
                "About Gulf of Mexico IDE",
                "<h3>Gulf of Mexico IDE</h3>"
                "<p>A polished development environment for the "
                "Gulf of Mexico esoteric language.</p>"
                "<p>Features multi-theme support, bracket matching, "
                "indent guides, auto-completion, and more.</p>"
                f"<p><small>Qt: {_get_qt_version()}</small></p>",
            )

        # ── Persistence ───────────────────────────────────────

        def _load_settings_from_disk(self) -> None:
            try:
                if self._settings_path.exists():
                    raw = json.loads(self._settings_path.read_text(encoding="utf-8"))
                    if isinstance(raw, dict):
                        self._settings.update(raw)
            except (OSError, ValueError, json.JSONDecodeError):
                pass

        def _save_settings_to_disk(self) -> None:
            try:
                self._settings_path.parent.mkdir(parents=True, exist_ok=True)
                self._settings_path.write_text(
                    json.dumps(self._settings, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except OSError:
                pass

        def _load_recent_from_disk(self) -> None:
            try:
                if self._recent_path.exists():
                    data = json.loads(self._recent_path.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        self.recent_files = [str(x) for x in data][:10]
            except (OSError, ValueError, json.JSONDecodeError):
                self.recent_files = []

        def _save_recent_to_disk(self) -> None:
            try:
                self._recent_path.parent.mkdir(parents=True, exist_ok=True)
                self._recent_path.write_text(
                    json.dumps(self.recent_files, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except OSError:
                pass

        def _restore_session(self) -> None:
            s = self._settings
            sz = s.get("window_size")
            if isinstance(sz, list) and len(sz) == 2:
                self.resize(int(sz[0]), int(sz[1]))
            pos = s.get("window_pos")
            if isinstance(pos, list) and len(pos) == 2:
                self.move(int(pos[0]), int(pos[1]))

            files = s.get("open_files")
            if isinstance(files, list) and files:
                first = True
                for p in files:
                    try:
                        text = Path(str(p)).read_text(encoding="utf-8")
                    except OSError:
                        continue
                    if first:
                        single = self._single_untitled()
                        if single:
                            self._load_into(single, str(p), text)
                        else:
                            self._new_tab(str(p), text)
                        first = False
                    else:
                        self._new_tab(str(p), text)
                active = s.get("active_index")
                if isinstance(active, int) and 0 <= active < self.tabs.count():
                    self.tabs.setCurrentIndex(active)

        def _save_session(self) -> None:
            open_files = []
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, CodeEditor):
                    p = w.property("path") or ""
                    if p:
                        open_files.append(str(p))
            self._settings["window_size"] = [self.width(), self.height()]
            self._settings["window_pos"] = [self.x(), self.y()]
            self._settings["open_files"] = open_files
            self._settings["active_index"] = self.tabs.currentIndex()
            self._save_settings_to_disk()
            self._save_recent_to_disk()


def _get_qt_version() -> str:
    try:
        from gulfofmexico.ide.qt_compat import QT_VERSION
        return QT_VERSION
    except Exception:
        return "unknown"


# ══════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════

def run(open_files: list[str] | None = None, run_on_open: bool = False) -> None:
    if not PYSIDE_AVAILABLE:
        raise RuntimeError(
            "PySide6 is not installed.  Install with 'pip install PySide6' "
            "or enable the optional extra: poetry install -E ide."
        )
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Gulf of Mexico IDE")
    win = MainWindow()
    if open_files:
        for p in open_files:
            try:
                text = Path(p).read_text(encoding="utf-8")
            except OSError:
                text = None
            win.open_file(p, text)
    win.show()
    if run_on_open:
        QTimer.singleShot(0, win.run_current)
    app.exec()
