# Contributing to Gulf of Mexico

Thank you for your interest in contributing to Gulf of Mexico! This guide covers everything you need to know to get started.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Project Layout](#project-layout)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Making Changes](#making-changes)
7. [Pull Request Process](#pull-request-process)
8. [Issue Guidelines](#issue-guidelines)
9. [Adding Language Features](#adding-language-features)
10. [Adding Examples](#adding-examples)

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally.
3. **Create a branch** for your work.
4. **Make changes**, write tests, and verify everything passes.
5. **Push** and open a **Pull Request**.

---

## Development Setup

### Prerequisites

- Python 3.10+
- Git

### Clone and install

```bash
git clone https://github.com/<your-username>/GulfOfMexico.git
cd GulfOfMexico
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
```

### Install dev dependencies

Dev dependencies (pytest, ruff, pylint, pre-commit) are managed via Poetry groups:

```bash
# With Poetry
poetry install --with dev

# Without Poetry — install manually
pip install pytest ruff pylint pre-commit
```

### Set up pre-commit hooks (optional but recommended)

```bash
pre-commit install
```

This runs linting checks automatically before each commit.

---

## Project Layout

```
gulfofmexico/
├── base.py                  # Core types (Token, errors) — no internal imports
├── builtin.py               # Value types, built-in functions, KEYWORDS
├── serialize.py             # Value serialization
├── repl.py                  # Interactive REPL
├── processor/               # Front-end: source → AST
│   ├── lexer.py             #   Tokenizer
│   ├── syntax_tree.py       #   Statement parser
│   └── expression_tree.py   #   Expression tree builder
├── interpreter/             # Back-end: AST → execution
│   ├── context.py           #   Shared state (InterpreterContext)
│   ├── dispatch.py          #   Statement type resolution
│   ├── execution.py         #   Main loop
│   ├── expressions.py       #   Expression evaluator
│   ├── variables.py         #   Declaration & assignment
│   ├── operators.py         #   Equality, comparison, arithmetic
│   ├── namespaces.py        #   Scope lookup
│   ├── watchers.py          #   Reactive features
│   ├── persistence.py       #   File I/O
│   └── helpers.py           #   Utilities
└── ide/                     # GUI IDE (PySide6)
```

**Key rule**: `base.py` has zero intra-package imports and is the dependency root. `processor/` modules depend only on `base.py`. `interpreter/` modules can depend on both `base.py`, `builtin.py`, and `processor/`.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a full architecture guide.

---

## Coding Standards

### Style

- **Line length**: 120 characters max.
- **Indentation**: 4 spaces (standard Python — note: GOM source uses 3 spaces, but the interpreter's Python code uses 4).
- **Linter**: [Ruff](https://docs.astral.sh/ruff/) — config is in `pyproject.toml`.
- **Imports**: Group by stdlib → third-party → local. Use absolute imports for cross-package references (`from gulfofmexico.base import ...`), relative imports within a package (`from .context import ...`).

### Naming

- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- GOM value types: prefixed with `GulfOfMexico` (e.g., `GulfOfMexicoNumber`)

### Type hints

- Use type annotations on all public function signatures.
- Use `from __future__ import annotations` for forward references.
- Prefer `Optional[X]` over `X | None` for Python 3.10 compatibility.

### Linting

```bash
# Run ruff
ruff check gulfofmexico/

# Run ruff with auto-fix
ruff check --fix gulfofmexico/

# Run pylint (optional, stricter)
pylint gulfofmexico/
```

---

## Testing

### Running tests

```bash
# Run the full test suite
python -m pytest

# Run with verbose output
python -m pytest -v

# Run a specific test
python -m pytest tests/test_examples.py::test_spec_compliance_output

# Stop on first failure
python -m pytest -x
```

### Test structure

| File | Purpose |
|------|---------|
| `tests/test_examples.py` | Runs all `.gom` example programs and test files via subprocess |
| `tests/spec_compliance.gom` | Comprehensive GOM-language test (25+ rules) |
| `tests/test_comments.gom` | Comment syntax test |

### What the tests verify

- **`test_example_runs_successfully`** — Every `.gom` file in `examples/` must exit with code 0.
- **`test_gom_test_file`** — Every `.gom` file in `tests/` (except `spec_compliance.gom`) must exit with code 0.
- **`test_spec_compliance_output`** — `spec_compliance.gom` must print `ALL TESTS COMPLETE` in its output.

### Writing new tests

For language-level tests, add assertions in `tests/spec_compliance.gom` or create a new `.gom` test file in `tests/`. Test files must:

1. Exit with code 0 on success.
2. Use `print` to output results for verification.
3. Not rely on interactive input (`read`).

For Python-level tests, add functions in `tests/test_examples.py` or create new `test_*.py` files in `tests/`.

---

## Making Changes

### Branch naming

Use descriptive branch names:

- `feature/word-numbers` — new feature
- `fix/string-indexing` — bug fix
- `docs/installation-guide` — documentation
- `refactor/split-execution` — code restructuring

### Commit messages

Write clear, concise commit messages:

```
fix: correct -1-based indexing for string slicing

The string indexer was using 0-based offset calculation.
Adjusted to use idx + 1 per the GOM spec.
```

Format: `type: short description`

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Before submitting

1. **Run the tests**: `python -m pytest`
2. **Run the linter**: `ruff check gulfofmexico/`
3. **Run spec compliance**: `gom tests/spec_compliance.gom`
4. **Check all examples**: `for f in examples/*.gom; do gom "$f" || echo "FAIL: $f"; done`

---

## Pull Request Process

1. Ensure all tests pass and linting is clean.
2. Update documentation if your change affects user-facing behavior.
3. Add or update examples if you've added a new language feature.
4. Update `docs/CHANGELOG.md` with your changes.
5. Open a PR against the `main` branch.
6. Describe what your change does and why.
7. Link any related issues.

### PR checklist

- [ ] Tests pass (`python -m pytest`)
- [ ] Linter clean (`ruff check gulfofmexico/`)
- [ ] Spec compliance passes (`gom tests/spec_compliance.gom`)
- [ ] Documentation updated (if applicable)
- [ ] Changelog updated (if applicable)
- [ ] Examples added/updated (if new feature)

---

## Issue Guidelines

### Bug reports

Include:
- Python version (`python --version`)
- OS and version
- GOM version (`pip show gulfofmexico`)
- Minimal `.gom` code that reproduces the issue
- Expected vs actual behavior
- Full error output (use `gom -s script.gom` for Python tracebacks)

### Feature requests

Include:
- Description of the proposed feature
- Example `.gom` syntax showing how it would work
- Whether it aligns with Lu Wilson's language specification

---

## Adding Language Features

If you're adding a new language feature, you'll typically need to touch several files:

### 1. Tokenizer changes (`processor/lexer.py`)

If the feature introduces new syntax tokens (new operators, new keywords), add them to the tokenizer.

### 2. Parser changes (`processor/syntax_tree.py`)

Add a new statement type dataclass and update `generate_syntax_tree()` to recognize the new syntax.

### 3. Keyword registration (`builtin.py`)

Register new keywords in the `KEYWORDS` dict so the dispatcher can recognize them.

### 4. Execution (`interpreter/execution.py`)

Add a handler for the new statement type in `interpret_code_statements()`.

### 5. Tests

Add test cases in `tests/spec_compliance.gom`.

### 6. Example

Create a new numbered example in `examples/` and update `examples/README.md`.

### 7. Documentation

Update `docs/LANGUAGE_REFERENCE.md` with the new feature's syntax and semantics.

---

## Adding Examples

Examples are numbered sequentially and live in `examples/`:

```
examples/
├── 01_hello_world.gom
├── 02_variables_and_types.gom
├── ...
└── 21_sorting.gom
```

### Guidelines for examples

1. **Number sequentially** — use the next available number.
2. **Start with a comment** explaining what the example demonstrates.
3. **Keep it focused** — each example should demonstrate one concept or a small set of related concepts.
4. **Include output** — use `print` statements so the output is visible when run.
5. **No interactive input** — examples should run without user interaction (no `read` calls).
6. **Test it** — run `gom examples/XX_your_example.gom` and verify it exits cleanly.
7. **Update the index** — add an entry in `examples/README.md`.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to abide by its terms.

---

*Questions? Open an issue on [GitHub](https://github.com/James-HoneyBadger/GulfOfMexico/issues) or reach out to the maintainers.*
