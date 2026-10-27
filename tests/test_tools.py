"""Tests for the static tooling (``gom --check`` / ``gom --fmt``) and stdin mode."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def run_cli(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    """Run the CLI in a clean environment so colour output stays deterministic."""
    clean = {k: v for k, v in os.environ.items() if k not in ("NO_COLOR", "FORCE_COLOR")}
    clean["NO_COLOR"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "gulfofmexico", *args],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(ROOT),
        env=clean,
        input=stdin,
    )


# ---------------------------------------------------------------------------
# format_source
# ---------------------------------------------------------------------------

class TestFormatSource:
    def test_indentation_is_remapped_to_three_space_levels(self):
        from gulfofmexico.tools import format_source

        source = "if true {\n    print(1)!\n        print(2)!\n}\n"
        assert format_source("t.gom", source) == (
            "if true {\n   print(1)!\n      print(2)!\n}\n"
        )

    def test_tabs_become_three_spaces(self):
        from gulfofmexico.tools import format_source

        assert format_source("t.gom", "if true {\n\tprint(1)!\n}\n") == (
            "if true {\n   print(1)!\n}\n"
        )

    def test_trailing_whitespace_and_blank_runs_are_trimmed(self):
        from gulfofmexico.tools import format_source

        source = "\n\nconst x = 1!   \n\n\n\nprint(x)!\n\n\n"
        assert format_source("t.gom", source) == "const x = 1!\n\nprint(x)!\n"

    def test_crlf_is_normalised(self):
        from gulfofmexico.tools import format_source

        assert format_source("t.gom", "const x = 1!\r\nprint(x)!\r\n") == (
            "const x = 1!\nprint(x)!\n"
        )

    def test_empty_source_stays_empty(self):
        from gulfofmexico.tools import format_source

        assert format_source("t.gom", "\n\n  \n") == ""

    def test_multiline_string_body_is_preserved(self):
        from gulfofmexico.tools import format_source

        source = '      const s = """one\n    two\n  three"""!\n'
        formatted = format_source("t.gom", source)
        assert "    two\n  three" in formatted
        assert formatted.startswith("const s =")

    def test_formatting_is_idempotent(self):
        from gulfofmexico.tools import format_source

        messy = "if true {\n        print(1)!\n}\n\n\n"
        once = format_source("t.gom", messy)
        assert format_source("t.gom", once) == once

    def test_already_formatted_source_is_unchanged(self):
        from gulfofmexico.tools import format_source

        source = (ROOT / "examples" / "01_hello_world.gom").read_text(encoding="utf-8")
        assert format_source("01_hello_world.gom", source) == source


# ---------------------------------------------------------------------------
# check_source
# ---------------------------------------------------------------------------

class TestCheckSource:
    def test_counts_top_level_statements(self):
        from gulfofmexico.tools import check_source

        assert check_source("t.gom", "const x = 1!\nprint(x)!\n") == 2

    def test_reports_non_multiple_of_three_indentation(self):
        from gulfofmexico.base import InterpretationError
        from gulfofmexico.tools import check_source

        with pytest.raises(InterpretationError, match="multiple of 3"):
            check_source("t.gom", "if true {\n    print(1)!\n}\n")

    def test_reports_tab_indentation(self):
        from gulfofmexico.base import InterpretationError
        from gulfofmexico.tools import check_source

        with pytest.raises(InterpretationError, match="tabs are not supported"):
            check_source("t.gom", "if true {\n\tprint(1)!\n}\n")

    def test_does_not_execute_the_program(self, capsys):
        from gulfofmexico.tools import check_source

        check_source("t.gom", 'print("should not appear")!\n')
        captured = capsys.readouterr()
        assert "should not appear" not in captured.out
        assert "should not appear" not in captured.err

    def test_checks_each_section_of_a_multi_section_file(self):
        from gulfofmexico.base import InterpretationError
        from gulfofmexico.tools import check_source

        good = "===== a =====\nconst const X = 1!\n===== b =====\nprint(X)!\n"
        assert check_source("t.gom", good) == 2

        bad = "===== a =====\nconst const X = 1!\n===== b =====\nif true {\n    print(X)!\n}\n"
        with pytest.raises(InterpretationError, match="multiple of 3"):
            check_source("t.gom", bad)

    @pytest.mark.parametrize(
        "example",
        sorted((ROOT / "examples").glob("*.gom")),
        ids=lambda path: path.stem,
    )
    def test_every_bundled_example_checks_clean(self, example: Path):
        from gulfofmexico.tools import check_source

        check_source(str(example), example.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

class TestSplitSections:
    def test_file_without_markers_is_one_unnamed_section(self):
        from gulfofmexico.sections import split_sections

        assert split_sections("print(1)!\n") == [(None, "print(1)!\n")]

    def test_preamble_and_named_sections(self):
        from gulfofmexico.sections import split_sections

        sections = split_sections("p!\n===== a =====\nA!\n===== b =====\nB!\n")
        assert sections == [(None, "p!\n"), ("a", "A!\n"), ("b", "B!\n")]

    def test_empty_marker_name_is_unnamed(self):
        from gulfofmexico.sections import split_sections

        assert split_sections("=====\nA!\n") == [(None, ""), (None, "A!\n")]


# ---------------------------------------------------------------------------
# CLI: --check
# ---------------------------------------------------------------------------

class TestCheckFlag:
    def test_clean_file_reports_ok(self, tmp_path: Path):
        target = tmp_path / "ok.gom"
        target.write_text("const x = 1!\nprint(x)!\n", encoding="utf-8")
        result = run_cli("--check", str(target))
        assert result.returncode == 0
        assert "ok (2 statements)" in result.stdout

    def test_broken_file_exits_one_with_a_diagnostic(self, tmp_path: Path):
        target = tmp_path / "bad.gom"
        target.write_text("if true {\n    print(1)!\n}\n", encoding="utf-8")
        result = run_cli("--check", str(target))
        assert result.returncode == 1
        assert "error:" in result.stderr
        assert str(target) in result.stderr

    def test_inline_code_can_be_checked(self):
        result = run_cli("--check", "-c", "const x = 1!")
        assert result.returncode == 0
        assert "<inline>" in result.stdout

    def test_reads_standard_input(self):
        result = run_cli("--check", "-", stdin="const x = 1!\n")
        assert result.returncode == 0
        assert "<stdin>" in result.stdout

    def test_missing_file_is_reported(self, tmp_path: Path):
        result = run_cli("--check", str(tmp_path / "nope.gom"))
        assert result.returncode == 1
        assert "cannot open" in result.stderr

    def test_multiple_files_are_all_checked(self, tmp_path: Path):
        first = tmp_path / "a.gom"
        second = tmp_path / "b.gom"
        first.write_text("const a = 1!\n", encoding="utf-8")
        second.write_text("if true {\n    print(1)!\n}\n", encoding="utf-8")
        result = run_cli("--check", str(first), str(second))
        assert result.returncode == 1
        assert f"{first}: ok" in result.stdout
        assert "multiple of 3" in result.stderr

    def test_no_target_is_a_usage_error(self):
        result = run_cli("--check")
        assert result.returncode == 2
        assert "nothing to work on" in result.stderr


# ---------------------------------------------------------------------------
# CLI: --fmt
# ---------------------------------------------------------------------------

class TestFormatFlag:
    def test_prints_canonical_source_without_touching_the_file(self, tmp_path: Path):
        target = tmp_path / "m.gom"
        target.write_text("if true {\n    print(1)!\n}\n", encoding="utf-8")
        result = run_cli("--fmt", str(target))
        assert result.returncode == 0
        assert result.stdout == "if true {\n   print(1)!\n}\n"
        assert target.read_text(encoding="utf-8") == "if true {\n    print(1)!\n}\n"

    def test_write_rewrites_the_file(self, tmp_path: Path):
        target = tmp_path / "m.gom"
        target.write_text("if true {\n    print(1)!\n}\n", encoding="utf-8")
        result = run_cli("--fmt", "-w", str(target))
        assert result.returncode == 0
        assert "reformatted" in result.stdout
        assert target.read_text(encoding="utf-8") == "if true {\n   print(1)!\n}\n"
        # The rewritten file still runs.
        assert run_cli(str(target)).returncode == 0

    def test_write_reports_when_nothing_changed(self, tmp_path: Path):
        target = tmp_path / "m.gom"
        target.write_text("const x = 1!\n", encoding="utf-8")
        result = run_cli("--fmt", "-w", str(target))
        assert result.returncode == 0
        assert "already formatted" in result.stdout

    def test_write_requires_a_file(self):
        result = run_cli("--fmt", "-w", "-c", "const x = 1!")
        assert result.returncode == 2
        assert "--write needs a file" in result.stderr

    def test_write_without_fmt_is_a_usage_error(self, tmp_path: Path):
        target = tmp_path / "m.gom"
        target.write_text("const x = 1!\n", encoding="utf-8")
        result = run_cli("-w", str(target))
        assert result.returncode == 2
        assert "--write needs --fmt" in result.stderr

    def test_format_and_check_gates_on_canonical_layout(self, tmp_path: Path):
        target = tmp_path / "m.gom"
        target.write_text("if true {\n    print(1)!\n}\n", encoding="utf-8")
        result = run_cli("--check", "--fmt", str(target))
        assert result.returncode == 1
        assert "not formatted" in result.stderr

        assert run_cli("--fmt", "-w", str(target)).returncode == 0
        result = run_cli("--check", "--fmt", str(target))
        assert result.returncode == 0
        assert "formatted" in result.stdout
        assert "ok (1 statement)" in result.stdout


# ---------------------------------------------------------------------------
# Stdin execution mode
# ---------------------------------------------------------------------------

class TestStdinMode:
    def test_program_is_read_from_standard_input(self):
        result = run_cli("-", stdin='print("from stdin")!\n')
        assert result.returncode == 0
        assert "from stdin" in result.stdout

    def test_errors_name_the_stdin_source(self):
        result = run_cli("-", stdin="if true {\n    print(1)!\n}\n")
        assert result.returncode == 1
        assert "<stdin>" in result.stderr


# ---------------------------------------------------------------------------
# Packaging metadata
# ---------------------------------------------------------------------------

class TestPackaging:
    def test_package_ships_a_py_typed_marker(self):
        assert (ROOT / "gulfofmexico" / "py.typed").is_file()

    def test_ruff_ruleset_is_pinned(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert 'select = ["E4", "E7", "E9", "F"]' in pyproject
        assert 'target-version = "py311"' in pyproject

    def test_coverage_measures_subprocesses(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert 'patch = ["subprocess"]' in pyproject
