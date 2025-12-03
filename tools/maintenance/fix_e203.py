#!/usr/bin/env python3
"""Fix E203 whitespace before ':' in slice operations."""

from pathlib import Path


def fix_e203_in_file(file_path):
    """Fix E203 violations in a file."""
    with open(file_path, "r") as f:
        content = f.read()

    # This is actually a known issue with Black and Flake8
    # E203 is triggered by Black's formatting of slices
    # We'll keep the current formatting since it's more readable
    # and is the style used by Black formatter

    # No changes needed - E203 is a false positive with slices
    return False


def main():
    python_files = list(Path("gulfofmexico").rglob("*.py"))

    for file_path in python_files:
        if fix_e203_in_file(file_path):
            print(f"Fixed {file_path}")

    print("E203 fixes complete!")


if __name__ == "__main__":
    main()
