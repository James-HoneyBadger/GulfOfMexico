from __future__ import annotations

import os
from pathlib import Path
import json
from functools import partial

# Use compatibility layer for Qt
try:
    from gulfofmexico.ide.qt_compat import (
        Qt,
        QThread,
        Signal,
        QObject,
        QTimer,
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
        QAction,
        QGuiApplication,
        QMenu,
        QT_VERSION,
    )

    PYSIDE_AVAILABLE = True
except ImportError as e:
    PYSIDE_AVAILABLE = False
    print(f"Qt not available: {e}")
    print("Install with: pip install PySide6 or pip install PyQt5")

from gulfofmexico.ide.runner import ExecutionSession, run_code

if PYSIDE_AVAILABLE:
    # Local imports only when GUI libs are present
    from gulfofmexico.ide.editor import CodeEditor
    from gulfofmexico.ide.highlighter import GomHighlighter


if PYSIDE_AVAILABLE:

    class Worker(QObject):
        finished = Signal(str, str)  # stdout, error

        def __init__(
            self,
            session: ExecutionSession,
            code: str,
            filename: str,
        ) -> None:
            super().__init__()
            self.session = session
            self.code = code
            self.filename = filename

        def run(self) -> None:  # noqa: D401
            out, err = run_code(self.session, self.code, self.filename)
            self.finished.emit(out, err or "")

    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Gulf of Mexico IDE")
            self.resize(1100, 800)

            self.session = ExecutionSession()
            self.thread: QThread | None = None
            self.worker: Worker | None = None

            self.tabs = QTabWidget()
            self.tabs.setTabsClosable(True)
            self.tabs.tabCloseRequested.connect(self._close_tab)
            self.setCentralWidget(self.tabs)

            # Console dock
            self.console = QTextEdit()
            self.console.setReadOnly(True)
            self.console.setContextMenuPolicy(Qt.CustomContextMenu)
            self.console.customContextMenuRequested.connect(self._show_console_menu)
            dock = QDockWidget("Console", self)
            dock.setWidget(self.console)
            self.addDockWidget(Qt.BottomDockWidgetArea, dock)

            # Toolbar-like run/save/open/stop/clear
            bar = QWidget()
            bl = QHBoxLayout(bar)
            self.btn_open = QPushButton("Open")
            self.btn_save = QPushButton("Save")
            self.btn_run = QPushButton("Run")
            self.btn_stop = QPushButton("Stop")
            self.btn_clear = QPushButton("Clear Console")
            bl.addWidget(self.btn_open)
            bl.addWidget(self.btn_save)
            bl.addWidget(self.btn_run)
            bl.addWidget(self.btn_stop)
            bl.addWidget(self.btn_clear)
            bl.addStretch(1)
            top = QWidget()
            layout = QVBoxLayout(top)
            layout.addWidget(bar)
            layout.addWidget(self.tabs)
            top.setLayout(layout)
            self.setCentralWidget(top)

            self.btn_open.clicked.connect(self._open_file)
            self.btn_save.clicked.connect(self._save_file)
            self.btn_run.clicked.connect(self._run_current)
            self.btn_stop.clicked.connect(self._stop_current)
            self.btn_clear.clicked.connect(self._clear_console)

            # Status bar and recent files
            self.statusBar().showMessage("Ready")
            self.recent_files: list[str] = []
            self._open_recent_menu = None
            self._recent_path = Path.home() / ".config" / "gom-ide" / "recent.json"
            self._load_recent_from_disk()
            self._settings_path = Path.home() / ".config" / "gom-ide" / "settings.json"
            self._loaded_settings: dict[str, object] | None = None

            # Menus
            self._build_menus()
            # Start with an empty tab
            self._new_tab()
            # Apply any saved settings and restore last session
            self._load_settings_apply()

        def _new_tab(
            self,
            path: str | None = None,
            content: str | None = None,
        ) -> None:
            editor = CodeEditor()
            GomHighlighter(editor.document())
            if content:
                editor.setPlainText(content)
            tab_name = Path(path).name if path else "untitled.gom"
            idx = self.tabs.addTab(editor, tab_name)
            self.tabs.setCurrentIndex(idx)
            editor.setProperty("path", path or "")
            self._connect_modified_signal(editor)

        def _connect_modified_signal(self, editor: "CodeEditor") -> None:
            def _slot(modified: bool) -> None:
                self._on_modified(editor, modified)

            editor.document().modificationChanged.connect(_slot)

        def _current_editor(self) -> CodeEditor | None:
            w = self.tabs.currentWidget()
            return w if isinstance(w, CodeEditor) else None

        def _close_tab(self, index: int) -> None:
            w = self.tabs.widget(index)
            if isinstance(w, CodeEditor):
                if not self._maybe_save_editor(w):
                    return
            self.tabs.removeTab(index)
            if self.tabs.count() == 0:
                self._new_tab()

        def _open_file(self) -> None:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open .gom",
                os.getcwd(),
                "Gulf of Mexico (*.gom)",
            )
            if not path:
                return
            try:
                text = Path(path).read_text(encoding="utf-8")
            except OSError as e:
                QMessageBox.critical(self, "Open Failed", str(e))
                return
            single = self._single_untitled_modified_editor()
            if single is not None:
                if not self._confirm_replace_unsaved(single, path):
                    return
                self._load_file_into_editor(single, path, text)
            else:
                self._new_tab(path, text)
            self._add_recent_file(path)

        def open_file(self, path: str, content: str | None = None) -> None:
            """Open a file programmatically (used by CLI/startup).

            If ``content`` is provided we'll use it; otherwise we attempt to
            read from ``path``. This mirrors the behavior of the public
            File->Open action but without user prompts.
            """
            if content is None:
                try:
                    content = Path(path).read_text(encoding="utf-8")
                except OSError:
                    content = None
            self._new_tab(path, content)
            self._add_recent_file(path)

        def _save_file(self) -> None:
            ed = self._current_editor()
            if not ed:
                return
            if self._save_specific(ed):
                saved_path = ed.property("path") or ""
                if saved_path:
                    self._add_recent_file(str(saved_path))

        def _save_file_as(self) -> None:
            ed = self._current_editor()
            if not ed:
                return
            self._save_specific(ed, save_as=True)

        def _save_specific(
            self,
            ed: "CodeEditor",
            save_as: bool = False,
        ) -> bool:
            path = ed.property("path") or ""
            if not path or save_as:
                path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save .gom",
                    os.getcwd(),
                    "Gulf of Mexico (*.gom)",
                )
                if not path:
                    return False
                ed.setProperty("path", path)
                name = Path(path).name
                self.tabs.setTabText(self.tabs.currentIndex(), name)
            try:
                Path(path).write_text(ed.toPlainText(), encoding="utf-8")
                ed.document().setModified(False)
                self._on_modified(ed, False)
                return True
            except OSError as e:
                QMessageBox.critical(self, "Save Failed", str(e))
                return False

        def _run_current(self) -> None:
            ed = self._current_editor()
            if not ed:
                return
            code = ed.toPlainText()
            path = ed.property("path") or "__ide_buffer__"
            self.console.clear()

            # Worker thread to avoid blocking UI
            self.thread = QThread(self)
            self.worker = Worker(self.session, code, str(path))
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self._run_finished)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.btn_run.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.statusBar().showMessage("Running...")
            self.thread.start()

        def _run_finished(self, out: str, err: str) -> None:
            if out:
                self.console.append(out)
            if err:
                prefix = "<span style='color:# e06c75'>"
                suffix = "</span>"
                self.console.append(prefix + err + suffix)
            self.btn_run.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.statusBar().showMessage("Ready")

        def _stop_current(self) -> None:
            if self.thread and self.thread.isRunning():
                # Best-effort: request interruption; cannot force-stop threads.
                self.thread.requestInterruption()
                self.statusBar().showMessage("Stop requested")

        def run_current(self) -> None:
            """Public wrapper to run the current editor (for CLI).

            Uses the same implementation as the Run button.
            """
            self._run_current()

        def _on_modified(self, ed: "CodeEditor", modified: bool) -> None:
            idx = self.tabs.indexOf(ed)
            if idx == -1:
                return
            path = ed.property("path") or "untitled.gom"
            name = Path(path).name
            if modified:
                name = "*" + name
            self.tabs.setTabText(idx, name)

        def _build_menus(self) -> None:
            mb = self.menuBar()
            file_menu = mb.addMenu("File")
            run_menu = mb.addMenu("Run")
            self._open_recent_menu = file_menu.addMenu("Open Recent")

            act_new = QAction("New", self)
            act_new.setShortcut("Ctrl+N")
            act_new.triggered.connect(self._new_tab)

            act_open = QAction("Open...", self)
            act_open.setShortcut("Ctrl+O")
            act_open.triggered.connect(self._open_file)

            act_save = QAction("Save", self)
            act_save.setShortcut("Ctrl+S")
            act_save.triggered.connect(self._save_file)

            act_save_as = QAction("Save As...", self)
            act_save_as.setShortcut("Ctrl+Shift+S")
            act_save_as.triggered.connect(self._save_file_as)

            act_exit = QAction("Exit", self)
            act_exit.triggered.connect(self.close)

            file_menu.addAction(act_new)
            file_menu.addAction(act_open)
            file_menu.addSeparator()
            file_menu.addAction(act_save)
            file_menu.addAction(act_save_as)
            file_menu.addSeparator()
            file_menu.addAction(act_exit)
            self._refresh_recent_menu()

            act_run = QAction("Run", self)
            act_run.setShortcut("F5")
            act_run.triggered.connect(self._run_current)

            act_stop = QAction("Stop", self)
            act_stop.setShortcut("Shift+F5")
            act_stop.triggered.connect(self._stop_current)

            run_menu.addAction(act_run)
            run_menu.addAction(act_stop)
            act_clear = QAction("Clear Console", self)
            act_clear.setShortcut("Ctrl+L")
            act_clear.triggered.connect(self._clear_console)
            run_menu.addAction(act_clear)

        def _maybe_save_editor(self, ed: "CodeEditor") -> bool:
            if not ed.document().isModified():
                return True
            path = ed.property("path") or "untitled.gom"
            name = Path(path).name
            mbox = QMessageBox(self)
            mbox.setIcon(QMessageBox.Icon.Warning)
            mbox.setText(f"Save changes to {name}?")
            mbox.setStandardButtons(
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel
            )
            choice = mbox.exec()
            if choice == QMessageBox.StandardButton.Save:
                return self._save_specific(ed)
            if choice == QMessageBox.StandardButton.Discard:
                return True
            return False

        def closeEvent(self, event) -> None:  # noqa: N802
            # Prompt to save all modified editors
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, CodeEditor):
                    if not self._maybe_save_editor(w):
                        event.ignore()
                        return
            self._save_settings()
            super().closeEvent(event)

        def _clear_console(self) -> None:
            self.console.clear()

        def _show_console_menu(self, pos) -> None:
            menu = QMenu(self)
            act_copy = QAction("Copy All", self)
            act_save = QAction("Save Output...", self)
            act_clear = QAction("Clear", self)
            act_copy.triggered.connect(self._console_copy_all)
            act_save.triggered.connect(self._console_save_output)
            act_clear.triggered.connect(self._clear_console)
            menu.addAction(act_copy)
            menu.addAction(act_save)
            menu.addSeparator()
            menu.addAction(act_clear)
            menu.exec(self.console.mapToGlobal(pos))

        def _console_copy_all(self) -> None:
            text = self.console.toPlainText()
            QGuiApplication.clipboard().setText(text)

        def _console_save_output(self) -> None:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Console Output",
                os.getcwd(),
                "Text Files (*.txt);;All Files (*)",
            )
            if not path:
                return
            try:
                content = self.console.toPlainText()
                Path(path).write_text(content, encoding="utf-8")
            except OSError as e:
                QMessageBox.critical(self, "Save Failed", str(e))

        def _add_recent_file(self, path: str) -> None:
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
                name = Path(p).name
                act = QAction(name, self)
                act.setToolTip(p)
                act.triggered.connect(partial(self._open_recent, p))
                self._open_recent_menu.addAction(act)
            self._open_recent_menu.addSeparator()
            act_clear = QAction("Clear List", self)
            act_clear.triggered.connect(self._clear_recent)
            self._open_recent_menu.addAction(act_clear)

        def _clear_recent(self) -> None:
            self.recent_files.clear()
            self._refresh_recent_menu()
            self._save_recent_to_disk()

        def _open_recent(self, path: str) -> None:
            try:
                text = Path(path).read_text(encoding="utf-8")
            except OSError as e:
                QMessageBox.critical(self, "Open Failed", str(e))
                return
            single = self._single_untitled_modified_editor()
            if single is not None:
                if not self._confirm_replace_unsaved(single, path):
                    return
                self._load_file_into_editor(single, path, text)
            else:
                self._new_tab(path, text)

        def _single_untitled_modified_editor(self) -> "CodeEditor | None":
            if self.tabs.count() != 1:
                return None
            w = self.tabs.currentWidget()
            if not isinstance(w, CodeEditor):
                return None
            raw = w.property("path") or ""
            if raw:
                return None
            if not w.document().isModified():
                return None
            return w

        def _confirm_replace_unsaved(
            self,
            ed: "CodeEditor",
            new_path: str,
        ) -> bool:
            name = Path(new_path).name
            mbox = QMessageBox(self)
            mbox.setIcon(QMessageBox.Icon.Warning)
            mbox.setText(f"Replace unsaved buffer with {name}?")
            mbox.setStandardButtons(
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel
            )
            choice = mbox.exec()
            if choice == QMessageBox.StandardButton.Save:
                return self._save_specific(ed)
            if choice == QMessageBox.StandardButton.Discard:
                return True
            return False

        def _load_file_into_editor(
            self,
            ed: "CodeEditor",
            path: str,
            text: str,
        ) -> None:
            ed.setPlainText(text)
            ed.setProperty("path", path)
            name = Path(path).name
            idx = self.tabs.indexOf(ed)
            if idx != -1:
                self.tabs.setTabText(idx, name)
            ed.document().setModified(False)
            self._on_modified(ed, False)

        def _load_recent_from_disk(self) -> None:
            try:
                if self._recent_path.exists():
                    raw = self._recent_path.read_text(encoding="utf-8")
                    data = json.loads(raw)
                    if isinstance(data, list):
                        self.recent_files = [str(x) for x in data][:10]
            except (OSError, ValueError, json.JSONDecodeError):
                self.recent_files = []

        def _save_recent_to_disk(self) -> None:
            try:
                self._recent_path.parent.mkdir(parents=True, exist_ok=True)
                payload = json.dumps(
                    self.recent_files,
                    ensure_ascii=False,
                    indent=2,
                )
                self._recent_path.write_text(payload, encoding="utf-8")
            except OSError:
                pass

        def _load_settings_apply(self) -> None:
            try:
                if self._settings_path.exists():
                    raw = self._settings_path.read_text(encoding="utf-8")
                    data = json.loads(raw)
                    if isinstance(data, dict):
                        self._loaded_settings = data
            except (OSError, ValueError, json.JSONDecodeError):
                self._loaded_settings = None

            s = self._loaded_settings or {}
            # Apply window size/position
            size = s.get("size")
            if (
                isinstance(size, list)
                and len(size) == 2
                and all(isinstance(x, int) for x in size)
            ):
                self.resize(int(size[0]), int(size[1]))
            pos = s.get("pos")
            if (
                isinstance(pos, list)
                and len(pos) == 2
                and all(isinstance(x, int) for x in pos)
            ):
                self.move(int(pos[0]), int(pos[1]))

            # Restore last open files
            files = s.get("open_files")
            if isinstance(files, list) and files:
                first = True
                for p in files:
                    try:
                        text = Path(str(p)).read_text(encoding="utf-8")
                    except OSError:
                        continue
                    if first:
                        ed = self._single_untitled_modified_editor()
                        if ed is not None:
                            self._load_file_into_editor(ed, str(p), text)
                        else:
                            self._new_tab(str(p), text)
                        first = False
                    else:
                        self._new_tab(str(p), text)
                active = s.get("active_index")
                if isinstance(active, int) and 0 <= active < self.tabs.count():
                    self.tabs.setCurrentIndex(active)

        def _save_settings(self) -> None:
            open_files: list[str] = []
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, CodeEditor):
                    p = w.property("path") or ""
                    if p:
                        open_files.append(str(p))
            payload = {
                "size": [self.width(), self.height()],
                "pos": [self.x(), self.y()],
                "open_files": open_files,
                "active_index": self.tabs.currentIndex(),
            }
            try:
                self._settings_path.parent.mkdir(parents=True, exist_ok=True)
                text = json.dumps(payload, ensure_ascii=False, indent=2)
                self._settings_path.write_text(text, encoding="utf-8")
            except OSError:
                pass


def run(
    open_files: list[str] | None = None,
    run_on_open: bool = False,
) -> None:
    if not PYSIDE_AVAILABLE:
        raise RuntimeError(
            "PySide6 is not installed. Install with 'pip install PySide6' "
            "or enable the optional extra: poetry install -E ide."
        )
    app = QApplication.instance() or QApplication([])
    win = MainWindow()
    # If the caller supplied files to open on startup, open them now.
    if open_files:
        for p in open_files:
            # Try to read file contents, else open an empty editor
            try:
                text = Path(p).read_text(encoding="utf-8")
            except OSError:
                text = None
            win.open_file(p, text)
    win.show()
    # If requested: run the active editor shortly after entering the event
    # loop. Use QTimer.singleShot(0, ...) to ensure the app is fully shown
    # first.
    if run_on_open:
        QTimer.singleShot(0, win.run_current)
    app.exec()
