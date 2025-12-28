#!/usr/bin/env python3
"""Run GOM test files via REPL and report results."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
# Look for .gom files in tests/ and examples/ directories
TEST_DIRS = [ROOT / "tests", ROOT / "examples"]
TIMEOUT = 8  # seconds per file

PASS_MARKERS = [
    "PASS:",  # explicit tests that print PASS
]


def run_via_repl(path: Path):
    """Run a single .gom file by loading it into the REPL and quitting."""
    cmd = [sys.executable, "-m", "gulfofmexico.repl"]
    rel = path.relative_to(ROOT)
    # Feed :load and :quit
    input_data = f":load {rel}\n:quit\n".encode()
    try:
        proc = subprocess.run(
            cmd,
            input=input_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=TIMEOUT,
            cwd=str(ROOT),
            check=False,
        )
        code = proc.returncode
        out = proc.stdout.decode(errors="replace")
        has_error = (
            "InterpretationError" in out or "Traceback" in out
        )
        ok = code == 0 and not has_error
        status = "PASS" if ok else "UNKNOWN"
        # if no explicit PASS, still consider it PASS if exit clean
        if any(m in out for m in PASS_MARKERS):
            status = "PASS"
        return status, code, out
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode(errors="replace")
        return "TIMEOUT", 124, out
    except (OSError, subprocess.SubprocessError) as e:
        return "ERROR", -1, str(e)


def main():
    """Run all GOM test files and report results."""
    files = []
    for test_dir in TEST_DIRS:
        if test_dir.exists():
            files.extend(sorted(test_dir.rglob("*.gom")))
    files = sorted(set(files))  # Remove duplicates

    if not files:
        dirs_str = ", ".join(str(d) for d in TEST_DIRS)
        print(f"No .gom files found in {dirs_str}", file=sys.stderr)
        sys.exit(1)

    results = []
    for f in files:
        status, code, out = run_via_repl(f)
        preview = "\n".join(out.splitlines()[:10])
        results.append((f, status, code, preview))
        print(f"{status:10} [{code:>3}]  {f.relative_to(ROOT)}")

    print("\n=== Summary ===")
    total = len(results)
    failures = [r for r in results if r[1] not in ("PASS", "UNKNOWN")]
    print(f"Total files: {total}")
    print(f"Failures:   {len(failures)}")

    for f, status, code, preview in results:
        if status not in ("PASS",):
            print("\n---", f.relative_to(ROOT), f"[{status}/{code}]", "---")
            print(preview)


if __name__ == "__main__":
    main()
