#!/usr/bin/env python3
"""Remove parentheses from function calls in .gom files"""

import re
import sys
from pathlib import Path


def fix_file(filepath):
    """Fix function calls in a single file"""
    with open(filepath, "r") as f:
        content = f.read()

    original = content

    # Pattern: function_name(args) where function_name is lowercase and not preceded by 'function' or 'fn' or 'async'
    # Replace with: function_name args

    # Match: word(stuff) but not after 'function' or 'fn' or 'async'
    # We need to handle: add(3, 5) -> add 3, 5
    # But keep: function add(a, b) unchanged

    # Find all function calls (name followed by parentheses with content)
    # But NOT when preceded by keywords like 'function', 'fn', 'async', 'class'

    # Remove parens from function calls - match word(content) but not after function/fn/async keywords
    pattern = r"(?<!function\s)(?<!fn\s)(?<!async\s)(?<!class\s)(\b[a-z_][a-zA-Z0-9_]*)\(([^)]+)\)"

    def replace_call(match):
        func_name = match.group(1)
        args = match.group(2)
        # Check if this looks like a function definition context by looking backward
        start = match.start()
        # Look at the 20 characters before this match
        context = content[max(0, start - 20) : start]

        # If preceded by function/fn/async keywords, don't replace
        if re.search(r"\b(function|fn|async)\s*$", context):
            return match.group(0)  # Keep original

        # Otherwise, remove parentheses
        return f"{func_name} {args}"

    content = re.sub(pattern, replace_call, content)

    # Also handle zero-argument calls: func() -> func
    # But again, not in function definitions
    pattern_zero = r"(?<!function\s)(?<!fn\s)(?<!async\s)(\b[a-z_][a-zA-Z0-9_]*)\(\)"

    def replace_zero_arg(match):
        func_name = match.group(1)
        start = match.start()
        context = content[max(0, start - 20) : start]

        if re.search(r"\b(function|fn|async)\s*$", context):
            return match.group(0)  # Keep original

        return func_name

    content = re.sub(pattern_zero, replace_zero_arg, content)

    if content != original:
        with open(filepath, "w") as f:
            f.write(content)
        return True
    return False


def main():
    programs_dir = Path("programs")
    if not programs_dir.exists():
        print("programs/ directory not found")
        sys.exit(1)

    fixed_count = 0
    for gom_file in programs_dir.rglob("*.gom"):
        if fix_file(gom_file):
            print(f"Fixed: {gom_file}")
            fixed_count += 1

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
