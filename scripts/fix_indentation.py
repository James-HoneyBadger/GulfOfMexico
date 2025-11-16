#!/usr/bin/env python3
"""Fix indentation in all .gom files to use multiples of 3 spaces."""

import re
from pathlib import Path


def get_indentation(line):
    """Get the number of leading spaces in a line."""
    return len(line) - len(line.lstrip(" "))


def fix_indentation(content):
    """Fix indentation to be multiples of 3."""
    lines = content.split("\n")
    fixed_lines = []
    changes_made = False

    for line in lines:
        # Skip empty lines and lines with no leading spaces
        if not line or not line[0] == " ":
            fixed_lines.append(line)
            continue

        indent = get_indentation(line)
        rest = line.lstrip(" ")

        # If indentation is not a multiple of 3, fix it
        if indent % 3 != 0:
            # Round to nearest multiple of 3
            new_indent = round(indent / 3) * 3
            fixed_line = " " * new_indent + rest
            fixed_lines.append(fixed_line)
            changes_made = True
        else:
            fixed_lines.append(line)

    return "\n".join(fixed_lines), changes_made


def main():
    """Fix all .gom files in the project."""
    gom_dir = Path("/home/james/GOM")
    gom_files = list(gom_dir.rglob("*.gom"))

    fixed_count = 0

    for gom_file in gom_files:
        try:
            content = gom_file.read_text(encoding="utf-8")
            fixed_content, changed = fix_indentation(content)

            if changed:
                gom_file.write_text(fixed_content, encoding="utf-8")
                print(f"Fixed: {gom_file.relative_to(gom_dir)}")
                fixed_count += 1
        except Exception as e:
            print(f"Error processing {gom_file}: {e}")

    print(f"\nTotal files fixed: {fixed_count}/{len(gom_files)}")


if __name__ == "__main__":
    main()
