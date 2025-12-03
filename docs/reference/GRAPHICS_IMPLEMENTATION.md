# Gulf of Mexico — Graphics System

Complete graphics implementation: -1 based coordinates, fractional indexing, three-valued color logic, and drawing primitives.

### Core Features

1. **-1 Based Coordinate System**
   - Top-left corner is `(-1, -1)` matching Gulf of Mexico's array indexing
   - All coordinates shifted by +1 internally for PIL compatibility

2. **Fractional Pixel Indexing**
   - Can draw pixels at fractional coordinates like `(0.5, 0.5)`
   - Implements blending to nearby pixels for smooth rendering

3. **Three-Valued Color Logic**
   - Colors support `maybe` values for probabilistic rendering
   - `Color(255, maybe, 0)` creates red with random green channel
   - Named color `"maybe"` is fully probabilistic

4. **Drawing Primitives**
   - `rect(x, y, width, height, color)` - rectangles
   - `circle(x, y, radius, color)` - circles
   - `line(x1, y1, x2, y2, color)` - lines
   - `polygon(points, color)` - polygons from point list
   - `text(text, x, y, color, size)` - text rendering
   - `pixel(x, y, color)` - single pixel with fractional support

5. **Transformation Stack**
   - `translate(x, y)` - move origin
   - `rotate(angle)` - rotate in degrees
   - `scale(sx, sy)` - scale drawing
   - `saveTransform()` / `restoreTransform()` - save/restore state

6. **I/O Operations**
   - `save(filepath)` - save to PNG/JPEG/etc
   - `show()` - display in image viewer

### File Structure

```
gulfofmexico/graphics/
├── __init__.py      # Module exports
├── canvas.py        # GulfOfMexicoCanvas class
└── colors.py        # GulfOfMexicoColor class and named colors
```

### Integration with builtin.py

Added two new builtin functions:
- `Canvas(width, height, background)` - create a canvas
- `Color(r, g, b, a)` - create a color

Canvas objects expose methods via namespace:
- Drawing: rect, circle, line, polygon, text, pixel
- Transform: translate, rotate, scale, saveTransform, restoreTransform
- I/O: save, show, clear
- Properties: width, height

### Dependencies

- **Pillow** (PIL Fork) - optional dependency for graphics
- Install with: `pip install Pillow` or `pip install -e .[graphics]`

### Example Usage

```gom
// Create a canvas (syntax uses = for function call assignment)
const canvas = Canvas(800, 600, "white")!

// Draw with -1 based coords
canvas.rect(-1, -1, 100, 100, "red")!
canvas.circle(200, 200, 50, "blue")!

// Probabilistic colors
const randomColor = Color(maybe, maybe, maybe)!
canvas.rect(100, 100, 50, 50, randomColor)!

// Save the result
canvas.save("output.png")!
```

### Status

✅ Graphics module created
✅ Canvas class with -1 indexing implemented
✅ Color system with maybe support
✅ All drawing primitives
✅ Transformation stack
✅ Integration with builtin.py
✅ Pillow added to pyproject.toml
🔧 Method signatures need arg count fixes
⏳ Example programs need syntax corrections
⏳ Full testing pending
⏳ Documentation pending

### Known Issues

1. Method wrapper functions need proper arg counts (currently using -1 variadic)
2. Example programs created but need Gulf of Mexico syntax corrections
3. Need to verify all drawing operations work correctly
4. Documentation needs to be written

### Next Steps

1. Fix arg counts in builtin.py canvas method wrappers
2. Test each drawing primitive individually
3. Update example programs with correct syntax
4. Create comprehensive GRAPHICS_GUIDE.md
5. Add graphics examples to README.md
6. Consider adding more features:
   - Image loading
   - Filters/effects
   - Animation support
   - Reactive canvas updates with `when` statements
