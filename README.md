# GOM - Gulf of Mexico Programming Language

This implementation is based on the conceptual design of **Gulf of Mexico**, the perfect programming language created by Lu Wilson (TodePond) (https://github.com/TodePond/GulfOfMexico).

## 🚀 Two Implementations

**Gulf of Mexico** provides both an **interpreter** (Python) and a **compiler** (C++) with 100% feature parity!

### Python Interpreter
- Full-featured REPL with IDE
- Perfect for development and prototyping
- Rich debugging and interactive features

### C++ Compiler ⚡ NEW!
- **10-100x faster** than the interpreter
- Compiles to native executables
- **34 built-in functions** (math, statistics, finance, business, scientific)
- **70+ satirical keywords** (blockchain, ai_powered, happy, sprint, etc.)
- **Map/Dictionary support** with -1 array indexing
- Production-ready performance

See [CONSOLIDATION_COMPLETE.md](CONSOLIDATION_COMPLETE.md) for full compiler documentation.

## Installation

```bash
git clone https://github.com/James-HoneyBadger/GulfOfMexico.git
cd GulfOfMexico
pip install -e .

# Build the compiler (optional, for high performance)
cd compiler/build
cmake ..
make -j4
```

## Usage

### Python Interpreter
```bash
# Run a program
python -m gulfofmexico script.gom

# Interactive REPL
python -m gulfofmexico

# Execute inline code
python -m gulfofmexico -c "print(42)!"

# Launch IDE
python -m gulfofmexico.ide
```

### C++ Compiler
```bash
# Compile a program
cd compiler/build
./gomcc program.gom -o program.cpp
g++ -std=c++17 program.cpp -o program
./program

# Example with built-in functions
./gomcc ../examples/test_analysis.gom -o test.cpp
g++ -std=c++17 test.cpp -o test
./test
```

### REPL quick start

```bash
python -m gulfofmexico.repl
```

Inside the REPL you can load files (including multi-file demos with `=====` sections):

```text
:load programs/01_basics/01_hello_world.gom
:load programs/demos/grand_deluxe_demo.gom
```

Handy commands: `:vars`, `:history [n]`, `:run [n|last]`, `:reset`, `:quit`.
See USER_GUIDE.md → "Using the REPL" for more.

## Core Language Features

### Arrays Start at -1
```
const nums [10, 20, 30]!
print(nums[-1])!  // 10
print(nums[0])!   // 20
```

### Fractional Indexing
```
const list [1, 3]!
list[0.5] = 2!
// Result: [1, 2, 3]
```

### Probabilistic Variables
```
var x 10!    // Confidence 1
var x 20!!   // Confidence 2 (wins)
var x 30!!!  // Confidence 3 (highest)
```

### Variable Lifetimes
```
const temp <5.0> = 99!     // Expires in 5 seconds
const brief 100 = 42!      // Expires after 100 lines
```

### Three-Valued Logic
```
const yes true!
const no false!
const maybe maybe!
```

### Reactive Programming
```
var count 0!

when count > 5 {
   print("Count exceeded 5!")!
}

count = 10!  // Triggers when statement
```

### Async Functions
```
async function fetch() => {
   return 42!
}!

const result await(fetch())!
```

### String Interpolation
```
const name "Alice"!
print("Hello, ${name}!")!
```

## 📊 Built-in Functions (Compiler Only)

The C++ compiler includes 34 built-in functions for math, statistics, finance, and more!

### Math Functions (12)
```javascript
sqrt(144)           // → 12.0
pow(2, 8)           // → 256.0
sin(1.5708)         // → 1.0
abs(-42)            // → 42.0
floor(3.7)          // → 3.0
// Also: cos, tan, ceil, round, log, log10, exp
```

### Statistical Functions (7)
```javascript
const data = [10, 20, 30, 40, 50]!
mean(data)          // → 30.0
median(data)        // → 30.0
stdev(data)         // → 15.81
// Also: variance, min_val, max_val, sum_list
```

### Financial Functions (3)
```javascript
compound_interest(1000, 0.05, 10, 12)  // → 1647.01
simple_interest(1000, 0.05, 10)         // → 1500.0
pmt(0.05, 12, 1000)                     // → 112.83
```

### Business Functions (3)
```javascript
roi(1500, 1000)           // → 50.0% ROI
profit_margin(1500, 1000) // → 33.33% margin
cagr(1000, 2000, 5)       // → 14.87% annual growth
```

### Scientific Functions (2)
```javascript
linear_regression([1,2,3,4,5], [2,4,6,8,10])  // → [2.0, 0.0]
quadratic_solve(1, -5, 6)                      // → [3.0, 2.0]
```

See [BUILTIN_FUNCTIONS.md](BUILTIN_FUNCTIONS.md) for complete reference.

## 🎭 Satirical Features

Gulf of Mexico includes experimental satirical features that make programming... interesting:

### Emotional Programming 😊😢😠
Programs can have feelings! Execution changes based on mood:

```
happy {
   print "Everything is great!"!
}

tired {
   print "Ugh, fine, I'll do it..."!
}
```

Moods: `happy` (no errors), `sad` (1-2 errors), `angry` (3+ errors), `excited` (70% random), `tired` (always, with delay)

### Superstitious Programming 🍀
Let luck decide your code's fate:

```
lucky {
   risky_operation()!
}

cross_fingers {
   maybe_works()!
}
```

Types: `lucky` (optimistic), `unlucky` (pessimistic), `cross_fingers` (50/50), `knock_on_wood` (error suppression)

### Procrastination Keywords ⏰
Why do now what you can do... eventually?

```
later {
   // 50% chance of execution
}

eventually {
   // 75% chance  
}

whenever {
   // 90% chance
}
```

### Corporate Speak 💼
Synergize your paradigms!

```
synergize x, y!           // Combine values
leverage value!           // Multiply by 2
paradigm_shift value!     // Negate/reverse
circle_back!              // No-op (naturally)
touch_base!               // Print corporate wisdom
```

### Passive-Aggressive Error Handling
```
try {
   risky_code()!
} whatever {
   print "Meh, didn't work"!
}
```

### Quantum Programming ⚛️
Variables exist in superposition until observed:

```
quantum x [1, 2, 3, 4, 5]!       // Superposition of 5 states
const result = observe("x")!      // Collapses to single value
quantum uncertain maybe!          // true/false superposition
```

### Time Travel ⏰
Access past and future variable states:

```
var x 10!
x = 20!
x = 30!

const old_val = past("x", 2)!    // Returns 10
const prediction = future("x")!   // Random prediction
```

**See `programs/demos/grand_deluxe_demo.gom` for all features in action!**

## 📚 Example Programs

Over **80 example programs** organized by category:

- **`programs/01_basics/`** - Core language features (hello world, variables, arrays, functions, classes)
- **`programs/02_features/`** - Advanced features (equality, three-valued logic, reactive, async, lifetimes)
- **`programs/03_graphics/`** - Graphics and visualization (canvas, transforms, generative art, Mandelbrot)
- **`programs/04_satirical/`** - Satirical keywords (emotional, superstitious, corporate, quantum, time travel)
- **`programs/05_analysis/`** - Data analysis (base conversion, statistics, finance, business, scientific)
- **`programs/06_compiler_tests/`** - C++ compiler test programs
- **`programs/demos/`** - Complete demo applications (banking, calculator, task manager, RPG character)
- **`programs/tests/`** - Unit and integration tests

See [programs/README.md](programs/README.md) for complete documentation and syntax guidelines.

### Quick Examples

```bash
# Core basics
python -m gulfofmexico programs/01_basics/01_hello_world.gom
python -m gulfofmexico programs/01_basics/05_functions.gom

# Advanced features
python -m gulfofmexico programs/02_features/10_reactive.gom
python -m gulfofmexico programs/02_features/12_async.gom

# Graphics
python -m gulfofmexico programs/03_graphics/19_mandelbrot.gom

# Satirical fun
python -m gulfofmexico programs/04_satirical/25_ultimate_satire.gom

# Ultimate showcase (all features)
python -m gulfofmexico programs/demos/grand_deluxe_demo.gom
```

## Syntax

### Variables
```
const x 10!          // Immutable
var y 20!            // Mutable  
const var z [1,2]!   // Mutable content, immutable reference
```

### Functions
```
function add(a, b) => a + b!

fn multiply(x, y) => x * y!  // Short form
```

**Call Syntax:**
- Functions with arguments: `add 5 3!` or `add(5, 3)!`
- Zero-arg functions: `getValue()!` (parentheses required)
- Methods: `obj.method()!` (zero-arg) or `obj.method arg!` (with args)

See TECHNICAL_REFERENCE.md for complete call syntax rules.

### Classes
```
class Person {
   var name "Unknown"!
   var age 0!
   
   function init(n, a) => {
      name = n!
      age = a!
   }!
   
   function greet() => {
      print("Hi, I'm ${name}")!
   }!
}!

const alice = new(Person, "Alice", 30)!  // With constructor args
const bob = new Person!                   // Without args (uses defaults)
alice.greet()!  // Zero-arg method requires parentheses
```

**Constructors**: Classes with an `init` method support constructor arguments via `new(Class, arg1, arg2)`. Requires parentheses.

### Control Flow
```
if condition {
   // code
}

when condition {
   // reactive
}

after <2.0> {
   // delayed
}
```

## Operators

**Arithmetic:** `+` `-` `*` `/` `^`

**Comparison:** `<` `>` `<=` `>=`

**Equality:**
- `=` Approximate
- `==` Standard
- `===` Strict
- `====` Strictest

**Logical:** `&` `|` `;` (not)

## Built-in Functions

- `print()` - Output
- `Number()` `String()` `Boolean()` - Type conversion
- `read()` `write()` - File I/O
- `Map()` - Create dictionary
- `sleep()` `exit()` - Control
- `regex_match()` `regex_findall()` `regex_replace()` - Regex
- Math functions: `sin` `cos` `sqrt` `log` etc.
- Word numbers: `zero` through `nineteen`, `twenty()` `thirty()` etc.

## Debug Output

```
const x 10?      // Level 1
const y 20??     // Level 2
const z 30???    // Level 3
const w 40????   // Level 4
```

## Multi-File Programs

```
===== utils =====
function helper() => 42!
export helper to main!

===== main =====
import helper!
print(helper())!
```
## IDE

```bash
python -m gulfofmexico.ide       # Qt GUI with web fallback
python -m gulfofmexico.ide --web # Force web interface
./run_web_ide.sh                 # Convenience script for web IDE
```

Web IDE: `http://localhost:8080/ide`

The Web IDE includes embedded examples and supports loading any `.gom` file from the programs directory. Try loading `programs/demos/grand_deluxe_demo.gom` to see all features in action!
Web IDE: `http://localhost:8080/ide`

## Requirements

- Python 3.10+
- requests (required)
- pynput (optional)
- pygithub (optional)
- PySide6/PyQt5 (optional, for Qt IDE)

## Author

James Temple  
Email: james@honey-badger.org  
GitHub: [James-HoneyBadger](https://github.com/James-HoneyBadger)

## License

This is free and unencumbered software released into the public domain.
