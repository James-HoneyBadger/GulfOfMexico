"""
Canvas implementation for Gulf of Mexico graphics

Features:
- -1 based coordinate system (top-left is (-1, -1))
- Fractional pixel indexing
- Drawing primitives (rect, circle, line, polygon, text)
- Transformation stack
- Save/load/display capabilities
"""

from __future__ import annotations
from typing import Union, Optional, List, Tuple
from dataclasses import dataclass, field
import math

try:
    from PIL import Image, ImageDraw, ImageFont

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    Image = None
    ImageDraw = None
    ImageFont = None

from .colors import GulfOfMexicoColor, parse_color


@dataclass
class GulfOfMexicoCanvas:
    """Canvas for drawing with Gulf of Mexico's -1 based coordinate system."""

    width: int
    height: int
    background: GulfOfMexicoColor = field(
        default_factory=lambda: GulfOfMexicoColor(255, 255, 255)
    )
    _image: Optional[Image.Image] = field(default=None, init=False, repr=False)
    _draw: Optional[ImageDraw.ImageDraw] = field(default=None, init=False, repr=False)
    _transform_stack: List[dict] = field(default_factory=list, init=False, repr=False)
    _current_transform: dict = field(
        default_factory=lambda: {"translate": (0, 0), "rotate": 0, "scale": (1, 1)},
        init=False,
        repr=False,
    )

    def __post_init__(self):
        """Initialize the PIL image and drawing context."""
        if not PILLOW_AVAILABLE:
            raise ImportError(
                "Pillow (PIL) is required for graphics. Install it with:\n"
                "  pip install Pillow\n"
                "or install with graphics extras:\n"
                "  pip install -e .[graphics]"
            )

        bg_color = self.background.to_rgba_tuple()
        self._image = Image.new("RGBA", (self.width, self.height), bg_color)
        self._draw = ImageDraw.Draw(self._image)

    def _convert_coords(
        self, x: Union[int, float], y: Union[int, float]
    ) -> Tuple[float, float]:
        """Convert from -1 based coords to PIL's 0-based coords."""
        # In Gulf of Mexico: (-1, -1) is top-left
        # In PIL: (0, 0) is top-left
        # So we add 1 to both coordinates
        return (x + 1, y + 1)

    def _apply_transform(self, x: float, y: float) -> Tuple[float, float]:
        """Apply current transformation to coordinates."""
        # Apply scale
        sx, sy = self._current_transform["scale"]
        x *= sx
        y *= sy

        # Apply rotation (around origin)
        angle = math.radians(self._current_transform["rotate"])
        if angle != 0:
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            x_rot = x * cos_a - y * sin_a
            y_rot = x * sin_a + y * cos_a
            x, y = x_rot, y_rot

        # Apply translation
        tx, ty = self._current_transform["translate"]
        x += tx
        y += ty

        return (x, y)

    def clear(self, color: Optional[Union[str, GulfOfMexicoColor]] = None) -> None:
        """Clear the canvas to a solid color."""
        if color is None:
            color = self.background
        else:
            color = parse_color(color)

        bg_rgba = color.to_rgba_tuple()
        self._image = Image.new("RGBA", (self.width, self.height), bg_rgba)
        self._draw = ImageDraw.Draw(self._image)

    def pixel(
        self,
        x: Union[int, float],
        y: Union[int, float],
        color: Union[str, GulfOfMexicoColor],
    ) -> None:
        """Set a single pixel (supports fractional coordinates!)."""
        color_obj = parse_color(color)
        rgba = color_obj.to_rgba_tuple()

        # Convert coordinates
        px, py = self._convert_coords(x, y)
        px, py = self._apply_transform(px, py)

        # Fractional indexing: draw to nearby pixels with interpolation
        x_int, y_int = int(px), int(py)
        x_frac, y_frac = px - x_int, py - y_int

        if x_frac == 0 and y_frac == 0:
            # Exact pixel
            if 0 <= x_int < self.width and 0 <= y_int < self.height:
                self._image.putpixel((x_int, y_int), rgba)
        else:
            # Fractional: blend to nearby pixels
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                nx, ny = x_int + dx, y_int + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # Simple blending (could be more sophisticated)
                    weight = (1 - abs(dx - x_frac)) * (1 - abs(dy - y_frac))
                    if weight > 0.1:  # Only draw if significant weight
                        self._image.putpixel((nx, ny), rgba)

    def rect(
        self,
        x: Union[int, float],
        y: Union[int, float],
        width: Union[int, float],
        height: Union[int, float],
        color: Union[str, GulfOfMexicoColor],
        fill: bool = True,
    ) -> None:
        """Draw a rectangle."""
        color_obj = parse_color(color)
        rgba = color_obj.to_rgba_tuple()

        # Convert coordinates
        x1, y1 = self._convert_coords(x, y)
        x2, y2 = self._convert_coords(x + width, y + height)

        # Apply transform to corners
        x1, y1 = self._apply_transform(x1, y1)
        x2, y2 = self._apply_transform(x2, y2)

        if fill:
            self._draw.rectangle([x1, y1, x2, y2], fill=rgba)
        else:
            self._draw.rectangle([x1, y1, x2, y2], outline=rgba, width=2)

    def circle(
        self,
        x: Union[int, float],
        y: Union[int, float],
        radius: Union[int, float],
        color: Union[str, GulfOfMexicoColor],
        fill: bool = True,
    ) -> None:
        """Draw a circle."""
        color_obj = parse_color(color)
        rgba = color_obj.to_rgba_tuple()

        # Convert center coordinates
        cx, cy = self._convert_coords(x, y)
        cx, cy = self._apply_transform(cx, cy)

        # Calculate bounding box
        x1 = cx - radius
        y1 = cy - radius
        x2 = cx + radius
        y2 = cy + radius

        if fill:
            self._draw.ellipse([x1, y1, x2, y2], fill=rgba)
        else:
            self._draw.ellipse([x1, y1, x2, y2], outline=rgba, width=2)

    def line(
        self,
        x1: Union[int, float],
        y1: Union[int, float],
        x2: Union[int, float],
        y2: Union[int, float],
        color: Union[str, GulfOfMexicoColor],
        width: int = 2,
    ) -> None:
        """Draw a line."""
        color_obj = parse_color(color)
        rgba = color_obj.to_rgba_tuple()

        # Convert coordinates
        px1, py1 = self._convert_coords(x1, y1)
        px2, py2 = self._convert_coords(x2, y2)

        px1, py1 = self._apply_transform(px1, py1)
        px2, py2 = self._apply_transform(px2, py2)

        self._draw.line([px1, py1, px2, py2], fill=rgba, width=width)

    def polygon(
        self,
        points: List[Tuple[Union[int, float], Union[int, float]]],
        color: Union[str, GulfOfMexicoColor],
        fill: bool = True,
    ) -> None:
        """Draw a polygon from a list of (x, y) points."""
        color_obj = parse_color(color)
        rgba = color_obj.to_rgba_tuple()

        # Convert all points
        converted_points = []
        for x, y in points:
            px, py = self._convert_coords(x, y)
            px, py = self._apply_transform(px, py)
            converted_points.append((px, py))

        if fill:
            self._draw.polygon(converted_points, fill=rgba)
        else:
            self._draw.polygon(converted_points, outline=rgba)

    def text(
        self,
        text: str,
        x: Union[int, float],
        y: Union[int, float],
        color: Union[str, GulfOfMexicoColor],
        size: int = 16,
    ) -> None:
        """Draw text."""
        color_obj = parse_color(color)
        rgba = color_obj.to_rgba_tuple()

        # Convert coordinates
        px, py = self._convert_coords(x, y)
        px, py = self._apply_transform(px, py)

        try:
            font = ImageFont.truetype("DejaVuSans.ttf", size)
        except:
            font = ImageFont.load_default()

        self._draw.text((px, py), text, fill=rgba, font=font)

    # Transformation methods
    def save_transform(self) -> None:
        """Save current transformation state."""
        self._transform_stack.append(self._current_transform.copy())

    def restore_transform(self) -> None:
        """Restore previous transformation state."""
        if self._transform_stack:
            self._current_transform = self._transform_stack.pop()

    def translate(self, x: Union[int, float], y: Union[int, float]) -> None:
        """Add translation to current transform."""
        tx, ty = self._current_transform["translate"]
        self._current_transform["translate"] = (tx + x, ty + y)

    def rotate(self, angle: Union[int, float]) -> None:
        """Add rotation (in degrees) to current transform."""
        self._current_transform["rotate"] += angle

    def scale(
        self, sx: Union[int, float], sy: Optional[Union[int, float]] = None
    ) -> None:
        """Add scaling to current transform."""
        if sy is None:
            sy = sx
        current_sx, current_sy = self._current_transform["scale"]
        self._current_transform["scale"] = (current_sx * sx, current_sy * sy)

    # I/O methods
    def save(self, filepath: str) -> None:
        """Save the canvas to an image file."""
        self._image.save(filepath)

    def show(self) -> None:
        """Display the canvas (opens in default image viewer)."""
        self._image.show()

    def get_pixel(
        self, x: Union[int, float], y: Union[int, float]
    ) -> Tuple[int, int, int, int]:
        """Get the RGBA value of a pixel."""
        px, py = self._convert_coords(x, y)
        px, py = int(px), int(py)

        if 0 <= px < self.width and 0 <= py < self.height:
            return self._image.getpixel((px, py))
        return (0, 0, 0, 0)

    @property
    def image(self) -> Image.Image:
        """Access the underlying PIL Image."""
        return self._image
