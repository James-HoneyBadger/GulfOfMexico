"""
Graphics module for Gulf of Mexico

Provides canvas drawing, colors, shapes with Gulf of Mexico's unique features:
- -1 based coordinate system (top-left is (-1, -1))
- Fractional pixel indexing
- Three-valued color logic (maybe transparency)
- Probabilistic rendering
"""

from .canvas import GulfOfMexicoCanvas
from .colors import GulfOfMexicoColor, parse_color

__all__ = ["GulfOfMexicoCanvas", "GulfOfMexicoColor", "parse_color"]
