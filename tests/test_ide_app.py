# test helpers use monkeypatch and threading
import threading

import pytest

import gulfofmexico.ide.app as app


def test_format_error_html_escapes():
    html = app._format_error_html('<bad>&"')
    assert "&lt;bad&gt;" in html
    assert "&amp;" in html
    assert "#e06c75" in html
    assert "<pre" in html


def test_is_port_open_true(monkeypatch):
    class DummySock:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_conn(addr, timeout=0.3):
        return DummySock()

    monkeypatch.setattr(app.socket, "create_connection", fake_conn)
    assert app.is_port_open(12345) is True


def test_is_port_open_false(monkeypatch):
    def fake_conn(addr, timeout=0.3):
        raise OSError("nope")

    monkeypatch.setattr(app.socket, "create_connection", fake_conn)
    assert app.is_port_open(12345) is False


@pytest.mark.skipif(not hasattr(app, "MainWindow"), reason="Qt not available")
def test_open_web_ide_opens_existing(monkeypatch):
    # Simulate a server already running on port 8080
    def fake_conn(addr, timeout=0.3):
        class S:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        return S()

    monkeypatch.setattr(app.socket, "create_connection", fake_conn)

    opened = {}

    def fake_browser(url):
        opened["url"] = url

    monkeypatch.setattr("webbrowser.open", fake_browser)

    class Dummy:
        def __init__(self):
            self.msg = None

        def statusBar(self):
            return self

        def showMessage(self, msg):
            self.msg = msg

    dummy = Dummy()
    # call the unbound method
    app.MainWindow._open_web_ide(dummy, port=8080)

    assert "http://localhost:8080/ide" == opened["url"]
    assert "Opened existing Web IDE" in dummy.msg


@pytest.mark.skipif(not hasattr(app, "MainWindow"), reason="Qt not available")
def test_open_web_ide_starts_server(monkeypatch):
    # Simulate no server running: create_connection raises
    def fake_conn(addr, timeout=0.3):
        raise OSError("nope")

    monkeypatch.setattr(app.socket, "create_connection", fake_conn)

    called = {}

    def fake_run(port):
        called["started"] = port

    monkeypatch.setattr(app, "run_web_ide", fake_run)

    # Monkeypatch threading.Thread to call target immediately for predictability
    class FakeThread:
        def __init__(self, target=None, daemon=False):
            self.target = target

        def start(self):
            if self.target:
                self.target()

    monkeypatch.setattr(threading, "Thread", FakeThread)

    class Dummy:
        def __init__(self):
            self.msg = None

        def statusBar(self):
            return self

        def showMessage(self, msg):
            self.msg = msg

    dummy = Dummy()
    app.MainWindow._open_web_ide(dummy, port=8080)
    # After patched Thread runs, our fake_run should have been called
    assert called.get("started") == 8080
