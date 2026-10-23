"""Tests for the user-facing presentation layer.

Covers the terminal UI primitives (colour policy, diagnostics, tables) plus the
CLI and REPL surfaces that users actually see.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def run_cli(*args: str, env: dict[str, str] | None = None,
            stdin: str | None = None) -> subprocess.CompletedProcess:
    """Run the CLI with a clean environment for deterministic colour output."""
    clean = {k: v for k, v in os.environ.items() if k not in ("NO_COLOR", "FORCE_COLOR")}
    clean.update(env or {})
    return subprocess.run(
        [sys.executable, "-m", "gulfofmexico", *args],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(ROOT),
        env=clean,
        input=stdin,
    )


# ---------------------------------------------------------------------------
# Terminal primitives
# ---------------------------------------------------------------------------

class TestColorPolicy:
    def test_no_color_disables_ansi(self, monkeypatch):
        from gulfofmexico import ui

        monkeypatch.setenv("NO_COLOR", "1")
        assert ui.paint("x", "red") == "x"

    def test_force_color_enables_ansi(self, monkeypatch):
        from gulfofmexico import ui

        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("FORCE_COLOR", "1")
        assert "\x1b[" in ui.paint("x", "red")

    def test_dumb_terminal_disables_ansi(self, monkeypatch):
        from gulfofmexico import ui

        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        monkeypatch.setenv("TERM", "dumb")
        assert not ui.color_enabled(sys.stdout)


class TestDiagnosticRendering:
    def test_layout_aligns_caret_under_token(self):
        from gulfofmexico.ui import Diagnostic, render_diagnostic

        text = render_diagnostic(
            Diagnostic(
                message="cannot reassign a constant",
                filename="demo.gom",
                line=2,
                column=1,
                length=4,
                source_line="name = \"Lu\"!",
            )
        )
        lines = ANSI.sub("", text).splitlines()
        assert lines[0] == "error: cannot reassign a constant"
        assert lines[1] == "  --> demo.gom:2:1"
        assert lines[2] == "  |"
        assert lines[3] == "2 | name = \"Lu\"!"
        assert lines[4] == "  | ^^^^"

    def test_hint_aligns_with_gutter(self):
        from gulfofmexico.ui import Diagnostic, render_diagnostic

        text = ANSI.sub("", render_diagnostic(
            Diagnostic(
                message="boom", filename="a.gom", line=7,
                column=3, source_line="   x", hint="try something else",
            )
        ))
        assert "  = hint: try something else" in text

    def test_out_of_range_line_does_not_crash(self):
        from gulfofmexico.base import raise_error_at_token, InterpretationError
        from gulfofmexico.base import Token, TokenType

        with pytest.raises(InterpretationError):
            raise_error_at_token(
                "x.gom", "only one line",
                "bad token", Token(TokenType.NAME, "tok", 99, 3),
            )


class TestStructureHelpers:
    def test_table_aligns_columns(self):
        from gulfofmexico.ui import table

        rendered = ANSI.sub("", table(
            [(":help", "show help"), (":quit", "exit")],
            header=("command", "meaning"),
        ))
        lines = rendered.splitlines()
        assert lines[0].startswith("command")
        assert "show help" in lines[2]
        # The second column starts at the same offset on every row.
        assert lines[2].index("show help") == lines[3].index("exit")

    def test_kv_block_pads_keys(self):
        from gulfofmexico.ui import kv_block

        rendered = ANSI.sub("", kv_block([("a", "1"), ("long", "2")], indent=0))
        assert rendered.splitlines()[0].startswith("a     1")

    def test_bullet_list(self):
        from gulfofmexico.ui import bullet_list

        assert ANSI.sub("", bullet_list(["one", "two"])).splitlines()[1] == "  • two"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class TestCliSurface:
    def test_version_flag(self):
        result = run_cli("--version")
        assert result.returncode == 0
        assert re.fullmatch(r"gom \d+\.\d+\.\d+\n", result.stdout)

    def test_short_version_flag(self):
        assert run_cli("-V").stdout.startswith("gom ")

    def test_help_is_grouped(self):
        result = run_cli("--help")
        assert result.returncode == 0
        for section in ("usage:", "running code:", "output:", "modes:", "environment:"):
            assert section in result.stdout

    def test_help_mentions_no_color(self):
        assert "--no-color" in run_cli("--help").stdout

    def test_help_is_plain_when_piped(self):
        assert not ANSI.search(run_cli("--help").stdout)

    def test_missing_file_reports_error_and_hint(self):
        result = run_cli("definitely-not-here.gom")
        assert result.returncode == 1
        assert result.stderr.startswith("error: ")
        assert "hint:" in result.stderr

    def test_directory_argument_is_rejected(self):
        result = run_cli("examples")
        assert result.returncode == 1
        assert "is a directory" in result.stderr

    def test_runtime_error_uses_compiler_layout(self):
        result = run_cli("-c", 'const const n = 1!\nn = 2!')
        assert result.returncode == 1
        assert result.stderr.splitlines()[0].startswith("error: ")
        assert "--> __inline__:2:1" in result.stderr
        assert "^" in result.stderr

    def test_errors_are_plain_when_piped(self):
        result = run_cli("-c", "n = 2!")
        assert not ANSI.search(result.stderr)

    def test_forced_color_emits_ansi(self):
        result = run_cli("-c", "n = 2!", env={"FORCE_COLOR": "1"})
        assert ANSI.search(result.stderr)

    def test_no_color_flag_wins_over_force(self):
        result = run_cli("--no-color", "-c", "n = 2!", env={"FORCE_COLOR": "1"})
        assert not ANSI.search(result.stderr)

    def test_successful_run_is_silent_and_exits_zero(self):
        result = run_cli("-c", "print(1)!")
        assert result.returncode == 0
        assert result.stdout == "1\n"
        assert result.stderr == ""

    def test_verbose_reports_timing(self):
        result = run_cli("examples/01_hello_world.gom", env={"GULFOFMEXICO_VERBOSE": "1"})
        assert result.returncode == 0
        assert re.search(r"Code has finished executing in \d+ ms\.", result.stdout)

    def test_broken_pipe_is_silent(self):
        """Closing the reader early (``| head``) must not report an error."""
        result = subprocess.run(
            f"{sys.executable} -m gulfofmexico examples/23_algorithms.gom | head -2",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(ROOT),
        )
        assert result.returncode == 0
        assert result.stderr.strip() == ""

    def test_language_errors_do_not_dump_internal_debug(self):
        result = run_cli("-c", 'print "a"!\nbad = 1!')
        assert result.returncode == 1
        assert "error:" in result.stderr
        assert "[DB_PRINT]" not in result.stderr

    def test_vars_json_snapshot(self, tmp_path):
        snapshot = tmp_path / "vars.json"
        result = run_cli(
            "examples/47_type_annotations.gom", "--vars-json", str(snapshot)
        )
        assert result.returncode == 0
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
        names = {row["name"]: row for row in payload}
        assert names["pi"]["value"] == "3.14159"
        assert names["pi"]["type"] == "Number"
        assert names["nums"]["type"] == "List"
        # Built-ins and keywords are not reported.
        assert "print" not in names and "true" not in names

    def test_quiet_suppresses_verbose(self):
        result = run_cli(
            "examples/01_hello_world.gom",
            "-q",
            env={"GULFOFMEXICO_VERBOSE": "1"},
        )
        assert result.returncode == 0
        assert "Code has finished executing" not in result.stdout


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

class TestReplSurface:
    def test_banner_shows_product_and_version(self):
        result = run_cli(stdin=":quit\n", env={"NO_COLOR": "1"})
        assert result.returncode == 0
        assert "Gulf of Mexico" in result.stdout
        assert re.search(r"v\d+\.\d+\.\d+", result.stdout)
        assert ":help" in result.stdout

    def test_help_lists_commands_and_language_hints(self):
        result = run_cli(stdin=":help\n:quit\n", env={"NO_COLOR": "1"})
        assert "Commands" in result.stdout
        assert "Writing code" in result.stdout
        assert ":load <file>" in result.stdout

    def test_vars_table(self):
        result = run_cli(stdin='const const total = 42!\n:vars\n:quit\n', env={
            "NO_COLOR": "1", "GULFMEXICO_SKIP_GLOBALS": "1",
        })
        assert "name" in result.stdout and "value" in result.stdout
        assert "total" in result.stdout
        assert "Number" in result.stdout

    def test_result_is_rendered_as_a_value_not_a_repr(self):
        result = run_cli(stdin="2 + 3!\n:quit\n", env={"NO_COLOR": "1"})
        assert "5" in result.stdout
        assert "GulfOfMexico" not in result.stdout

    def test_errors_go_to_stderr(self):
        result = run_cli(stdin="n = 1!\n:quit\n", env={"NO_COLOR": "1"})
        assert "error:" in result.stderr
        assert "Attempted to set" in result.stderr

    def test_quit_prints_farewell(self):
        result = run_cli(stdin=":quit\n", env={"NO_COLOR": "1"})
        assert "bye." in result.stdout

    def test_reset_acknowledges(self):
        result = run_cli(stdin=":reset\n:quit\n", env={"NO_COLOR": "1"})
        assert "state reset" in result.stdout.lower()
