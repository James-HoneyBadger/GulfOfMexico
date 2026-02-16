# Gulf of Mexico — Architecture Guide

Technical overview of the interpreter's internal architecture, execution pipeline, and module responsibilities.

---

## Table of Contents

1. [Execution Pipeline](#execution-pipeline)
2. [Package Map](#package-map)
3. [Front-End: Processor Package](#front-end-processor-package)
4. [Back-End: Interpreter Package](#back-end-interpreter-package)
5. [Top-Level Modules](#top-level-modules)
6. [IDE Package](#ide-package)
7. [Value Type Hierarchy](#value-type-hierarchy)
8. [Statement Types](#statement-types)
9. [Expression Tree Nodes](#expression-tree-nodes)
10. [Dependency Graph](#dependency-graph)
11. [Key Design Decisions](#key-design-decisions)

---

## Execution Pipeline

A Gulf of Mexico program flows through four stages:

```
Source Code (.gom file or inline string)
        │
        ▼
┌─────────────────┐
│  1. TOKENIZER   │  processor/lexer.py
│                 │  Source text → Token stream
│                 │  Handles: quotes, comments, whitespace tracking,
│                 │  escape sequences, ¡, ()
└────────┬────────┘
         │  list[Token]
         ▼
┌─────────────────┐
│  2. PARSER      │  processor/syntax_tree.py
│                 │  Tokens → Statement tuples (CodeStatement)
│                 │  Handles: statement splitting by !/?, indentation
│                 │  validation, scoped blocks, type annotation
│                 │  extraction, ambiguous parse generation
└────────┬────────┘
         │  list[CodeStatement]  (each is a tuple of possible parses)
         ▼
┌─────────────────┐
│  3. DISPATCH    │  interpreter/dispatch.py
│                 │  Resolve ambiguous statement tuples to a single
│                 │  concrete type by inspecting runtime namespace
│                 │  values (keyword checks)
└────────┬────────┘
         │  Concrete statement (VariableDeclaration, Conditional, etc.)
         ▼
┌─────────────────┐
│  4. EXECUTION   │  interpreter/execution.py
│                 │  Walk statements, evaluate expressions, manage
│                 │  namespaces, handle reactive features, run
│                 │  import/export between file sections
└─────────────────┘
```

**Multi-file support**: Source files may contain multiple sections separated by `=====` markers. Each section runs through the full pipeline independently. Sections communicate via `export`/`import`, with values serialized through `serialize.py`.

---

## Package Map

```
gulfofmexico/                     # Top-level package
├── __init__.py                   #   run_file() — orchestrates the full pipeline
├── __main__.py                   #   CLI entry point (argparse)
├── base.py                       #   Core types: Token, TokenType, OperatorType, errors
├── builtin.py                    #   All GOM value types, built-in functions, KEYWORDS dict
├── repl.py                       #   Interactive REPL with meta-commands
├── serialize.py                  #   JSON-safe serialization/deserialization of GOM values
│
├── processor/                    #   FRONT-END (source → AST)
│   ├── __init__.py               #     Re-exports: tokenize, generate_syntax_tree
│   ├── lexer.py                  #     Tokenizer
│   ├── syntax_tree.py            #     Statement parser + AST node definitions
│   └── expression_tree.py        #     Expression tree builder + node definitions
│
├── interpreter/                  #   BACK-END (AST → execution)
│   ├── __init__.py               #     Re-exports public API
│   ├── context.py                #     InterpreterContext dataclass, type aliases, constants
│   ├── dispatch.py               #     Statement type resolution
│   ├── execution.py              #     Main interpretation loop
│   ├── expressions.py            #     Expression evaluation engine
│   ├── variables.py              #     Variable declaration and assignment
│   ├── operators.py              #     Tiered equality, comparison, arithmetic
│   ├── namespaces.py             #     Scope lookup, literal-value resolution
│   ├── watchers.py               #     When-statements, next/previous tracking
│   ├── persistence.py            #     File I/O for persistent variables
│   └── helpers.py                #     Small utility functions
│
└── ide/                          #   GRAPHICAL IDE (optional, PySide6)
    ├── __init__.py               #     Package docstring
    ├── __main__.py               #     IDE launcher (argparse)
    ├── app.py                    #     Main window, menus, session management
    ├── editor.py                 #     Code editor widget with line numbers
    ├── highlighter.py            #     Syntax highlighting using the production tokenizer
    ├── runner.py                 #     Threaded program execution with output capture
    └── qt_compat.py              #     PySide6/PyQt5 compatibility layer
```

---

## Front-End: Processor Package

The processor package converts source text into an abstract syntax tree. It has no runtime dependencies — it only imports from `base.py`.

### `lexer.py` — Tokenizer

Converts source code into a flat list of `Token` objects. Each token carries its type, value, line number, column, and the **amount of whitespace before it** (critical for significant-whitespace operator precedence).

Key features:
- Matched quote counting (number of opening quotes must equal closing quotes)
- Single-line (`//`) and block (`/* */`) comments
- Triple-quoted strings
- Escape sequence processing
- Parentheses-as-whitespace
- The empty value `()`
- Inverted exclamation mark `¡`

### `syntax_tree.py` — Statement Parser

Converts a token stream into a list of `CodeStatement` tuples. Each `CodeStatement` is a **tuple of possible interpretations** — the same tokens might parse as either a `VariableAssignment` or an `ExpressionStatement`, for instance. Ambiguity is resolved at runtime by `dispatch.py`.

Also defines all 13 statement AST node types (see [Statement Types](#statement-types)).

Key features:
- Statement splitting by `!`, `?`, and `}` terminators
- Indentation validation (multiples of 3 spaces)
- Scoped block parsing (curly braces)
- Type annotation extraction and removal
- Function definition parsing

### `expression_tree.py` — Expression Tree Builder

Converts a span of tokens into a tree of `ExpressionTreeNode` objects, implementing GOM's unique **significant-whitespace operator precedence**: operators with less surrounding whitespace bind tighter.

Also defines all 6 expression node types (see [Expression Tree Nodes](#expression-tree-nodes)).

Key features:
- Whitespace-based operator precedence (wider spacing = lower precedence)
- Function call detection via spacing heuristics
- List literal parsing
- Index expression parsing
- Unary operator handling

---

## Back-End: Interpreter Package

The interpreter package executes the AST. All modules share mutable state through `InterpreterContext`.

### `context.py` — Shared State

Defines `InterpreterContext`, the central dataclass that carries all mutable execution state:
- `filename`, `code` — source location metadata
- `namespaces` — stack of scope dictionaries (`list[Namespace]`)
- `async_statements` — queued async statement blocks
- `when_statement_watchers` — registered when-statement conditions
- `imports/exports` — inter-section data transfer
- `deleted_values` — set of deleted GOM values
- `verbose`, `show_tb` — runtime flags

Also defines `ReturnSentinel` (distinguishes explicit `return` from implicit expression results), type aliases (`Namespace`, `AsyncStatements`, `WhenStatementWatchers`), and constants (equality ratios, persistence file paths).

### `dispatch.py` — Statement Classification

Resolves ambiguous `CodeStatement` tuples to a single concrete statement type. Checks whether names in the statement refer to keywords in the current namespace, then selects the most specific match. Falls back to `VariableAssignment` → `ExpressionStatement`.

### `execution.py` — Main Loop

The core interpretation loop. Contains three public functions:

- **`interpret_code_statements_main_wrapper()`** — Top-level entry point. Sets up the interpreter context, runs the statement list, and handles async statement queuing.
- **`interpret_code_statements()`** — Recursive inner loop. Iterates over statements, dispatches each to the appropriate handler, manages lifetime decrements, and processes when-watcher triggers.
- **`execute_conditional()`** — Evaluates `if` blocks with three-valued boolean support (when the condition is `maybe`, the block executes probabilistically).

### `expressions.py` — Expression Evaluator

Evaluates `ExpressionTreeNode` trees to produce GOM values. This is the largest interpreter module.

Key responsibilities:
- Value/name lookup in namespaces
- Binary and unary operator evaluation (delegates to `operators.py`)
- Function call dispatch (user-defined and built-in)
- String interpolation with currency symbols (`${}`, `£{}`, `¥{}`, `{}€`)
- Escape sequence processing in string literals
- `await`/`next`/`previous` keyword handling
- List literal construction
- Index expression evaluation
- Constructor (`new`) calls with single-instance enforcement
- Async function registration

### `variables.py` — Declaration and Assignment

Handles `const`/`var` declarations and variable reassignment.

Key responsibilities:
- Mutability enforcement (const vs var)
- Lifetime attachment (`<N>` syntax)
- Confidence level attachment (`~N~` syntax)
- `const const const` persistent immutables (delegates to `persistence.py`)
- Destructuring assignment
- Dotted property assignment (`obj.prop = val`)
- Indexed assignment (`arr[i] = val`) with recursive drill-down
- When-watcher trigger evaluation after assignment
- Next-promise resolution
- `Date.now` settable clock support

### `operators.py` — Operator Implementation

Implements all GOM operators on GOM value types.

Key features:
- **Four-tiered equality**: `is_approx_equal()`, `is_equal()`, `is_really_equal()`, `is_really_really_equal()`
- Approximate equality uses `SequenceMatcher` for strings and numeric tolerance for numbers
- Three-valued logical operators (`maybe` handled probabilistically via `random()`)
- Unary minus: negates numbers, reverses strings and lists
- Logical NOT via `;`: `;true` → `false`, `;maybe` → `maybe`

### `namespaces.py` — Scope Lookup

Searches the namespace stack (most-local scope first) for variable names.

Key features:
- Dotted-name resolution (`obj.prop.subprop`)
- Literal-value resolution (bare numbers, zero-quote strings, booleans, `undefined`)
- Returns both the resolved `Name` and the containing `Namespace`

### `watchers.py` — Reactive Features

Implements GOM's reactive programming constructs.

Key features:
- When-statement registration and condition re-evaluation
- `next`/`previous` expression rewriting and tracking
- Name-watcher callbacks for deferred execution
- Async-next blocking wait
- Temporary namespace cleanup

### `persistence.py` — File I/O

Manages persistent variable storage on disk.

Key features:
- `const const const` immutable globals (saved/loaded via `pickle` in `~/.gulfofmexico_runtime/`)
- Infinite-lifetime variable persistence
- GitHub-based public global variable loading (optional, requires `pygithub`)

### `helpers.py` — Utilities

Small, dependency-free utility functions:
- `get_built_expression()` — converts token lists to expression trees
- `get_modified_next_name()` / `get_modified_prev_name()` — name mangling for next/previous tracking
- `gather_names_or_values()` — extracts all name tokens from expression trees
- `check_type_annotation()` — stub type annotation validator

---

## Top-Level Modules

### `base.py` — Core Types

Foundation module with zero intra-package dependencies. Defines:

- **`Token`** — dataclass with `type`, `value`, `line`, `column`, `whitespace_before`
- **`TokenType`** — enum of all token types (NAME, NUMBER, STRING, OPERATOR, PUNCTUATION, etc.)
- **`OperatorType`** — enum of binary operators (ADD, SUBTRACT, MULTIPLY, etc.)
- **`InterpretationError`** / **`NonFormattedError`** — error classes
- **`raise_error_at_token()`** / **`raise_error_at_line()`** — error formatting with ANSI-colored source location
- **`is_alph_num()`** — Unicode-aware identifier character check
- **`STR_TO_OPERATOR`** — mapping from operator strings to `OperatorType`

### `builtin.py` — Value Types and Built-ins

The largest module (~1025 lines). Defines all GOM value types as Python dataclasses and registers all built-in functions/keywords.

**Value type hierarchy**:

```
GulfOfMexicoValue (abstract base)
├── GulfOfMexicoNumber        # wraps float, digit-indexable
├── GulfOfMexicoString        # wraps str, char-indexable
├── GulfOfMexicoBoolean       # three values: true/false/maybe
├── GulfOfMexicoList          # wraps list, -1-based, push/pop
├── GulfOfMexicoMap           # key-value store
├── GulfOfMexicoFunction      # user-defined function (stores CodeStatement body)
├── GulfOfMexicoObject        # class instance
├── GulfOfMexicoUndefined     # the undefined value
├── GulfOfMexicoKeyword       # language keyword placeholder
├── GulfOfMexicoPromise       # next-value promise
├── GulfOfMexicoPendingInit   # sentinel during class construction
└── GulfOfMexicoSpecialBlankValue  # the empty value ()
```

Mixin classes:
- `GulfOfMexicoMutable` — marks types that support mutation
- `GulfOfMexicoIndexable` — marks types that support `[]` indexing
- `GulfOfMexicoNamespaceable` — marks types with `.` property access

Also defines:
- `Name` — a named binding (wraps a string identifier)
- `Variable` — pairs a `Name` with a value plus metadata (const/var, lifetime, confidence)
- `VariableLifetime` — tracks remaining statement count or time
- `BuiltinFunction` — wraps Python callables as GOM functions
- `KEYWORDS` — master dict of all built-in keywords, values, and functions
- Word number keywords (`zero`–`nineteen`, `twenty`–`ninety`, `hundred`, `thousand`, `million`)
- Named fractions (`half`, `third`, `quarter`)
- Math function keywords (`abs`, `sqrt`, `sin`, etc.)

### `serialize.py` — Serialization

JSON-compatible serialization and deserialization of GOM values and Python objects. Used for:
- `export`/`import` data transfer between file sections
- `const const const` persistent storage

Avoids `eval()` — uses safe type lookup by class name.

### `repl.py` — Interactive REPL

Full-featured REPL with persistent state across inputs.

Features:
- Multi-line input with automatic continuation detection
- Meta-commands (`:help`, `:quit`, `:reset`, `:load`, `:vars`, `:history`, `:save`, `:open`, `:run`, `:clip`)
- Clipboard integration
- Command history
- Error handling with optional traceback display

---

## IDE Package

Optional graphical IDE built on PySide6 (with PyQt5 fallback).

### `app.py` — Main Window

`MainWindow(QMainWindow)` with:
- Multi-tab code editor
- Console output dock
- Menus: File (new/open/save/recent), Edit, Run (run/stop)
- Keyboard shortcuts (Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+R, etc.)
- Session persistence (window geometry, open files)
- Threaded code execution via `Worker(QObject)` to keep UI responsive

### `editor.py` — Code Editor

`CodeEditor(QPlainTextEdit)` with:
- Line number gutter (`LineNumberArea`)
- Current-line highlighting
- Tab-width configuration (3 spaces per GOM spec)

### `highlighter.py` — Syntax Highlighting

Uses the production `lexer.tokenize()` function to tokenize each line, then applies One Dark-style colors:
- Keywords → purple
- Names → red
- Numbers → orange
- Strings → green
- Operators → cyan
- Punctuation → yellow

### `runner.py` — Execution

`ExecutionSession` maintains persistent interpreter state. `run_code()` captures stdout via a thread-safe `OutputCapture(StringIO)` and returns `(output, error)`.

### `qt_compat.py` — Compatibility

Tries `PySide6` first, falls back to `PyQt5`. Exports a unified set of Qt classes used by the other IDE modules.

---

## Value Type Hierarchy

```
GulfOfMexicoValue (ABC)
│
├── GulfOfMexicoMutable (mixin)
│   ├── GulfOfMexicoList
│   ├── GulfOfMexicoMap
│   └── GulfOfMexicoObject
│
├── GulfOfMexicoIndexable (mixin)
│   ├── GulfOfMexicoList
│   ├── GulfOfMexicoString
│   └── GulfOfMexicoNumber
│
├── GulfOfMexicoNamespaceable (mixin)
│   └── GulfOfMexicoObject
│
├── Immutable values
│   ├── GulfOfMexicoNumber
│   ├── GulfOfMexicoString
│   ├── GulfOfMexicoBoolean
│   ├── GulfOfMexicoUndefined
│   └── GulfOfMexicoFunction
│
└── Internal types
    ├── GulfOfMexicoKeyword
    ├── GulfOfMexicoPromise
    ├── GulfOfMexicoPendingInit
    └── GulfOfMexicoSpecialBlankValue
```

---

## Statement Types

Defined in `processor/syntax_tree.py`:

| Type | Syntax | Description |
|------|--------|-------------|
| `VariableDeclaration` | `const x = 1!` | New variable (const or var) |
| `VariableAssignment` | `x = 2!` | Reassign existing variable |
| `Conditional` | `if expr { ... }` | If block |
| `FunctionDefinition` | `function f() => { ... }!` | Function declaration |
| `ClassDeclaration` | `class C { ... }!` | Class declaration |
| `ReturnStatement` | `return expr!` | Return from function |
| `DeleteStatement` | `delete x!` | Remove variable |
| `ReverseStatement` | `reverse!` | Reverse replay |
| `WhenStatement` | `when expr { ... }` | Reactive watcher |
| `AfterStatement` | `after expr { ... }` | Delayed execution |
| `ExportStatement` | `export x to y!` | Export to another section |
| `ImportStatement` | `import x from y!` | Import from another section |
| `ExpressionStatement` | `f(x)!` | Standalone expression |

---

## Expression Tree Nodes

Defined in `processor/expression_tree.py`:

| Node | Description |
|------|-------------|
| `ValueNode` | Leaf — a single token (name, number, string, boolean) |
| `ExpressionNode` | Binary operation — left, operator, right |
| `SingleOperatorNode` | Unary operation — operator, operand |
| `FunctionNode` | Function call — function expr, argument exprs |
| `IndexNode` | Index access — target expr, index expr |
| `ListNode` | List literal — list of element exprs |

---

## Dependency Graph

```
                    base.py
                   ╱       ╲
          processor/        builtin.py ←── serialize.py
         ╱    |    ╲              ╲
   lexer  syntax  expression    interpreter/
     .py   _tree    _tree      ╱  |  |  |  ╲
            .py      .py    ctx  dispt exec  ...
                              ╲   |    ↕   ╱
                            expressions ←→ execution  (circular, broken by late imports)
                                  ↕
                             variables ←→ watchers
```

### Circular Dependencies

Three circular import chains exist in the interpreter package. They are broken by **late imports** inside function bodies:

1. **`expressions.py` ↔ `execution.py`** — Expression evaluation needs to execute if-blocks; execution needs to evaluate expressions.
2. **`variables.py` → `execution.py`** — Variable assignment may trigger conditional execution (when-watchers).
3. **`watchers.py` → `execution.py`** — When-watcher firing needs to execute statement blocks.

---

## Key Design Decisions

### Why tuples of possible parses?

GOM's syntax is inherently ambiguous — `greet "hello"` could be a function call or a variable assignment followed by a string literal. The parser generates **all valid interpretations** as a tuple, and `dispatch.py` resolves the ambiguity at runtime by checking whether names refer to keywords, functions, or variables.

### Why significant whitespace for operators?

This is a core language design feature from Lu Wilson's specification. The `expression_tree.py` builder calculates operator precedence by measuring the total whitespace on both sides of each operator token. Less whitespace = higher precedence.

### Why no loop constructs?

GOM intentionally omits `for`, `while`, and `do` loops. All iteration must be expressed as recursion. This is a deliberate design constraint from the language specification.

### Why single-instance classes?

Each class can have at most one live instance. Creating a new instance of a class replaces any prior instance. This is an intentional language constraint that enforces a unique object model.

### Why -1-based indexing?

Arrays, strings, and numbers all start indexing at `-1` instead of `0` or `1`. This is the signature feature of the language design: `arr[-1]` returns the **first** element, `arr[0]` returns the second.

---

*This architecture guide describes Gulf of Mexico v0.2.0. For the full language specification, see [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md).*
