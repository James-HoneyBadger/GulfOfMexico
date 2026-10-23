from __future__ import annotations

"""Qt compatibility layer — supports PySide6 (preferred) or PyQt5 fallback."""

try:
    # ---- PySide6 (preferred) ----
    from PySide6.QtCore import (  # noqa: F401
        QByteArray, QDir, QModelIndex, QObject, QRect, QSize,
        QSortFilterProxyModel, QStringListModel, Qt, QThread, QTimer,
        Signal, QPropertyAnimation, QEasingCurve,
    )
    from PySide6.QtGui import (  # noqa: F401
        QAction, QBrush, QColor, QFont, QFontDatabase, QFontMetricsF,
        QGuiApplication, QKeySequence, QPainter, QPalette, QShortcut,
        QSyntaxHighlighter, QTextCharFormat, QTextCursor, QTextFormat, QTextOption,
    )
    from PySide6.QtWidgets import (  # noqa: F401
        QApplication, QCheckBox, QComboBox, QCompleter, QDialog,
        QDialogButtonBox, QDockWidget, QFileDialog, QFileSystemModel,
        QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog,
        QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem,
        QMainWindow, QMenu, QMessageBox, QPlainTextEdit, QPushButton,
        QScrollArea, QSizePolicy, QSpinBox, QSplitter, QStackedWidget,
        QTabWidget, QTextBrowser, QTextEdit, QToolBar, QToolButton, QTreeView,
        QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
    )
    QT_VERSION = "PySide6"

except ImportError:
    # ---- PyQt5 fallback ----
    from PyQt5.QtCore import (  # noqa: F401
        QByteArray, QDir, QModelIndex, QObject, QPropertyAnimation,
        QEasingCurve, QRect, QSize, QSortFilterProxyModel, QStringListModel, Qt, QThread,
        QTimer,
    )
    from PyQt5.QtCore import pyqtSignal as Signal  # noqa: F401
    from PyQt5.QtGui import (  # noqa: F401
        QBrush, QColor, QFont, QFontDatabase, QFontMetricsF,
        QGuiApplication, QKeySequence, QPainter, QPalette, QShortcut,
        QSyntaxHighlighter, QTextCharFormat, QTextFormat, QTextOption,
    )
    from PyQt5.QtWidgets import (  # noqa: F401
        QAction, QApplication, QCheckBox, QComboBox, QCompleter,
        QDialog, QDialogButtonBox, QDockWidget, QFileDialog,
        QFileSystemModel, QFormLayout, QFrame, QGridLayout, QGroupBox,
        QHBoxLayout, QHeaderView, QLabel, QLineEdit, QListWidget,
        QListWidgetItem, QMainWindow, QMenu, QMessageBox, QPlainTextEdit,
        QPushButton, QScrollArea, QSizePolicy, QSpinBox, QSplitter,
        QStackedWidget, QTabWidget, QTextBrowser, QTextEdit, QToolBar, QToolButton,
        QTreeView, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
    )
    QT_VERSION = "PyQt5"
