# Gulf of Mexico Programs

This directory contains example programs, demos, and tests for the Gulf of Mexico programming language.

## Directory Structure

```
programs/
├── 01_basics/              Core language features
│   ├── 01_hello_world.gom
│   ├── 02_variables.gom
│   ├── 03_arrays.gom
│   ├── 04_probabilistic.gom
│   ├── 05_functions.gom
│   ├── 06_classes.gom
│   └── 07_conditionals.gom
│
├── 02_features/            Advanced language features
│   ├── 08_equality.gom
│   ├── 09_three_valued_logic.gom
│   ├── 10_reactive.gom
│   ├── 11_lifetimes.gom
│   ├── 12_async.gom
│   ├── 13_string_interpolation.gom
│   ├── 14_arithmetic.gom
│   └── 15_word_numbers.gom
│
├── 03_graphics/            Graphics and visualization
│   ├── 16_graphics.gom
│   ├── 17_graphics_transforms.gom
│   ├── 18_generative_art.gom
│   ├── 19_mandelbrot.gom
│   └── mandelbrot_simple.gom
│
├── 04_satirical/           Satirical/comedy language features
│   ├── 19_passive_aggressive_errors.gom
│   ├── 20_procrastination.gom
│   ├── 21_corporate_speak.gom
│   ├── 22_satirical_showcase.gom
│   ├── 23_emotional_programming.gom
│   ├── 24_superstitious_programming.gom
│   ├── 25_ultimate_satire.gom
│   ├── 26_quantum_programming.gom
│   ├── 27_time_travel.gom
│   ├── 28_quantum_time_spectacular.gom
│   ├── 29_gaslighting_variables.gom
│   ├── 30_blockchain_satire.gom
│   ├── 31_ai_buzzwords.gom
│   ├── 32_agile_scrum.gom
│   ├── 33_security_theater.gom
│   ├── 34_devops_cargo_cult.gom
│   └── 35_startup_culture.gom
│
├── 05_analysis/            Math, stats, finance, science
│   ├── 36_base_numbers.gom
│   ├── 37_base_simple.gom
│   ├── 38_base_practical.gom
│   ├── 39_statistics.gom
│   ├── 40_financial.gom
│   ├── 41_business.gom
│   └── 42_scientific.gom
│
├── demos/                  Complete demo applications
│   ├── grand_deluxe_demo.gom     ★ Ultimate feature showcase
│   ├── async_pipeline.gom
│   ├── banking_system.gom
│   ├── calculator.gom
│   ├── feature_showcase.gom
│   ├── multi_file.gom
│   ├── reactive_counter.gom
│   ├── rpg_character.gom
│   └── task_manager.gom
│
└── examples/               Legacy examples folder
    └── 00_complete_showcase.gom
```

## Quick Start

### Run a Program

```bash
# Using the interpreter
python3 -m gulfofmexico programs/01_basics/01_hello_world.gom

# Using the Web IDE
./run_web_ide.sh
# Then click "Load" and select a program
```

### Compile and Run (C++ Compiler)

```bash
cd compiler/build
./gomcc ../examples/test_builtins.gom -o output.cpp
g++ -std=c++17 output.cpp -o program
./program
```

## Language Features by Category

### 01_basics - Core Language
- **Hello World**: Basic print statements
- **Variables**: `const const`, `const var`, `var const`, `var var`
- **Arrays**: Start at index -1, fractional indexing
- **Probabilistic**: Confidence levels with `!` markers
- **Functions**: Arrow syntax `=>`, multiple forms
- **Classes**: Object-oriented patterns
- **Conditionals**: if/else with three-valued logic

### 02_features - Advanced Features
- **Equality**: `==`, `===`, `====`, `~=` (approximate)
- **Three-Valued Logic**: `true`, `false`, `maybe`
- **Reactive**: `when` statements for reactivity
- **Lifetimes**: Temporal keywords (`previous`, `current`, `future`)
- **Async/Await**: Asynchronous programming
- **String Interpolation**: `"Hello ${name}"`
- **Arithmetic**: Standard math operations
- **Word Numbers**: Natural language numbers

