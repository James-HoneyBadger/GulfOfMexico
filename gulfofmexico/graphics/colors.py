"""
Color system for Gulf of Mexico graphics

Supports:
- RGB and RGBA colors
- Three-valued logic for alpha (maybe = 0.5)
- Named colors
- Probabilistic color values
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union
import random


@dataclass
class GulfOfMexicoColor:
    """Color with support for maybe/probabilistic values."""

    r: Union[int, float, None]  # 0-255 or None for "maybe"
    g: Union[int, float, None]
    b: Union[int, float, None]
    a: Union[int, float, None] = 255  # alpha: 0-255, None = "maybe" (127)

    def to_rgba_tuple(self) -> tuple[int, int, int, int]:
        """Convert to (r, g, b, a) tuple, resolving maybe values."""

        def resolve(val: Union[int, float, None], default: int = 127) -> int:
            if val is None:  # "maybe"
                return random.randint(0, 255) if random.random() > 0.5 else default
            return int(max(0, min(255, val)))

        return (resolve(self.r), resolve(self.g), resolve(self.b), resolve(self.a, 127))

    def to_hex(self) -> str:
        """Convert to hex color string."""
        r, g, b, a = self.to_rgba_tuple()
        if a == 255:
            return f"#{r:02x}{g:02x}{b:02x}"
        return f"#{r:02x}{g:02x}{b:02x}{a:02x}"


# Named colors (Gulf of Mexico style)
NAMED_COLORS = {
    "red": GulfOfMexicoColor(255, 0, 0),
    "green": GulfOfMexicoColor(0, 255, 0),
    "blue": GulfOfMexicoColor(0, 0, 255),
    "yellow": GulfOfMexicoColor(255, 255, 0),
    "cyan": GulfOfMexicoColor(0, 255, 255),
    "magenta": GulfOfMexicoColor(255, 0, 255),
    "white": GulfOfMexicoColor(255, 255, 255),
    "black": GulfOfMexicoColor(0, 0, 0),
    "gray": GulfOfMexicoColor(127, 127, 127),
    "grey": GulfOfMexicoColor(127, 127, 127),
    "orange": GulfOfMexicoColor(255, 165, 0),
    "purple": GulfOfMexicoColor(128, 0, 128),
    "pink": GulfOfMexicoColor(255, 192, 203),
    "brown": GulfOfMexicoColor(165, 42, 42),
    "maybe": GulfOfMexicoColor(None, None, None, None),  # Fully probabilistic!
}


def parse_color(
    color_spec: Union[str, tuple, list, GulfOfMexicoColor],
) -> GulfOfMexicoColor:
    """Parse various color formats into GulfOfMexicoColor.

    Supports:
    - Named colors: "red", "blue", "maybe"
    - Hex strings: "#FF0000", "#FF0000AA"
    - RGB tuples: (255, 0, 0)
    - RGBA tuples: (255, 0, 0, 128)
    - GulfOfMexicoColor objects (pass-through)
    """
    if isinstance(color_spec, GulfOfMexicoColor):
        return color_spec

    if isinstance(color_spec, str):
        # Named color
        if color_spec.lower() in NAMED_COLORS:
            return NAMED_COLORS[color_spec.lower()]

        # Hex color
        if color_spec.startswith("#"):
            hex_str = color_spec[1:]
            if len(hex_str) == 6:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                return GulfOfMexicoColor(r, g, b)
            elif len(hex_str) == 8:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                a = int(hex_str[6:8], 16)
                return GulfOfMexicoColor(r, g, b, a)

    if isinstance(color_spec, (tuple, list)):
        if len(color_spec) == 3:
            return GulfOfMexicoColor(color_spec[0], color_spec[1], color_spec[2])
        elif len(color_spec) == 4:
            return GulfOfMexicoColor(
                color_spec[0], color_spec[1], color_spec[2], color_spec[3]
            )

    # Default to black if can't parse
    return GulfOfMexicoColor(0, 0, 0)
