# Gulf of Mexico — Architecture

Overview of the interpreter's internal architecture.

## Execution Pipeline

```
Source Code (.gom)
    │
    ▼
┌──────────────┐
│  Lexer       │  processor/lexer.py
│  (Tokenize)  │  Produces Token stream
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Parser      │  processor/syntax_tree.py
│  (Parse)     │  Produces statement tuples (CodeStatement)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Dispatch    │  interpreter/dispatch.py
│  (Classify)  │  Determines statement type (Assignment, Conditional, etc.)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Execution   │  interpreter/execution.py
│  (Execute)   │  Main interpretation loop
└──────────────┘
```

## Package Structure

### `gulfofmexico/` — Top-level package

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 141 | Entry point — `run_file()` reads source, splits multi-file sections, runs pipeline |
| `__main__.py` | 183 | CLI — argparse for file/REPL/inline modes, debug flags |
| `base.py` | 193 | Core types: Token, TokenType, OperatorType, error formatting with ANSI colors |
| `builtin.py` | ~1020 | All GOM value types, built-in functions, keyword registrations |
| `repl.py` | 473 | Interactive REPL with commands (`:help`, `:vars`, `:load`, etc.) |
| `serialize.py` | 203 | JSON serialization for variable persistence and export/import |

### `gulfofmexico/processor/` — Front-end pipeline

| File | Lines | Purpose |
|------|-------|---------|
| `lexer.py` | 323 | Tokenizer — converts source text to Token stream |
| `syntax_tree.py` | 941 | Parser — converts tokens to statement tuples (CodeStatement) |
| `expression_tree.py` | 475 | Expression tree builder — handles operator precedence and significant whitespace |

### `gulfofmexico/interpreter/` — Back-end interpreter

| File | Lines | Purpose |
|------|-------|---------|
| `context.py` | ~140 | `InterpreterContext` dataclass (shared mutable state), `ReturnSentinel`, type aliases |
| `helpers.py` | 87 | Small utilities (expression building, name mangling) |
| `operators.py` | 381 | Tiered equality (`=`/`==`/`===`/`====`), comparison, arithmetic on GOM values |
| `namespaces.py` | 131 | Scope lookup, literal-value resolution from token trees |
| `persistence.py` | 132 | File I/O for `const const const` variables, GitHub-based public globals |
| `expressions.py` | 562 | Expression evaluation engine, function call dispatch |
| `variables.py` | 359 | Variable declaration (`const`/`var`), assignment, lifetime tracking, watchers |
| `watchers.py` | 416 | When-statement registration, next/previous value tracking, name watchers |
| `dispatch.py` | 135 | Statement type determination — classifies raw tuples into typed statements |
| `execution.py` | 351 | Main interpretation loop — iterates over statements, dispatches to handlers |

### `gulfofmexico/ide/` — Graphical IDE

| File | Lines | Purpose |
|------|-------|---------|
| `app.py` | 654 | Main application window (PySide6/Qt) |
| `editor.py` | 99 | Code editor widget with line numbers |
| `highlighter.py` | 136 | Syntax highlighting for GOM keywords |
| `runner.py` | 84 | Background program execution |
| `qt_compat.py` | 50 | Qt version compatibility layer |

## Value Types

All GOM values are Python dataclasses defined in `builtin.py`:

| Type | Python Class | Description |
|------|-------------|-------------|
| Number | `GulfOfMexicoNumber` | Wraps `float`, digit-indexable |
| String | `GulfOfMexicoString` | Wraps `str`, char-indexable |
| Boolean | `GulfOfMexicoBoolean` | Three values: true/false/maybe |
| List | `GulfOfMexicoList` | Wraps `list`, -1 based indexing |
| Map | `GulfOfMexicoMap` | Key-value store |
| Function | `GulfOfMexicoFunction` | User-defined function |
| Class | `GulfOfMexicoClass` | Class definition |
| Instance | `GulfOfMexicoInstance` | Class instance (single per class) |
| Undefined | `GulfOfMexicoUndefined` | The undefined value |
| Date | `GulfOfMexicoDate` | Date/time |
| Regex | `GulfOfMexicoRegex` | Regular expression |

## Statement Types

Defined in `processor/syntax_tree.py` and dispatched in `interpreter/dispatch.py`:

- `PrintStatement` — output to stdout
- `VariableDeclaration` — `const`/`var` declarations
- `AssignmentStatement` — variable reassignment
- `IndexedAssignment` — `arr[i] = val`
- `DottedAssignment` — `obj.prop = val`
- `Conditional` — `if` blocks
- `FunctionDeclaration` — `function`/`fn`/`func`/`f`
- `ClassDeclaration` — `class` blocks
- `ReturnStatement` — `return` from function
- `WhenStatement` — reactive watcher
- `DeleteStatement` — `delete` variable
- `ImportStatement` — `import` from other sections
- `ExportStatement` — `export` to other sections
- `ReverseStatement` — `reverse!` replay
- `ExpressionStatement` — standalone expression evaluation

## Multi-File Support

Source files can contain multiple sections separated by `=====` markers:

```
===== utils =====
// This section defines utilities

===== main =====
// This section is the main program
```

Each section is tokenized and executed independently. Sections communicate via `export`/`import` statements.

## Environment Variables

| Variable | Effect |
|----------|--------|
| `GULFOFMEXICO_DEBUG` | Print internal debug messages to stderr |
| `GULFOFMEXICO_VERBOSE` | Show completion messages, wait for when-statements |
