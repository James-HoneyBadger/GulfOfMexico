#!/usr/bin/env python3
"""Remove specific unused imports based on Flake8 output."""
import re
from pathlib import Path


# Map of file paths to unused imports
UNUSED_IMPORTS = {
    "gulfofmexico/async_scheduler.py": [
        ("dataclasses", "field"),
        ("gulfofmexico.builtin", "GulfOfMexicoValue"),
    ],
    "gulfofmexico/interpreter.py": [
        ("", "sys"),
        ("", "locale"),
        ("time", "sleep"),
        ("threading", "Thread"),
        ("gulfofmexico.base", "NonFormattedError"),
    ],
    "gulfofmexico/ide/__main__.py": [
        ("", "sys"),
    ],
    "gulfofmexico/ide/app.py": [
        ("gulfofmexico.ide.qt_compat", "QT_VERSION"),
    ],
    "gulfofmexico/ide/web_ide.py": [
        ("", "os"),
    ],
    "gulfofmexico/ide/qt_compat.py": [
        ("PyQt5.QtCore", "Qt"),
        ("PyQt5.QtCore", "QThread"),
        ("PyQt5.QtCore", "pyqtSignal as Signal"),
        ("PyQt5.QtCore", "QObject"),
        ("PyQt5.QtCore", "QTimer"),
        ("PyQt5.QtWidgets", "QApplication"),
        ("PyQt5.QtWidgets", "QFileDialog"),
        ("PyQt5.QtWidgets", "QMainWindow"),
        ("PyQt5.QtWidgets", "QMessageBox"),
        ("PyQt5.QtWidgets", "QDockWidget"),
        ("PyQt5.QtWidgets", "QWidget"),
        ("PyQt5.QtWidgets", "QVBoxLayout"),
        ("PyQt5.QtWidgets", "QHBoxLayout"),
        ("PyQt5.QtWidgets", "QPushButton"),
        ("PyQt5.QtWidgets", "QTextEdit"),
        ("PyQt5.QtWidgets", "QTabWidget"),
        ("PyQt5.QtWidgets", "QMenu"),
        ("PyQt5.QtWidgets", "QAction"),
        ("PyQt5.QtGui", "QGuiApplication"),
    ],
    "gulfofmexico/plugin_system.py": [
        ("typing", "Type"),
        ("gulfofmexico.builtin", "BuiltinFunction"),
    ],
    "gulfofmexico/processor/expression_tree.py": [
        ("gulfofmexico.base", "NonFormattedError"),
        ("gulfofmexico.base", "InterpretationError"),
    ],
    "gulfofmexico/engine/core.py": [
        ("gulfofmexico.engine.namespace", "NamespaceManager"),
    ],
    "gulfofmexico/serialize.py": [
        ("", "json"),
        ("gulfofmexico.builtin", "db_str_push"),
        ("gulfofmexico.builtin", "db_list_pop"),
        ("gulfofmexico.builtin", "db_list_push"),
        ("gulfofmexico.builtin", "db_str_pop"),
    ],
    "scripts/run_all_programs.py": [
        ("", "shlex"),
    ],
}


def remove_import_line(lines, module, name):
    """Remove a specific import from the list of lines."""
    new_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue

        stripped = line.strip()

        # Case 1: from module import name
        if module and f"from {module} import" in line:
            if name in line:
                # Check if it's a multi-line import or single
                if "(" in line or ("," in line and name not in line.rstrip(",")):
                    # Multi-import, just remove the specific name
                    line = re.sub(rf",?\s*{re.escape(name)}\s*,?", "", line)
                    line = re.sub(r",\s*,", ",", line)  # Clean up double commas
                    line = re.sub(r"\(\s*,", "(", line)  # Clean up leading comma
                    line = re.sub(r",\s*\)", ")", line)  # Clean up trailing comma
                    if line.strip() not in ["from {} import ()".format(module), ""]:
                        new_lines.append(line)
                else:
                    # Single import, skip the line
                    continue
            else:
                new_lines.append(line)
        # Case 2: import name
        elif not module and stripped == f"import {name}":
            continue
        else:
            new_lines.append(line)

    return new_lines


def main():
    for file_path_str, imports in UNUSED_IMPORTS.items():
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"Skipping {file_path} (not found)")
            continue

        print(f"Processing {file_path}...")

        with open(file_path, "r") as f:
            lines = f.readlines()

        for module, name in imports:
            lines = remove_import_line(lines, module, name)

        with open(file_path, "w") as f:
            f.writelines(lines)

    print("Done!")


if __name__ == "__main__":
    main()
