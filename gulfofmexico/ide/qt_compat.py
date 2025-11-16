"""Qt compatibility layer - allows IDE to work with either PySide6 or PyQt5"""

try:
    # Try PySide6 first
    from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
    from PySide6.QtWidgets import (
        QApplication,
        QFileDialog,
        QMainWindow,
        QMessageBox,
        QDockWidget,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QPushButton,
        QTextEdit,
        QTabWidget,
        QMenu,
    )
    from PySide6.QtGui import QAction, QGuiApplication

    QT_VERSION = "PySide6"

except ImportError:
    # Fall back to PyQt5
    from PyQt5.QtWidgets import (
        QApplication,
        QFileDialog,
        QMainWindow,
        QMessageBox,
        QDockWidget,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QPushButton,
        QTextEdit,
        QTabWidget,
        QMenu,
        QAction,
    )

    QT_VERSION = "PyQt5"

print(f"Gulf of Mexico IDE using {QT_VERSION}")
