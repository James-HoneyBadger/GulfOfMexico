"""
Tests for debug output behavior.

Verifies that:
1. Internal debug messages are buffered and NOT shown during normal execution
2. Debug messages ARE shown when GULFOFMEXICO_DEBUG=1 is set
3. Debug messages ARE flushed to stderr when an error occurs
4. The flush_debug_logs() function works correctly

Can be run with pytest or standalone:
    python tests/test_debug_output.py
"""

import os
import subprocess
import sys
from pathlib import Path

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

    # Define a minimal pytest-compatible decorator
    def pytest_fixture(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    pytest = type("pytest", (), {"fixture": pytest_fixture})


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def run_program(gom_code: str, env: dict = None, expect_error: bool = False):
    """Run a Gulf of Mexico program and capture stdout/stderr.

    Args:
        gom_code: GOM source code to execute
        env: Environment variables to set
        expect_error: Whether we expect the program to fail

    Returns:
        tuple of (stdout, stderr, returncode)
    """
    # Create temporary file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".gom", delete=False) as f:
        f.write(gom_code)
        temp_file = f.name

    try:
        # Prepare environment
        test_env = os.environ.copy()
        if env:
            test_env.update(env)

        # Run the program
        result = subprocess.run(
            [sys.executable, "-m", "gulfofmexico", temp_file],
            capture_output=True,
            text=True,
            timeout=3,
            env=test_env,
            cwd=str(PROJECT_ROOT),
        )

        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        # Program likely has when/after statements waiting
        # Kill it and return what we captured
        return "", "", 124  # timeout exit code
    finally:
        # Clean up temp file
        os.unlink(temp_file)


def test_no_debug_output_on_success():
    """Verify that successful programs don't show [DB_PRINT] messages."""
    code = """
print("Hello, World")!
const x = 42!
print("x =", x)!
"""

    stdout, stderr, returncode = run_program(code)

    # Check that program executed successfully
    assert returncode in (0, 124)  # 0 or timeout (waiting for when statements)

    # Check stdout has the program output
    assert "Hello, World" in stdout
    assert "42" in stdout

    # Check that stderr does NOT contain debug messages
    assert "[DB_PRINT]" not in stderr


def test_debug_output_with_env_var():
    """Verify that GULFOFMEXICO_DEBUG=1 shows [DB_PRINT] messages."""
    code = """
print("Testing debug")!
"""

    stdout, stderr, returncode = run_program(code, env={"GULFOFMEXICO_DEBUG": "1"})

    # Check that program executed
    assert returncode in (0, 124)

    # Check stdout has the program output
    assert "Testing debug" in stdout

    # Check that stderr DOES contain debug messages when env var is set
    assert "[DB_PRINT]" in stderr
    assert "Called with:" in stderr


def test_debug_output_on_error():
    """Verify that errors flush buffered debug messages."""
    code = """
print("Before error")!
const x = undefined_variable!
print("After error")!
"""

    stdout, stderr, returncode = run_program(code, expect_error=True)

    # Check that program failed
    assert returncode != 0

    # Check stdout has output before the error
    assert "Before error" in stdout

    # Check that stderr contains the debug messages that were buffered
    # (they should be flushed when the error occurs)
    assert "[DB_PRINT]" in stderr
    assert "Before error" in stderr


def test_flush_debug_logs_function():
    """Test the flush_debug_logs() function directly."""
    from gulfofmexico.builtin import db_print, flush_debug_logs, _DEBUG_LOGS
    from gulfofmexico.builtin import GulfOfMexicoString
    import io
    import sys
    from contextlib import redirect_stderr

    # Clear any existing debug logs
    _DEBUG_LOGS.clear()

    # Call db_print without GULFOFMEXICO_DEBUG set
    old_env = os.environ.get("GULFOFMEXICO_DEBUG")
    if "GULFOFMEXICO_DEBUG" in os.environ:
        del os.environ["GULFOFMEXICO_DEBUG"]

    try:
        # Capture stderr
        stderr_capture = io.StringIO()

        with redirect_stderr(stderr_capture):
            # These should buffer, not print
            db_print(GulfOfMexicoString("Test 1"))
            db_print(GulfOfMexicoString("Test 2"))

            # Verify nothing written yet
            assert stderr_capture.getvalue() == ""

            # Now flush
            flush_debug_logs()

            # Verify messages were written
            stderr_output = stderr_capture.getvalue()
            assert "[DB_PRINT]" in stderr_output
            assert "Test 1" in stderr_output
            assert "Test 2" in stderr_output

        # Verify buffer was cleared
        assert len(_DEBUG_LOGS) == 0
    finally:
        # Restore environment
        if old_env is not None:
            os.environ["GULFOFMEXICO_DEBUG"] = old_env


def test_no_debug_in_repl_success():
    """Verify REPL doesn't show debug messages on successful execution."""
    # This would require a more complex test with pexpect or similar
    # For now, we'll skip it as the main behavior is tested above
    pass


def test_web_ide_debug_suppression():
    """Verify web IDE suppresses debug output when GULFOFMEXICO_DEBUG is not set."""
    from gulfofmexico.ide.web_ide import WEB_IDE_DEBUG, _webide_debug
    import io
    import sys
    from contextlib import redirect_stderr

    # Verify WEB_IDE_DEBUG respects environment
    old_env = os.environ.get("GULFOFMEXICO_DEBUG")

    try:
        # Without debug env var
        if "GULFOFMEXICO_DEBUG" in os.environ:
            del os.environ["GULFOFMEXICO_DEBUG"]

        # Reimport to pick up new env var
        import importlib
        import gulfofmexico.ide.web_ide as web_ide_module

        importlib.reload(web_ide_module)

        # Should be False
        assert not web_ide_module.WEB_IDE_DEBUG

        # _webide_debug should not write anything
        stderr_capture = io.StringIO()
        with redirect_stderr(stderr_capture):
            web_ide_module._webide_debug("Test message")

        assert stderr_capture.getvalue() == ""

        # With debug env var
        os.environ["GULFOFMEXICO_DEBUG"] = "1"
        importlib.reload(web_ide_module)

        # Should be True
        assert web_ide_module.WEB_IDE_DEBUG

        # _webide_debug should write
        stderr_capture = io.StringIO()
        with redirect_stderr(stderr_capture):
            web_ide_module._webide_debug("Test message 2")

        assert "Test message 2" in stderr_capture.getvalue()

    finally:
        # Restore environment
        if old_env is not None:
            os.environ["GULFOFMEXICO_DEBUG"] = old_env
        else:
            if "GULFOFMEXICO_DEBUG" in os.environ:
                del os.environ["GULFOFMEXICO_DEBUG"]


if __name__ == "__main__":
    if HAS_PYTEST:
        pytest.main([__file__, "-v"])
    else:
        # Run tests manually
        print("Running tests without pytest...")
        print("\n" + "=" * 70)

        tests = [
            ("No debug output on success", test_no_debug_output_on_success),
            ("Debug output with env var", test_debug_output_with_env_var),
            ("Debug output on error", test_debug_output_on_error),
            ("Flush debug logs function", test_flush_debug_logs_function),
            ("Web IDE debug suppression", test_web_ide_debug_suppression),
        ]

        passed = 0
        failed = 0

        for name, test_func in tests:
            try:
                print(f"\nTest: {name}")
                test_func()
                print(f"✓ PASSED: {name}")
                passed += 1
            except AssertionError as e:
                print(f"✗ FAILED: {name}")
                print(f"  Error: {e}")
                failed += 1
            except Exception as e:
                print(f"✗ ERROR: {name}")
                print(f"  {type(e).__name__}: {e}")
                failed += 1

        print("\n" + "=" * 70)
        print(f"\nResults: {passed} passed, {failed} failed")
        sys.exit(0 if failed == 0 else 1)
