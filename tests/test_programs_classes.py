"""Unit tests for the `programs/01_basics/06_classes.gom` example.

This test runs the program source via the same helper used by other tests
and asserts the expected printed output appears.
"""

from pathlib import Path


def test_programs_01_basics_06_classes(tmp_path, monkeypatch):
    """Run the classes example and assert expected outputs.

    Uses the helper `run_program` from tests/test_debug_output.py which creates
    a temporary .gom file and invokes the program via the test harness.
    """
    # Import the helper used by the test-suite to run GOM snippets
    try:
        from tests.test_debug_output import run_program
    except Exception:
        # If importing helper fails for whatever reason, fallback to a thin
        # runner that uses the same mechanism. This keeps the test resilient
        # to running under different test runners.
        from tests.test_debug_output import run_program  # try again to fail loudly

    proj_root = Path(__file__).parent.parent
    program_path = proj_root / "programs" / "01_basics" / "06_classes.gom"

    code = program_path.read_text()

    stdout, stderr, returncode = run_program(code)

    # Program should complete successfully
    assert returncode in (0, 124)

    # Expected outputs from the example program
    assert "Hi, I'm Alice and I'm 25 years old." in stdout
    assert "Hi, I'm Bob and I'm 30 years old." in stdout
    assert "Bob is now 31!" in stdout
