#!/usr/bin/env python3
"""
Create a colorful Mandelbrot-style fractal image
"""
from PIL import Image, ImageDraw


def create_mandelbrot_art(width=600, height=400, filename="mandelbrot.png"):
    """Create a colorful fractal-like pattern"""
    # Create image
    img = Image.new("RGB", (width, height), color="#000033")
    draw = ImageDraw.Draw(img)

    # Create color palette (dark blue to white)
    colors = [
        "#000033",
        "#000066",
        "#000099",
        "#0000CC",
        "#0000FF",
        "#3333FF",
        "#6666FF",
        "#9999FF",
        "#CCCCFF",
        "#FFFFFF",
    ]

    # Draw horizontal gradient bands
    band_height = height // len(colors)
    for i, color in enumerate(colors):
        y = i * band_height
        draw.rectangle([0, y, width, y + band_height], fill=color)

    # Draw concentric circles to simulate Mandelbrot bulb
    center_x, center_y = width // 2, height // 2
    for i in range(10, 0, -1):
        radius = i * 15
        color_idx = min(9 - i, len(colors) - 1)
        color = colors[color_idx]
        draw.ellipse(
            [
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ],
            fill=color,
        )

    # Add smaller satellite circles
    satellites = [
        (width // 3, height // 2, 40),
        (2 * width // 3, height // 2, 40),
        (width // 2, height // 4, 30),
        (width // 2, 3 * height // 4, 30),
    ]

    for sx, sy, sradius in satellites:
        for i in range(3, 0, -1):
            r = sradius * i // 3
            color_idx = min(6 + i, len(colors) - 1)
            color = colors[color_idx]
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=color)

    # Save
    img.save(filename)
    print(f"Created {filename} ({width}x{height})")


if __name__ == "__main__":
    create_mandelbrot_art()
