"""Guard test: ensure there are no accidental zero-arg dotted method calls.

This test scans program/example .gom files for occurrences of the pattern
`<identifier>.<identifier> !` which comes from the no-paren sweep. For
zero-argument method invocations the language requires parentheses (e.g.
`obj.method()!`) to execute the method — `obj.method !` only returns the
method value and does not call it.

If the test finds any matches it lists them so they can be fixed.
"""

import re
from pathlib import Path

PATTERN = re.compile(r"(^|\s)([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s+!$")


def find_matches(root: Path):
    matches = []
    for path in sorted(root.rglob("*.gom")):
        # Only scan example/program files — ignore compiler examples or unrelated paths
        if "programs" not in str(path) and "examples" not in str(path):
            continue
        for i, line in enumerate(path.read_text().splitlines(), start=1):
            if PATTERN.search(line):
                matches.append((path.relative_to(root), i, line.strip()))
    return matches


def test_no_zeroarg_dotted_calls_in_programs_and_examples():
    root = Path(__file__).parent.parent
    hits = find_matches(root)
    if hits:
        out_lines = [f"{p}:{ln}: {text}" for p, ln, text in hits]
        pytest_msg = "\n".join(out_lines)
        raise AssertionError(
            "Zero-argument dotted method invocation(s) found — update to use parentheses (e.g. obj.method()!)\n"
            + pytest_msg
        )
