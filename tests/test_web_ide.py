import webbrowser

import gulfofmexico.ide.web_ide as web_ide


def test_run_web_ide_opens_browser(monkeypatch):
    opened = {}

    monkeypatch.setattr(webbrowser, "open", lambda url: opened.setdefault("url", url))

    class FakeServer:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def serve_forever(self):
            # Simulate server loop that ends via KeyboardInterrupt
            raise KeyboardInterrupt()

    monkeypatch.setattr(web_ide.socketserver, "TCPServer", lambda *a, **k: FakeServer())
    # Ensure the 'open_browser' thread runs immediately (avoid the internal sleep)

    class FakeThread:
        def __init__(self, target=None, daemon=False):
            self.target = target

        def start(self):
            if self.target:
                self.target()

    monkeypatch.setattr(web_ide.threading, "Thread", FakeThread)

    # Run - should call webbrowser.open with chosen port
    web_ide.run_web_ide(port=57001)
    assert opened.get("url") == "http://localhost:57001/ide"


def test_execute_code_basic_print():
    # Use the class as 'self' — execute_code uses class var workspace_dir
    res = web_ide.GOMWebIDEHandler.execute_code(web_ide.GOMWebIDEHandler, 'print "Hello from test"!')
    assert isinstance(res, dict)
    assert res.get("success") is True
    assert "Hello from test" in res.get("output", "")
