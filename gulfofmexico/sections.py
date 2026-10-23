"""
Multi-File Sections

A single source file may declare several named sections separated by
``===== name =====`` marker lines. Each section is parsed and executed
independently and can ``export`` values to, or ``import`` values from, another
section — so a section behaves like an importable file.

Both the runner (:func:`gulfofmexico.run_file`) and the static checker
(:func:`gulfofmexico.tools.check_source`) split sources here, which keeps the
two paths in agreement.
"""

from __future__ import annotations

import re
from typing import Optional

__all__ = ["SECTION_MARKER", "split_sections"]

SECTION_MARKER = re.compile(r"=====.*")


def split_sections(code: str) -> list[tuple[Optional[str], str]]:
    """Split *code* into ``(section_name, source)`` pairs.

    The preamble before the first marker is returned first, with a ``None``
    name. A file without markers yields a single unnamed section holding the
    whole source.
    """
    lines = code.splitlines(keepends=True)
    markers = [SECTION_MARKER.match(line) for line in lines]
    if not any(markers):
        return [(None, code)]

    sections: list[tuple[Optional[str], str]] = []
    for index, match in reversed([*enumerate(markers)]):
        if match is None:
            continue
        name = match.group().strip("=").strip() or None
        sections.insert(0, (name, "".join(lines[index + 1 :])))
        del lines[index:]
    sections.insert(0, (None, "".join(lines)))
    return sections
