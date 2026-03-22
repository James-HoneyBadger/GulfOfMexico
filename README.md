<p align="center">
  <h1 align="center">Gulf of Mexico</h1>
  <p align="center">
    An esoteric programming language where arrays start at <code>-1</code>, booleans have three values, and whitespace controls operator precedence.
  </p>
  <p align="center">
    <a href="https://github.com/James-HoneyBadger/GulfOfMexico/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
    <a href="https://pypi.org/project/gulfofmexico/"><img alt="PyPI" src="https://img.shields.io/pypi/v/gulfofmexico.svg"></a>
    <a href="https://www.python.org/downloads/"><img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-blue.svg"></a>
    <a href="https://github.com/James-HoneyBadger/GulfOfMexico/actions"><img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/James-HoneyBadger/GulfOfMexico/test.yml?label=tests"></a>
  </p>
</p>

---

Gulf of Mexico is an experimental interpreter for the language conceptually designed by [Lu Wilson (TodePond)](https://todepond.com). It features -1-based indexing, three-valued booleans (`true`, `false`, `maybe`), significant whitespace for operator binding, four tiers of equality, temporal variable lifetimes, word-number literals, and statement terminators with confidence levels.

```
print "Hello, World!"!
print "I am VERY sure this prints."!!
print "I am ABSOLUTELY sure this prints."!!!
```

## Highlights

| Feature | What it does |
|---------|-------------|
| **-1-based indexing** | `[10, 20, 30][-1]` → `10`. Arrays, strings, and numbers all start at `-1`. |
| **Three-valued booleans** | `maybe` evaluates probabilistically — `if maybe { ... }` runs ~50% of the time. |
| **Significant whitespace** | `2 * 1+3` = `8` but `2*1 + 3` = `5`. Tighter spacing binds harder. |
| **Tiered equality** | `=` (approximate), `==` (exact), `===` (strict), `====` (identity). |
| **Tilde equality** | `~=` (AEMI), `~==` (ABI), `~===` (AQMI) — approximate match operators. |
| **Temporal lifetimes** | `var x <5> = "temp"!` — variable expires after 5 statements. |
| **Negative hoisting** | `const x<-1> = 42!` — variable available one line *before* declaration. |
| **Word numbers** | `five`, `nineteen`, `hundred(3)`, `half`, `quarter` — write numbers as English. |
| **Confidence terminators** | Statements end with `!`, `!!`, or `!!!` to indicate confidence. `?` for debug. |
| **No loops** | Recursion is the only iteration mechanism. |
| **Single-instance classes** | Each class can have at most one instance at a time. |
| **Emoji identifiers** | `const 🎉 = 42!` — use emoji as variable and function names. |
| **Compound assignment** | `+=`, `-=`, `*=`, `/=`, `^=` — modify-in-place operators. |
| **Currency interpolation** | `"${x}"`, `"£{x}"`, `"¥{x}"` — three currency symbols for string interpolation. |

## Quick Start

```bash
# Install from PyPI
pip install gulfofmexico

# — or install from source —
git clone https://github.com/James-HoneyBadger/GulfOfMexico.git
cd GulfOfMexico
pip install -e .

# Run a program
gom examples/01_hello_world.gom

# Start the interactive REPL
gom

# Launch the graphical IDE (requires PySide6)
pip install gulfofmexico[ide]
gom-ide
```

> **Convenience scripts** are also provided at the project root: `./run_cli.sh` and `./run_ide.sh`.

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for detailed platform-specific setup instructions.

## Language at a Glance

### Variables and Types

```
const name = "GOM"!        // immutable
var counter = 0!            // mutable
var counter = counter + 1!  // reassign

// Types: Number, String, Boolean, List, Map, Undefined
const pi = 3.14!
const flag = maybe!
const items = [1, 2, 3]!
```

### -1-Based Indexing

```
const arr = [10, 20, 30]!
print arr[-1]!    // 10 — first element
print arr[0]!     // 20 — second element
print arr[1]!     // 30 — third element
```

### Significant Whitespace

Whitespace controls operator binding — tighter spacing groups first:

```
const a = 2 * 1+3!    // 2 * (1+3) = 8
const b = 2*1 + 3!    // (2*1) + 3 = 5
```

### Three-Valued Booleans

```
const a = true!       // always true
const b = false!      // always false
const c = maybe!      // true ~50% of the time

;true                 // false  (semicolon = NOT)
;maybe                // maybe
```

### Tiered Equality

```
10 = 11       // true   — approximate (within ~10%)
10 == 11      // false  — exact value
10 == 10      // true
10 === 10     // true   — value + type
10 ;= 5       // true   — inequality (semicolon-equals)
```

### Tilde Equality

```
5 ~= 10           // true   — AEMI: same type → true
5 ~= "hello"      // maybe  — different type → maybe
"Hello" ~== "hello"  // true — ABI: case-insensitive
100 ~=== 100.5    // true   — AQMI: within 1%
```

### Functions

```
function add(a, b) => {
   return a + b!
}!

// Single-arg: call with space syntax
function greet(name) => {
   print "Hello, ${name}!"!
}!

greet "World"!            // space syntax
const sum = add(3, 7)!    // parenthesized call
```

### Control Flow (No Loops!)

```
function countdown(n) => {
   if n > 0 {
      print n!
      const prev = n - 1!
      countdown(prev)!
   }
}!
countdown(5)!
```

### Classes (Single Instance)

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

### Reactive Features

```
// When-watchers: fire when condition becomes true
var x = 0!
when x > 5 {
   print "x is now big!"!
}
x = 10!    // triggers the watcher

// Variable lifetimes
var temp <3> = "alive"!   // expires after 3 statements

// Previous values
var y = 100!
y = 200!
print previous y!          // 100
```

## CLI Usage

```
gom                          # Start the REPL
gom script.gom               # Run a file
gom -c "print 42!"           # Run inline code
gom -s script.gom            # Show Python traceback on error
gom --debug script.gom       # Show internal debug messages
```

The `python -m gulfofmexico` invocation works identically to `gom`.

### REPL Commands

| Command | Description |
|---------|-------------|
| `:help` | Show help |
| `:quit` | Exit REPL |
| `:reset` | Clear all state |
| `:load <file>` | Load and execute a `.gom` file |
| `:vars` | Show all variables in scope |
| `:history` | Show command history |
| `:save <file>` | Save history to a file |
| `:open <file>` | Open file in default editor |
| `:run <file>` | Run a file and keep state |
| `:clip` | Copy last output to clipboard |

## Examples

26 example programs are included in [`examples/`](examples/), covering every feature of the language from hello world to recursive algorithms. See [examples/README.md](examples/README.md) for the full program index.

```bash
# Run a single example
gom examples/01_hello_world.gom

# Run all examples
for f in examples/*.gom; do
  echo "--- $(basename "$f") ---"
  gom "$f"
done
```

## Documentation

| Document | Description |
|----------|-------------|
| **[Language Reference](docs/LANGUAGE_REFERENCE.md)** | Complete syntax and semantics for every language feature |
| **[Architecture Guide](docs/ARCHITECTURE.md)** | Interpreter internals, execution pipeline, and module map |
| **[Installation Guide](docs/INSTALLATION.md)** | Platform-specific setup, virtual environments, extras |
| **[Contributing Guide](CONTRIBUTING.md)** | How to contribute, coding standards, and testing workflow |
| **[Changelog](docs/CHANGELOG.md)** | Version history and release notes |
| **[Examples Index](examples/README.md)** | Annotated guide to all 26 example programs |
| **[Code of Conduct](CODE_OF_CONDUCT.md)** | Community standards |

## Project Structure

```
gulfofmexico/                   # Main package
├── __init__.py                 # Entry point — run_file()
├── __main__.py                 # CLI (argparse)
├── base.py                     # Token, TokenType, OperatorType, errors
├── builtin.py                  # Value types, built-in functions, keywords
├── repl.py                     # Interactive REPL
├── serialize.py                # Value serialization for persistence
├── processor/                  # Front-end pipeline
│   ├── lexer.py                #   Tokenizer (source → tokens)
│   ├── syntax_tree.py          #   Statement parser (tokens → AST)
│   └── expression_tree.py      #   Expression tree builder
├── interpreter/                # Back-end execution engine
│   ├── context.py              #   InterpreterContext, type aliases
│   ├── dispatch.py             #   Statement type classification
│   ├── execution.py            #   Main interpretation loop
│   ├── expressions.py          #   Expression evaluator
│   ├── variables.py            #   Declaration, assignment, lifetimes
│   ├── operators.py            #   Tiered equality, arithmetic, logic
│   ├── namespaces.py           #   Scope lookup, literal resolution
│   ├── watchers.py             #   When-statements, next/previous
│   ├── persistence.py          #   File I/O for persistent variables
│   └── helpers.py              #   Small utilities
└── ide/                        # Graphical IDE (optional, PySide6)
    ├── app.py                  #   Main window
    ├── editor.py               #   Code editor with line numbers
    ├── highlighter.py          #   Syntax highlighting
    ├── runner.py               #   Background execution
    └── qt_compat.py            #   PySide6 / PyQt5 compatibility

examples/                       # 26 example programs (.gom)
tests/                          # 170 unit + integration tests
docs/                           # Language reference, architecture, guides
```

## Testing

```bash
# Run the full test suite (170 tests)
python -m pytest

# Run spec compliance directly
gom tests/spec_compliance.gom
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full testing workflow.

## Installation Options

```bash
pip install gulfofmexico            # Core interpreter
pip install gulfofmexico[ide]       # + Graphical IDE (PySide6)
pip install gulfofmexico[all]       # All optional extras
```

| Extra | Package | Feature |
|-------|---------|---------|
| `ide` | PySide6 | Graphical IDE with 7 themes, movable panels, settings dialog, and syntax highlighting |
| `input` | pynput | Keyboard input support |
| `graphics` | Pillow | Image processing |
| `yaml` | PyYAML | YAML configuration files |
| `globals` | PyGithub | GitHub-based public variable sharing |

## License

MIT License — see [LICENSE](LICENSE) for details.

## Credits

- **Language Design** — [Lu Wilson (TodePond)](https://todepond.com)
- **Implementation** — [James Temple](https://github.com/James-HoneyBadger)
