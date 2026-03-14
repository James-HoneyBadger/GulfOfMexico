# Changelog

All notable changes to the Gulf of Mexico interpreter are documented here.

---

## v0.3.0 — 2026-03-13

### DreamBerd spec alignment, new example suite, and IDE overhaul

#### New language features

- **Tilde equality operators**: `~=` (AEMI), `~==` (ABI), `~===` (AQMI) — three levels of approximate matching.
- **Compound assignment**: `+=`, `-=`, `*=`, `/=`, `^=` operators for modify-in-place.
- **Emoji identifiers**: Variable and function names can use emoji characters (🎉, 🚀, etc.).
- **Negative lifetime hoisting**: `<-N>` makes a variable available N lines before its declaration.
- **Negative indentation**: Leading `}` characters are cosmetic and ignored by the parser.
- **Async interleaving**: `async function` bodies queue for deferred execution.
- **Variable overloading**: Re-declaring an existing name shadows it; `previous` still accesses the old value.
- **Number literal redefinition**: `const const 5 = 4!` redefines what `5` evaluates to.

#### IDE overhaul

- Rewrote all 4 IDE modules (`qt_compat.py`, `editor.py`, `highlighter.py`, `app.py`).
- **5 built-in themes**: Gulf Dark, Gulf Light, Solarized Dark, Monokai, Nord.
- **Settings dialog** (Ctrl+,) for theme selection.
- **Toolbar** with Run, Stop, New, Open, Save buttons.
- **Bracket matching** with visual highlights in the editor.
- Block-based syntax highlighter that adapts to the active theme.

#### Examples

- Deleted all 21 old example programs.
- Created 26 new comprehensive demos covering every GOM feature.
- New `examples/README.md` with feature coverage table.

#### Bug fixes

- Fixed operator documentation: GOM uses `&`/`|` (not `&&`/`||`) and `;=` (not `!=`).
- Fixed regex built-in functions to document single-arg comma-delimited syntax.
- Fixed recursion examples to use intermediate variables (prevents infinite recursion from argument expression parsing).
- Fixed class single-instance rule: must `delete` before creating a second instance.
- Fixed `list.push` to use space syntax (`arr.push 4!` not `arr.push(4)!`).
- Fixed variable reassignment regression from overloading feature.

#### Tests

- Added `tests/test_interpreter.py` with 141 unit tests covering all language features.
- Total test count: **170** (141 interpreter + 29 example/compliance tests), all passing.

#### Documentation

- Updated all documentation files to reflect v0.3.0 changes.
- Added DreamBerd Extensions section to Language Reference.
- Fixed logical operator (`&`/`|`), inequality (`;=`), and regex syntax across all docs.

---

## v0.2.0 — 2026-02-15

### Major refactor and spec compliance

#### Architecture

- Split monolithic `interpreter.py` into 10 focused modules in `gulfofmexico/interpreter/`: context, helpers, operators, namespaces, persistence, expressions, variables, watchers, dispatch, execution.
- Added public API re-exports in `gulfofmexico/interpreter/__init__.py` and `gulfofmexico/processor/__init__.py`.
- Removed dead code: `execution_context.py` (superseded by `interpreter/context.py`).
- Consolidated configuration: merged `setup.cfg` into `pyproject.toml`, removed phantom `gomconfig` entry point.
- Fixed stale `MANIFEST.in` references to non-existent directories and files.
- Added `.mypy_cache/` and `.ruff_cache/` to `.gitignore`.
- Added `tests/__init__.py` for proper package discovery.
- Added `[tool.pytest.ini_options]` with `testpaths` to `pyproject.toml`.

#### Spec compliance

- Comprehensive 94-rule audit against the language specification with 11 bugs found and fixed.
- ~12,500 lines of non-spec code removed (handler dispatch, plugin system, profiling, benchmarking, engine, handlers_impl, language_config, watcher_manager, etc.).

#### Bug fixes

- **-1-based indexing**: Implemented correctly across lists, numbers, and strings per spec (index -1 = first element).
- **Operator chars in strings**: Fixed crash when string literals contain operator characters (`+`, `-`, `*`, etc.).
- **Type annotations**: Fixed crash from wrong function signature in type annotation checker.
- **When statement**: Fixed condition evaluation to use current variable values instead of stale copies from registration time.
- **Next promise**: Fixed watcher key mismatch and added actual promise value resolution.
- **`use()` signal**: Fixed getter mode to support variadic calling (0 args = get, 1 arg = set).
- **Math functions**: Added 17 built-in math functions (abs, floor, ceil, round, sqrt, sin, cos, tan, log, exp, degrees, radians, pow, min, max, random, randomInt).
- **Reverse statement**: Added parser support for standalone `reverse!` (no variable name).
- **If-block return propagation**: Created `ReturnSentinel` pattern to distinguish explicit returns from implicit expression results.

#### Documentation

- Complete rewrite of all documentation: README, Language Reference, Architecture Guide, Changelog.
- New Installation Guide (`docs/INSTALLATION.md`) with platform-specific instructions.
- New Contributing Guide (`CONTRIBUTING.md`) with coding standards and testing workflow.
- Updated examples README with categorized program index.

#### Examples and tests

- 21 example programs created and verified passing.
- 5 examples updated for -1-based indexing.
- Spec compliance test (`tests/spec_compliance.gom`) expanded to cover all fixed bugs.
- All 24 tests passing.

---

## v0.1.6 — 2025-12-03

### Normalization and bugfixes

- Normalized example files to canonical no-paren calling style.
- Fixed zero-argument dotted method invocations.

---

## v0.1.5 — 2025-11-18

### Documentation standardization

- Unified look and feel across documentation files.
- Updated LICENSE to MIT License.

---

## v0.1.4 — 2025-11-17

### Release pipeline hardening

- GitHub Actions workflow now checks out the exact tag.
- Added support for manual dispatch in CI.

---

## v0.1.3 — 2025-11-17

### PyPI publication

- First official release to PyPI (`pip install gulfofmexico`).

---

## v0.1.2 — 2025-11-17

### First GitHub Release automation

- Added GitHub Actions workflow for builds and releases.
- Console scripts wired: `gulfofmexico`, `gom`, `gom-ide`.
- Repository cleanup and initial packaging.
