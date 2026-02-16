"""Test suite that runs all GOM example programs and spec compliance tests."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples"
TESTS_DIR = ROOT / "tests"
TIMEOUT = 30  # seconds per program


def _run_gom(filepath: Path) -> subprocess.CompletedProcess:
    """Run a .gom file via the interpreter and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "gulfofmexico", "-s", str(filepath)],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        cwd=str(ROOT),
    )


# Collect all example .gom files
EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.gom"))
TEST_GOM_FILES = sorted(TESTS_DIR.glob("*.gom"))


@pytest.mark.parametrize(
    "gom_file",
    EXAMPLE_FILES,
    ids=[f.stem for f in EXAMPLE_FILES],
)
def test_example_runs_successfully(gom_file: Path) -> None:
    """Each example program should exit with code 0."""
    result = _run_gom(gom_file)
    assert result.returncode == 0, (
        f"{gom_file.name} failed (exit {result.returncode}):\n"
        f"STDOUT:\n{result.stdout[-500:]}\n"
        f"STDERR:\n{result.stderr[-500:]}"
    )


@pytest.mark.parametrize(
    "gom_file",
    TEST_GOM_FILES,
    ids=[f.stem for f in TEST_GOM_FILES],
)
def test_gom_test_file(gom_file: Path) -> None:
    """Each .gom test file should exit with code 0."""
    result = _run_gom(gom_file)
    assert result.returncode == 0, (
        f"{gom_file.name} failed (exit {result.returncode}):\n"
        f"STDOUT:\n{result.stdout[-500:]}\n"
        f"STDERR:\n{result.stderr[-500:]}"
    )


def test_spec_compliance_output() -> None:
    """Spec compliance test should complete with ALL TESTS COMPLETE marker."""
    spec_file = TESTS_DIR / "spec_compliance.gom"
    if not spec_file.exists():
        pytest.skip("spec_compliance.gom not found")
    result = _run_gom(spec_file)
    assert result.returncode == 0, f"spec_compliance failed: {result.stderr[-300:]}"
    assert "ALL TESTS COMPLETE" in result.stdout, (
        "spec_compliance.gom did not print completion marker"
    )
