# Gulf of Mexico

An esoteric programming language interpreter based on [Lu Wilson (TodePond)](https://todepond.com)'s conceptual design. Gulf of Mexico features -1 based indexing, three-valued booleans, significant whitespace for operator binding, tiered equality, temporal variable lifetimes, and statement terminators with confidence levels.

## Quick Start

```bash
# Clone and install
git clone https://github.com/James-HoneyBadger/GulfOfMexico.git
cd GulfOfMexico
pip install -e .

# Run a program
python -m gulfofmexico examples/01_hello_world.gom

# Start the REPL
python -m gulfofmexico

# Launch the graphical IDE (requires PySide6)
pip install -e ".[ide]"
python -m gulfofmexico.ide
```

Or use the convenience scripts at the project root:

```bash
./run_cli.sh           # Start the REPL
./run_ide.sh           # Launch the IDE
```

## Language Overview

Every statement ends with `!` (the "confidence terminator"). More `!` marks indicate higher confidence.

```
print "Hello, World!"!
print "Definitely prints"!!!
```

### Variables

```
const name = "GOM"!        // immutable
var counter = 0!            // mutable
var counter = counter + 1!  // reassign
```

### Types

| Type | Examples |
|------|---------|
| Number | `42`, `3.14`, `-7` |
| String | `"hello"`, `'world'` |
| Boolean | `true`, `false`, `maybe` |
| List | `[1, 2, 3]` |
| Map | `Map()` |
| Undefined | `undefined` |

### -1 Based Indexing

Arrays, strings, and numbers all start at index `-1`:

```
const arr = [10, 20, 30]!
print arr[-1]!   // 10 (first element)
print arr[0]!    // 20 (second element)
print arr[1]!    // 30 (third element)
```

### Three-Valued Booleans

```
const a = true!
const b = false!
const c = maybe!           // evaluates probabilistically
Boolean(0)    // false
Boolean(1)    // true
Boolean(0.3)  // maybe (fractional -> maybe)
```

### Functions

Functions are declared with `function` (or `fn`, `func`, `f`) and use `=>` with curly braces:

```
function add(a, b) => {
   return a + b!
}!

function greet(name) => {
   print "Hello, ${name}!"!
}!

// Single-arg functions can be called with space syntax
greet "World"!

// Multi-arg functions use parenthesized calls
const sum = add(3, 7)!
```

### Control Flow

```
// Conditionals
if x > 10 {
   print "big"!
}

// Recursion (no traditional loops)
function countdown(n) => {
   if n > 0 {
      print n!
      const next = n - 1!
      countdown(next)!
   }
}!
```

### Significant Whitespace

Whitespace controls operator binding — tight binding groups operands:

```
const a = 2 * 1+3!   // 2 * (1+3) = 8
const b = 2*1 + 3!   // (2*1) + 3 = 5
```

### Tiered Equality

Four levels of precision in equality checks:

| Operator | Meaning | `10 = 11` | `10 == 11` | `10 === 10` |
|----------|---------|-----------|------------|-------------|
| `=` | Approximate (within 10) | `true` | — | — |
| `==` | Exact value | — | `false` | `true` |
| `===` | Value + type | — | — | `true` |
| `====` | Reference identity | — | — | — |

### Classes

GOM enforces single-instance-per-class:

```
class Counter {
   var count = 0!
   function increment() => {
      count = count + 1!
   }!
}!

const c = new Counter!
c.increment()!
print c.count!    // 1
```

### String Interpolation

Multiple currency symbols work as interpolation prefixes:

```
const val = 42!
print "${val}"!     // Dollar
print "£{val}"!     // Pound
print "¥{val}"!     // Yen
```

### Special Features

| Feature | Syntax | Description |
|---------|--------|-------------|
| Variable lifetimes | `var x <5> = "temp"!` | Variable expires after 5 statements |
| Previous values | `previous x` | Access the prior value of a variable |
| When watchers | `when x > 5 { ... }` | Execute block when condition becomes true |
| Next promises | `const f = next x!` | Capture the next value of a variable |
| Reverse replay | `reverse!` | Replay prior statements in reverse order |
| Delete | `delete x!` | Remove a variable from scope |
| Word numbers | `five`, `nineteen`, `hundred(3)` | English word number literals |
| Named fractions | `half`, `quarter`, `third` | Fraction literals |
| Signals | `const sig = use 0!` | Reactive signal (getter/setter) |
| Type annotations | `var x: Int = 10!` | Optional type hints |
| Noop | `noop!` | Do nothing |

### Math Functions

17 built-in math functions: `abs`, `floor`, `ceil`, `round`, `sqrt`, `sin`, `cos`, `tan`, `log`, `exp`, `degrees`, `radians`, `pow`, `min`, `max`, `random`, `randomInt`.

```
print abs(-5)!        // 5
print sqrt(16)!       // 4.0
print min(3, 7)!      // 3
print randomInt(1, 6)! // random integer 1-6
```

## CLI Usage

```
python -m gulfofmexico                   # REPL
python -m gulfofmexico script.gom        # Run file
python -m gulfofmexico -c "print 42!"    # Inline code
python -m gulfofmexico -s script.gom     # Show Python traceback on error
python -m gulfofmexico --debug script.gom  # Show internal debug messages
```

## REPL Commands

| Command | Description |
|---------|-------------|
| `:help` | Show help |
| `:quit` | Exit REPL |
| `:reset` | Clear state |
| `:load <file>` | Load and execute a file |
| `:vars` | Show all variables |
| `:history` | Show command history |
| `:save <file>` | Save history to file |

## Project Structure

```
gulfofmexico/               # Main interpreter package
├── __init__.py             # Entry point (run_file)
├── __main__.py             # CLI interface
├── base.py                 # Token, TokenType, OperatorType, error formatting
├── builtin.py              # Value types, built-in functions, keywords
├── repl.py                 # Interactive REPL
├── serialize.py            # Value serialization for persistence
├── interpreter/            # Interpreter core (11 modules)
│   ├── context.py          # Shared state, type aliases, ReturnSentinel
│   ├── helpers.py          # Utility functions
│   ├── operators.py        # Tiered equality, comparison, arithmetic
│   ├── namespaces.py       # Scope lookup, literal resolution
│   ├── persistence.py      # Variable storage (file I/O)
│   ├── expressions.py      # Expression evaluation engine
│   ├── variables.py        # Variable declaration and assignment
│   ├── watchers.py         # When-statements, next/previous tracking
│   ├── dispatch.py         # Statement type determination
│   └── execution.py        # Main interpretation loop
├── processor/              # Front-end pipeline
│   ├── lexer.py            # Tokenizer
│   ├── syntax_tree.py      # Parser / statement generation
│   └── expression_tree.py  # Expression tree builder
└── ide/                    # Graphical IDE (PySide6)
    ├── app.py              # Main application window
    ├── editor.py           # Code editor widget
    ├── highlighter.py      # Syntax highlighting
    ├── runner.py           # Program execution
    └── qt_compat.py        # Qt compatibility layer

examples/                   # 21 example programs
tests/                      # Spec compliance and regression tests
docs/                       # Documentation
```

## Examples

21 example programs covering all language features, from hello world to sorting algorithms:

| # | Program | Concepts |
|---|---------|----------|
| 01 | Hello World | Print, confidence levels |
| 02 | Variables & Types | const/var, booleans, type conversion |
| 03 | Operators | Arithmetic, comparison, logical, string ops |
| 04 | Tiered Equality | `=`, `==`, `===`, `====` |
| 05 | Control Flow | if blocks, recursion |
| 06 | Functions | Definition, higher-order, recursion |
| 07 | Lists | Indexing, push/pop, concatenation |
| 08 | Strings | Interpolation, escape sequences, reversal |
| 09 | Three-Valued Logic | maybe, probabilistic execution |
| 10 | Classes | OOP, single-instance enforcement |
| 11 | Word Numbers | English number literals, fractions |
| 12 | Delete | Deleting variables and values |
| 13 | Maps | Key-value data structures |
| 14 | Algorithms | Recursive algorithms (factorial, fibonacci) |
| 15 | Debug & Confidence | `?` debug output, `!`/`!!`/`!!!` |
| 16 | Lifetimes | Temporal variable expiration |
| 17 | Multiple Returns | Returning lists as multiple values |
| 18 | Number Indexing | Indexing individual digits |
| 19 | Currency Interpolation | `${}`, `£{}`, `¥{}` |
| 20 | Bank Simulation | Full application with classes |
| 21 | Sorting | Insertion sort, functional style |

Run all examples:

```bash
for f in examples/*.gom; do
  echo "--- $(basename "$f") ---"
  python -m gulfofmexico "$f"
done
```

## Installation Options

```bash
pip install -e .              # Core interpreter only
pip install -e ".[ide]"       # + Graphical IDE (PySide6)
pip install -e ".[all]"       # All optional dependencies
```

Optional extras:
- `ide` — PySide6 graphical IDE
- `input` — pynput keyboard input
- `graphics` — Pillow image support
- `yaml` — YAML configuration files
- `globals` — GitHub-based public variable sharing

## Testing

```bash
# Run spec compliance test
python -m gulfofmexico tests/spec_compliance.gom

# Run all example programs
for f in examples/*.gom; do
  timeout 15 python -m gulfofmexico -s "$f"
done
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Credits

- **Original Design**: [Lu Wilson (TodePond)](https://todepond.com)
- **Implementation**: James Temple
