#!/usr/bin/env python3
"""Detect zero-argument dotted method invocations in .gom source files.

This script scans `programs/` and `examples/` directories for lines matching
the pattern `obj.method !` (a dotted name followed by whitespace and a
bang). In the Gulf of Mexico interpreter that pattern returns the method
itself instead of calling it; for zero-argument methods the correct
invocation is `obj.method()!`.

Exit status: 0 if no occurrences found, 1 if any matches were found.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERN = re.compile(r"^(\s*)([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*!\s*(#.*)?$")


def should_scan(path: Path) -> bool:
    s = str(path)
    # Only scan program/example demo files (not build artifacts or generated docs)
    return ("/programs/" in s or "/examples/" in s) and path.suffix == ".gom"


def main() -> int:
    hits = []
    for path in sorted(ROOT.rglob("*.gom")):
        if not should_scan(path):
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            m = PATTERN.match(line)
            if m:
                hits.append((path.relative_to(ROOT), i, line.rstrip()))

    if hits:
        print(
            "Zero-argument dotted method invocation(s) found (use obj.method()! instead):",
            file=sys.stderr,
        )
        for p, ln, text in hits:
            print(f"{p}:{ln}: {text}", file=sys.stderr)
        return 1

    print("No zero-arg dotted method invocations found.")
    return 0


def _fix_file(path: Path) -> bool:
    """Perform an in-place fix of matching lines and return True if any changes were made."""
    changed = False
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        m = PATTERN.match(line)
        if m:
            leading, obj, method, comment = m.groups()
            # Preserve comment and leading whitespace
            comment = comment or ""
            new_line = f"{leading}{obj}.{method}()!{(' ' + comment) if comment else ''}"
            if new_line != line:
                changed = True
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    if changed:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return changed


def run_with_fix(dry_run: bool = False) -> int:
    """Scan files and optionally fix occurrences.

    Returns 0 when no issues (or all fixed in dry-run), 1 if issues were found
    or files modified (when not dry-run).
    """
    hits = []
    for path in sorted(ROOT.rglob("*.gom")):
        if not should_scan(path):
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if PATTERN.match(line):
                hits.append((path, i, line.rstrip()))

    if not hits:
        print("No zero-arg dotted method invocations found.")
        return 0

    if dry_run:
        print("Found occurrences (dry-run):", file=sys.stderr)
        for p, ln, text in hits:
            print(f"{p.relative_to(ROOT)}:{ln}: {text}", file=sys.stderr)
        return 1

    # Perform in-place fix and report
    modified_files = []
    for path, _, _ in hits:
        if _fix_file(path):
            modified_files.append(path.relative_to(ROOT))

    if modified_files:
        print("Modified files:")
        for p in modified_files:
            print(str(p))
        # Indicate that files were changed so callers (pre-commit) can re-stage
        return 1

    return 0


if __name__ == "__main__":
    # Simple CLI behavior
    args = sys.argv[1:]
    if "--fix" in args:
        dry = "--dry-run" in args
        raise SystemExit(run_with_fix(dry_run=dry))
    raise SystemExit(main())
