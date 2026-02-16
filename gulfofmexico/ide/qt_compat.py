"""Qt compatibility layer - allows IDE to work with either PySide6 or PyQt5"""

try:
    # Try PySide6 first
    from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal  # noqa: F401
    from PySide6.QtGui import QAction, QGuiApplication  # noqa: F401
    from PySide6.QtWidgets import (  # noqa: F401
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

    QT_VERSION = "PyQt5"

print(f"Gulf of Mexico IDE using {QT_VERSION}")
