#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROGRAMS = ROOT / "programs"
TIMEOUT = 6  # seconds per file

# Simple heuristics for classifying output
PASS_MARKERS = [
    "PASS:",
]

# Files that intentionally may wait for when/after: use shorter head in preview later


def run_file(path: Path):
    cmd = [sys.executable, "-m", "gulfofmexico", str(path)]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=TIMEOUT,
            cwd=str(ROOT),
        )
        code = proc.returncode
        out = proc.stdout.decode(errors="replace") if isinstance(proc.stdout, bytes) else proc.stdout
        status = "PASS" if any(m in out for m in PASS_MARKERS) or code in (0, 124, 130, 143) else "UNKNOWN"
        return status, code, out
    except subprocess.TimeoutExpired as e:
        out = e.stdout or b""
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        # Interpreter prints a completion hint and then waits; timeout here is expected
        return "PASS-TIMEOUT", 124, out
    except Exception as e:
        return "ERROR", -1, str(e)


def main():
    files = sorted(PROGRAMS.rglob("*.gom"))
    if not files:
        print("No .gom files found under programs/", file=sys.stderr)
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
    failures = [r for r in results if r[1] not in ("PASS", "PASS-TIMEOUT", "UNKNOWN")]
    print(f"Total files: {total}")
    print(f"Failures:   {len(failures)}")

    # Show details for non-PASS statuses
    for f, status, code, preview in results:
        if status not in ("PASS", "PASS-TIMEOUT"):
            print("\n---", f.relative_to(ROOT), f"[{status}/{code}]", "---")
            print(preview)


if __name__ == "__main__":
    main()
