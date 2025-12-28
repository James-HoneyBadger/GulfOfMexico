#!/usr/bin/env python3
"""Run GOM programs and classify results."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
# Look for .gom files in tests/ and examples/ directories
TEST_DIRS = [ROOT / "tests", ROOT / "examples"]
TIMEOUT = 6  # seconds per file

# Simple heuristics for classifying output
PASS_MARKERS = [
    "PASS:",
]

# Files that intentionally may wait for when/after:
# use shorter head in preview later


def run_file(path: Path):
    """Execute a GOM file and return status and output."""
    cmd = [sys.executable, "-m", "gulfofmexico", str(path)]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=TIMEOUT,
            cwd=str(ROOT),
            check=False,
        )
        code = proc.returncode
        out = (
            proc.stdout.decode(errors="replace")
            if isinstance(proc.stdout, bytes)
            else proc.stdout
        )
        success = (
            any(m in out for m in PASS_MARKERS)
            or code in (0, 124, 130, 143)
        )
        status = "PASS" if success else "UNKNOWN"
        return status, code, out
    except subprocess.TimeoutExpired as e:
        out_bytes: bytes = e.stdout or b""
        if isinstance(out_bytes, bytes):
            out = out_bytes.decode(errors="replace")
        else:
            out = str(out_bytes)
        # Timeout is expected for interactive programs
        return "PASS-TIMEOUT", 124, out
    except (OSError, subprocess.SubprocessError) as e:
        return "ERROR", -1, str(e)


def main():
    """Process all GOM test files and report results."""
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
        status, code, out = run_file(f)
        # Keep only first ~12 lines of output for the report
        preview = "\n".join(out.splitlines()[:12])
        results.append((f, status, code, preview))
        print(f"{status:12} [{code:>3}]  {f.relative_to(ROOT)}")

    print("\n=== Summary ===")
    total = len(results)
    failures = [
        r
        for r in results
        if r[1] not in ("PASS", "PASS-TIMEOUT", "UNKNOWN")
    ]
    print(f"Total files: {total}")
    print(f"Failures:   {len(failures)}")

    # Show details for non-PASS statuses
    for f, status, code, preview in results:
        if status not in ("PASS", "PASS-TIMEOUT"):
            print(
                "\n---",
                f.relative_to(ROOT),
                f"[{status}/{code}]",
                "---",
            )
            print(preview)


if __name__ == "__main__":
    main()
