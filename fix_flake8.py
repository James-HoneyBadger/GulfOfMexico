#!/usr/bin/env python3
"""
Automatically fix common Flake8 issues in the codebase.
"""
import re
import sys
from pathlib import Path


def remove_unused_imports(file_path, unused_imports):
    """Remove unused imports from a file."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Check if this line contains an unused import
        should_skip = False
        for unused in unused_imports:
            # Handle different import formats
            if f"import {unused}" in line or f"from {unused}" in line:
                # Check if it's the specific unused import
                if (
                    f"'{unused}'" in unused
                    or line.strip().endswith(unused)
                    or f"{unused}," in line
                    or f" {unused}\n" in line
                ):
                    should_skip = True
                    break

        if not should_skip:
            new_lines.append(line)

    with open(file_path, "w") as f:
        f.writelines(new_lines)


def fix_trailing_whitespace(file_path):
    """Remove trailing whitespace from all lines."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    new_lines = [line.rstrip() + "\n" if line.strip() else "\n" for line in lines]

    with open(file_path, "w") as f:
        f.writelines(new_lines)


def fix_inline_comments(file_path):
    """Fix inline comments that don't start with '# '."""
    with open(file_path, "r") as f:
        content = f.read()

    # Fix comments like #comment to # comment
    content = re.sub(r"([^#])#([^ \n])", r"\1# \2", content)

    with open(file_path, "w") as f:
        f.write(content)


def main():
    # List of files to fix
    python_files = list(Path("gulfofmexico").rglob("*.py"))
    python_files.extend(Path(".").glob("*.py"))

    for file_path in python_files:
        if file_path.name == "fix_flake8.py":
            continue

        print(f"Fixing {file_path}...")

        # Fix trailing whitespace
        fix_trailing_whitespace(file_path)

        # Fix inline comments
        fix_inline_comments(file_path)

    print("Done!")


if __name__ == "__main__":
    main()