### 03_graphics - Graphics & Visualization
- **Canvas API**: Drawing shapes, colors, pixels
- **Transforms**: Rotation, scaling, translation
- **Generative Art**: Algorithmic art creation
- **Mandelbrot Set**: Fractal generation

### 04_satirical - Comedy Features
70+ satirical keywords including:
- `happy`, `sad`, `angry`, `confused`
- `blockchain`, `ai_powered`, `quantum`
- `agile`, `sprint`, `synergize`
- `eventually`, `probably`, `definitely`
- Many more hilarious programming concepts!

### 05_analysis - Data & Math
- **Base Conversion**: Binary, hex, custom bases
- **Statistics**: mean, median, stdev, variance, correlation
- **Financial**: compound interest, NPV, PMT
- **Business**: ROI, profit margins, CAGR
- **Scientific**: linear regression, derivatives, integration

 

## Syntax Guidelines

### Indentation
**IMPORTANT**: Gulf of Mexico requires indentation in multiples of **3 spaces**.

```gom
// ✓ Correct (3 spaces)
function example() => {
   print("Hello")!
}!

// ✗ Wrong (4 spaces)
function example() => {
    print("Hello")!
}!
```

### Function Calls
Functions use **space-separated** arguments without parentheses:

```gom
// ✓ Correct
const sum = add 3, 5!
print("Result:", sum)!

// ✗ Wrong - can't nest function calls in print
print(add 3, 5)!  // Error!
```

### Array Indexing
Arrays start at **-1**:

```gom
const arr = [10, 20, 30]!
print(arr[-1])!  // 10 (first element)
print(arr[0])!   // 20 (second element)
print(arr[1])!   // 30 (third element)
```

### Statement Terminators
All statements end with `!`:

```gom
print("Hello")!
const x = 42!
return x + 1!
```

## Running Tests

```bash
# Run all examples in a category
for f in programs/01_basics/*.gom; do
    echo "Testing $f"
    timeout 3 python3 -m gulfofmexico "$f"
done

# Run specific test suite
python3 -m pytest tests/  # Python tests
cd compiler/build && ./run_tests.sh  # Compiler tests
```

## Contributing

When adding new programs:
1. Use 3-space indentation
2. Follow the function call syntax (space-separated args)
3. End all statements with `!`
4. Add to the appropriate category folder
5. Update this README if adding new categories

## Web IDE

The grand_deluxe_demo.gom is specifically designed for the Web IDE and showcases:
- ✓ All core language features
- ✓ Built-in functions (math, stats, finance, etc.)
- ✓ Reactive programming
- ✓ Async/await
- ✓ Map/Dictionary support
- ✓ Satirical keywords
- ✓ Regex utilities

Access the Web IDE:
```bash
./run_web_ide.sh
# Opens browser at http://localhost:8080/ide
# Click "Load" → Select "programs/demos/grand_deluxe_demo.gom"
```

## Language Quirks & Features

- **-1 Indexing**: Arrays start at -1
- **Fractional Indexing**: Insert between elements with `arr[0.5] = value`
- **Probabilistic Variables**: Multiple declarations with `!` confidence levels
- **Three-Valued Booleans**: `true`, `false`, and `maybe`
- **Satirical Keywords**: 70+ keywords like `blockchain`, `ai_powered`, etc.
- **Temporal Access**: `previous x`, `current x`, `future x`
- **Reactive Programming**: `when condition { ... }`
- **String/Number Indexing**: Access digits and characters with `[]`

## See Also

- `/PROGRAMMING_GUIDE.md` - Complete language reference
- `/TECHNICAL_REFERENCE.md` - Implementation details
- `/compiler/README.md` - C++ compiler documentation
- `/gulfofmexico/ide/` - Web IDE source code
