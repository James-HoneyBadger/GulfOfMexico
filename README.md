<p align="center">
  <h1 align="center">Gulf of Mexico</h1>
  <p align="center">
    An esoteric programming language where arrays start at <code>-1</code>, booleans have three values, and whitespace controls operator precedence.
  </p>
  <p align="center">
    <a href="https://github.com/James-HoneyBadger/GulfOfMexico/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
    <a href="https://pypi.org/project/gulfofmexico/"><img alt="PyPI" src="https://img.shields.io/pypi/v/gulfofmexico.svg"></a>
    <a href="https://www.python.org/downloads/"><img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-blue.svg"></a>
    <a href="https://github.com/James-HoneyBadger/GulfOfMexico/actions"><img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/James-HoneyBadger/GulfOfMexico/ci.yml?label=tests"></a>
  </p>
</p>

---

Gulf of Mexico is a production-ready interpreter and IDE for the language conceptually designed by [Lu Wilson (TodePond)](https://todepond.com). It features -1-based indexing, three-valued booleans (`true`, `false`, `maybe`), significant whitespace for operator binding, four tiers of equality, temporal variable lifetimes, word-number literals, and statement terminators with confidence levels.

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
| **Tiered equality** | `=` (approximate), `==` (loose), `===` (precise), `====` (same literal/identity). |
| **Tilde equality** | `~=` (AEMI), `~==` (ABI), `~===` (AQMI) — approximate match operators. |
| **Temporal lifetimes** | `var x <5> = "temp"!` — variable expires after 5 statements. |
| **Negative hoisting** | `const x<-1> = 42!` — variable available one line *before* declaration. |
| **Word numbers** | `five`, `nineteen`, `hundred(3)`, `half`, `quarter` — write numbers as English. |
| **Confidence terminators** | Statements end with `!`, `!!`, or `!!!` to indicate confidence. `?` for debug. |
| **No loops** | Recursion is the only iteration mechanism. |
| **Single-instance classes** | Each class can have at most one instance at a time. |
| **Emoji identifiers** | `const 🎉 = 42!` — use emoji as variable and function names. |
| **Compound assignment** | `+=`, `-=`, `*=`, `/=`, `^=` — modify-in-place operators. |
| **Currency interpolation** | `"${x}"`, `"£{x}"`, `"¥{x}"`, `"{x}€"`, `"{obj$prop}"` — currency symbols for interpolation. |
| **Polished tooling** | Compiler-style diagnostics, a versioned REPL, and terminal-aware colour. |
| **Four declaration forms** | `const const`, `const var`, `var const`, `var var` — control re-assignment and editing separately. |
| **Arbitrary quoting** | `'x'`, `'''x'''`, `""""x""""`, or even `x` — any number of quotes makes a string. |
| **Parentheses are whitespace** | `add(3, 2)`, `add 3, 2`, `(add (3, 2))`, and `add)3, 2(!` all call `add`. |
| **Automatic insertion** | AEMI/ABI/AQMI repair missing `!`, brackets, and closing quotes. |
| **Object literals** | `{ name: "Lu" }` creates a map; `player.name` / `{player$name}` read properties. |

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
10 = 11        // true   — approximate (within ~10%)
3.14 == "3.14" // true   — loose (cross-type coercion)
3.14 === "3.14" // false  — precise (value + type)
10 === 10      // true   — value + type
const pi = 3.14!
3.14 ==== 3.14 // true   — the same literal
3.14 ==== pi   // false  — a literal is not the variable
10 ;= 5        // true   — inequality (semicolon-equals)
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

### Standard Helpers

GOM has no loops, so list work is recursion — and the prelude supplies the usual
helpers, written in GOM itself, so any name can be shadowed:

```
function double(n) => {
   return n * 2!
}!

function isBig(n) => {
   return n > 2!
}!

const numbers = map(range(5), double)!
print numbers!                   // [0, 2, 4, 6, 8]
print sum(numbers)!              // 20
print filter(numbers, isBig)!    // [4, 6, 8]
```

`range`, `rangeFrom`, `map`, `filter`, `reduce`, `zip`, `take`, `reverseOf`,
`concat`, `sortBy`, `sum`, `maxOf`, and `minOf` are available. Set
`GOM_NO_PRELUDE=1` for a bare namespace.

### Reactive Features

```
// When-watchers: fire on mutation once the condition holds
var x = 0!
when x > 5 {
   print "x is now big!"!
}
x = 10!    // triggers the watcher

// Variable lifetimes
var temp <3> = "alive"!   // expires after 3 statements

// Previous, current, and next values
var y = 100!
y = 200!
print previous y!          // 100
print current y!           // 200

// Postfix increment/decrement update the variable
y++!
print y!                   // 201

// Signals: get and set with one callable
const var score = use(0)!
score(9)!
print score()!             // 9
```

## CLI Usage

```console
gom                          # Start the REPL
gom script.gom               # Run a file
gom -c "print 42!"           # Run inline code
gom - < script.gom           # Run a program from standard input
gom --check script.gom       # Parse and validate without running
gom --fmt script.gom         # Print the program in canonical layout
gom --fmt -w script.gom      # Rewrite the file in canonical layout
gom -s script.gom            # Show a Python traceback on error
gom --debug script.gom       # Show internal debug messages
gom --version                # Print the interpreter version
```

`python -m gulfofmexico` works identically to `gom`. `gom --help` documents the
modes, grouped options, environment variables, and examples.

| Flag | Effect |
|------|--------|
| `-c CODE` | Run inline code and exit |
| `-s`, `--show-traceback` | Print the full Python traceback on failure |
| `--debug` | Internal debug messages (`GULFOFMEXICO_DEBUG=1`) |
| `--verbose` | Completion message with elapsed time (`GULFOFMEXICO_VERBOSE=1`) |
| `--no-color` | Disable ANSI colour (also honours `NO_COLOR`) |
| `-q`, `--quiet` | Suppress non-essential messages |
| `--vars-json PATH` | Write the final variables as JSON (used by the IDE inspector) |
| `--check` | Parse and validate the program without running it |
| `--fmt` | Print the program in canonical layout (never reflows a line) |
| `-w`, `--write` | With `--fmt`, rewrite the file in place |
| `-V`, `--version` | Print the version and exit |

`--check` and `--fmt` work on `-c` code, on `-` (stdin), and on several files
at once. `gom --check --fmt file.gom` fails when the file is not canonically
formatted, which is how CI keeps every bundled example tidy — combine the two
flags for a formatting gate:

```console
$ gom --check --fmt examples/*.gom
error: examples/07_lists.gom: not formatted
  = hint: run 'gom --fmt -w examples/07_lists.gom' to rewrite it
```

Formatting is deliberately conservative: it normalises indentation to 3-space
levels (preserving block structure), strips trailing whitespace, collapses runs
of blank lines, and guarantees a single final newline. Spacing *within* a line is
never touched, because it decides operator-precedence ties, and lines inside
triple-quoted strings are left exactly as written.

Exit codes are `0` for success, `1` when the program fails, and `2` for bad
usage, so the CLI composes cleanly in scripts and CI.

### Diagnostics

Errors are reported in a compiler-style layout with the offending line, a caret
under the exact token, and a hint where one helps:

```console
$ gom broken.gom
error: Attempted to set a variable that cannot be set.
  --> broken.gom:2:1
  |
2 | name = "Lu"!
  | ^^^^
```

Colour is emitted only when the stream is a terminal, so piped output and CI
logs stay plain text. Set `NO_COLOR=1` (or pass `--no-color`) to opt out
everywhere, and `FORCE_COLOR=1` to opt in.

### IDE

The graphical IDE (`gom-ide`) restores your session, shows a live **Variables**
inspector after every run, an **Outline** of functions and classes, and a
console with clickable error locations. The window title tracks the active file
and unsaved changes.

Editing support: **autocomplete** (<kbd>Ctrl</kbd>+<kbd>Space</kbd>),
**find in files** (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>F</kbd>), **go to
symbol** (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>O</kbd>), **rename symbol**
(<kbd>F2</kbd>), **live diagnostics** as you type, **Run with Input**
(<kbd>Shift</kbd>+<kbd>F5</kbd>) to feed a program's standard input, and
**Stop** (<kbd>F6</kbd>).

### REPL

The REPL greets you with a version banner and a short cheat sheet, keeps
persistent history in `~/.gom_history`, completes keywords and in-scope names on
<kbd>Tab</kbd>, and evaluates multi-line input without losing track of braces
inside strings or comments. Results are rendered as values, never as Python
objects.

| Command | Description |
|---------|-------------|
| `:help` | Show commands and language hints |
| `:quit`, `:q` | Exit the REPL |
| `:reset` | Clear all state |
| `:vars` | Show a table of variables in scope |
| `:load <file>` | Load and execute a `.gom` file |
| `:open <file>` | Stage a file as the next input |
| `:history [n]` | List history, or show block `n` |
| `:run [n\|last]` | Re-execute a history block |
| `:save <file> [all\|last\|<n>]` | Save history to a file |
| `:clip [last\|<n>]` | Copy a block to the clipboard |

## Examples

49 example programs are included in [`examples/`](examples/), covering every feature of the language from hello world to recursive algorithms. See [examples/README.md](examples/README.md) for the full program index.

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
| **[Examples Index](examples/README.md)** | Categorized guide to all 49 example programs |
| **[Code of Conduct](CODE_OF_CONDUCT.md)** | Community standards |

## Project Structure

```
gulfofmexico/                   # Main package
├── __init__.py                 # Entry point — run_file()
├── __main__.py                 # CLI (argparse)
├── base.py                     # Token, TokenType, OperatorType, errors
├── builtin.py                  # Value types, built-in functions, keywords
├── repl.py                     # Interactive REPL
├── ui.py                       # Terminal presentation (diagnostics, colour, tables)
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

examples/                       # 49 example programs (.gom)
tests/                          # Unit, integration, spec, and UX tests
docs/                           # Language reference, architecture, guides
```

## Testing

```bash
# Run the full test suite
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
