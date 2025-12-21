"""Qt compatibility layer - allows IDE to work with either PySide6 or PyQt5"""

try:
    # Try PySide6 first
    from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
    from PySide6.QtGui import QAction, QGuiApplication
    from PySide6.QtWidgets import (
        QApplication,
        QDockWidget,
        QFileDialog,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_VERSION = "PySide6"

except ImportError:
    # Fall back to PyQt5
    from PyQt5.QtCore import Qt, QThread, Signal, QObject, QTimer
    from PyQt5.QtWidgets import (
        QApplication,
        QFileDialog,
        QInputDialog,
        QLabel,
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
    from PyQt5.QtGui import QGuiApplication

    QT_VERSION = "PyQt5"

print(f"Gulf of Mexico IDE using {QT_VERSION}")
