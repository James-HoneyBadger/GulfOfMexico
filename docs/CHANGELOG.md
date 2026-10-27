# Unreleased

### Compatibility

- **Python 3.10 support is dropped.** The minimum supported version is now 3.11;
  CI tests 3.11 through 3.14, and the Ruff/mypy target versions and the Trove
  classifiers follow. Python 3.10 reached end-of-life in October 2026, and two
  of its resolution pins (`Pillow` < 13.0.0, `filelock` < 4.2.1) have no patched
  release for that version, so continuing to support 3.10 would leave
  permanently unfixable advisories in `poetry.lock`.

### Security

- **Dependency advisory sweep.** `poetry.lock` no longer resolves any package to
  a release with an open GitHub/OSV advisory:
  `cryptography` 46.0.5 → 50.0.2 (CVE-2026-39892, CVE-2026-34073),
  `requests` 2.32.5 → 2.34.2 (CVE-2026-25645), `urllib3` 2.6.3 → 2.8.0,
  `certifi` 2024.12.14 → 2026.10.23, `idna` 3.11 → 3.20,
  `pygments` 2.19.2 → 2.21.0, `pyjwt` 2.8.0 → 2.15.1,
  `virtualenv` 20.36.1 → 21.15.0 (with `filelock` 3.24.2 → 4.2.4), and
  `Pillow` 12.1.1 → 13.0.0.
- `pytest` moves to `^9.0.3` (CVE-2025-71176, insecure temporary directory).

# v1.2.0 — 2026-10-23

### Interfaces

- **New terminal presentation layer** (`gulfofmexico/ui.py`). One module now
  owns colour policy and layout, so the CLI and REPL share a visual language.
- **Compiler-style diagnostics.** Errors render as a labelled message, an
  `--> file:line:col` location, a gutter, the source line, a caret under the
  offending token, and a hint when one helps.
- **Colour is terminal-aware.** ANSI is emitted only for TTYs, so piped output
  and CI logs are plain. `NO_COLOR` and `--no-color` opt out; `FORCE_COLOR`
  opts in.
- **CLI additions.** `--version`, `--no-color`, and `-q/--quiet`; grouped help
  output with sections for running code, output, modes, and environment
  variables; friendly messages for missing files and directories; documented
  exit codes (`0` success, `1` program error, `2` usage error).
- **Verbose runs report elapsed time** (`Code has finished executing in 4 ms.`)
  and no longer imply the process is waiting when it is not.
- **REPL polish.** Versioned banner with a command cheat sheet, coloured
  prompts, grouped `:help` with language hints, a `:vars` table (name, type,
  value), results rendered as language values instead of Python objects, errors
  on stderr, and a farewell on quit.
- **IDE polish.** The window title tracks the active file and modified state,
  tab tooltips show full paths, the status bar reports run duration and whether
  errors occurred, and the welcome buffer is a compact quick-reference.
- **Working Variables inspector.** The IDE now runs programs with
  `--vars-json` and populates the inspector from the snapshot, so the panel
  shows the program's variables (name, type, value) instead of staying empty.
  Variables and Outline show friendly empty states, the console is padded for
  readability, and harmless Qt SVG warnings no longer flood the terminal.
- **Documentation.** `examples/README.md` is now a categorized index with links
  and a feature-coverage summary; README and `docs/INSTALLATION.md` document the
  new flags, colour controls, and REPL commands.

### Language

- **Parentheses now group.** Previously `print(1 + 2*3)` printed `1` and
  `add(3, 2)` failed when nested; now parenthesised groups and argument lists
  evaluate as the spec's examples require. Stray/unmatched parentheses are
  still treated as whitespace, so `add)3, 2(!` works.
- **Arbitrary quote counts.** `'''Lu'''`, `""""Luke""""`, and the spec's
  `""she said "hi"""` example now scan correctly. `""` remains the empty
  string.
- **Four declaration forms.** `const const`, `const var`, `var const`, and
  `var var` now have the spec's distinct edit/re-assign permissions.
- **Loose `==`.** `3.14 == "3.14"` is `true`; `===` remains type-precise and
  `====` now compares literal expressions (`3.14 ==== 3.14` is true,
  `3.14 ==== pi` is false).
- **Automatic insertion (AEMI/ABI/AQMI).** Missing `!` terminators, closing
  brackets, and closing quotes are repaired automatically per the spec.
- **Object literals and Cape Verdean interpolation.** `{ name: "Lu" }` creates
  a map, dot access works, and `"{player$name}"` interpolates properties.
- **Postfix `++`/`--`** now update the variable (and record `previous`).
- **`await next`** no longer errors.
- **Emoji identifiers** now accept combining marks, so keycap emoji such as
  `1️⃣` are valid names.
- **Equal-spacing operator ties** now fall back to normal precedence
  (`2 * 1 + 3` → `5`), which is what makes the spec's `2 + 2 === 5` true.
- **Deleted keywords raise errors.** After `delete class!`, using `class`
  reports that the keyword has been deleted.
- **Class instance counting** is scoped to the class declaration, so nested
  class declarations in factory functions can each create an instance.

### Tooling

- **`gom --check FILE`** parses a program — including every `===== name =====`
  section — and reports problems without running it. Expression trees are
  compiled too, so errors that would otherwise only appear mid-run are caught
  up front. Works with `-c`, with `-` (stdin), and with several files at once.
- **`gom --fmt FILE`** prints a program in canonical layout and `gom --fmt -w
  FILE` rewrites it in place. Formatting only touches leading indentation
  (remapped to 3-space levels, so block structure is preserved), trailing
  whitespace, runs of blank lines, and the final newline. Spacing *inside* a
  line is never changed, because it decides operator-precedence ties, and lines
  inside triple-quoted strings are left exactly as written.
- **`gom --check --fmt FILE`** fails when a file is not canonically formatted.
  It is used by CI to keep every bundled example formatted.
- **`gom -`** reads a program from standard input and names errors `<stdin>`.

### Standard library

- **Collection methods.** Lists gain `insert`, `sort`, `reverse`, `indexOf`,
  `contains`, `slice`, and `join` alongside `push`/`pop`/`length`; strings gain
  `split`, `upper`, `lower`, `trim`, `replace`, `contains`, `startsWith`,
  `endsWith`, and `indexOf`; maps gain `keys`, `values`, `has`, `delete`, and
  `length`. Methods are reachable with a dot on a name *or* on a literal
  (`"a,b".split(",")`), and a map method wins over an entry of the same name.
- **`gulfofmexico/prelude.py` — a standard helper library** written in GOM:
  `range`, `rangeFrom`, `map`, `filter`, `reduce`, `zip`, `take`, `reverseOf`,
  `concat`, `sortBy`, `sum`, `maxOf`, and `minOf`. Loaded into the base
  namespace at startup, shadowable by user declarations, and skipped entirely
  with `GOM_NO_PRELUDE=1`.

### Execution

- **`after` no longer blocks.** A scheduled block is queued and runs when its
  deadline arrives, drained at statement boundaries and at program end, in
  deadline order with FIFO tie-breaking. Use `sleep` when blocking is wanted.
- **`when` is armed at declaration** and fires only on mutation, never at
  registration, which is what the specification describes.
- **Persistence is hardened.** The runtime directory is created `0700` (the
  store file was already `0600`); an unparseable store is renamed to
  `store.json.corrupt` before being rebuilt instead of being overwritten; a
  store written by a *newer* schema is reported and never overwritten; a single
  malformed entry no longer hides the rest; and persisted maps with numeric
  keys keep their key type instead of silently becoming strings.
- **Persistent immutables use JSON.** `const const const` values are stored in
  `store.json` under `GOM_HOME` (default `~`) instead of a pickle, written
  atomically with `0600` permissions under an exclusive lock. An existing
  pickle store is left untouched and reported once; migrate it with
  `GOM_ALLOW_LEGACY_PICKLE=1`.
- **Recursion depth is bounded by default** (`GOM_RECURSION_LIMIT`, 10000) and
  reports an actionable error instead of a raw Python `RecursionError`.

### Performance

- **Expression trees are compiled once per statement** instead of on every
  evaluation. Recursion-heavy programs improve by an order of magnitude
  (`fib`-style recursion 2000 deep: ~2.9 s → ~0.6 s).
- **Temporal lifetimes only tick for variables that have one**, replacing a
  full-scope sweep per statement (164k sweeps to one scan per statement).
- **Deep recursion no longer degrades super-linearly.** A 20 000-deep recursion
  went from over a minute to under a second.

### IDE

- **Autocomplete** (`Ctrl+Space`) for keywords, builtins, prelude helpers, and
  every `const`/`var`/function/class name in the current file.
- **Run with Input** (`Shift+F5`) runs a program with a text box wired to stdin.
- **Stop** (`F6`) terminates a running program, and the status bar reports how
  long the last run took.
- **Find in Files** (`Ctrl+Shift+F`), **Go to Symbol** (`Ctrl+Shift+O`), and
  **Rename Symbol** (`F2`).
- **Live diagnostics**: the active editor is re-checked as you type and shows
  the first problem inline, in the status bar, and on the gutter.

### Packaging and CI

- The package ships `py.typed` and advertises `Typing :: Typed`.
- **Fixed ruff ruleset** (`E4`, `E7`, `E9`, `F`, `target-version = "py310"`) so
  local and CI lint results no longer drift with the ruff release; the fourteen
  existing findings in `ide/app.py` are fixed.
- **CI tests Python 3.10 through 3.14** (was 3.12 only), publishes coverage
  (measuring subprocess runs, ~68 %) with a floor, and validates that every
  bundled example parses and is canonically formatted.
- `pyproject.toml` gains coverage, mypy, and pytest-cov configuration, and the
  Python 3.14 classifier.
- Stale `poetry.lock` ignore rule removed from `.gitignore`.

### Tests and docs

- Added `tests/test_dreamb_spec.py` (~70 conformance tests),
  `tests/test_ux.py` (30 presentation tests covering colour policy, diagnostic
  layout, CLI flags, and REPL output), `tests/test_tools.py` (82 tests for the
  checker, formatter, section splitter, and stdin mode),
  `tests/test_persistence.py`, and `tests/test_collections_and_scheduler.py`.
  The suite now stands at 485 tests. `tests/test_persistence.py` was rewritten
  around behaviour rather than source text (the pickle guard now asserts that
  the JSON path never unpickles, structurally and at runtime) and covers
  concurrency, corrupt-store recovery, newer-schema refusal, per-entry
  resilience, codec error paths, typed map keys, non-ASCII round-trips, and the
  legacy `.inf_vars` format.
- The language reference documents collection methods, the prelude (§18), and
  the new environment variables; the README documents the new CLI modes.

# v1.1.0 — 2026-06-22

### UX, spec conformance, and expanded examples

#### Usability

- CLI now reports errors with source context and clear messages (missing files,
  type mismatches, runtime errors) instead of a generic "Error during execution."
- Added a richer `gom --help` with usage modes, environment variables, and examples.
- REPL gains persistent history (`~/.gom_history`), tab completion for keywords,
  namespace names, and meta-commands, and more robust multi-line brace detection
  that ignores braces inside strings and comments.
- IDE strips ANSI color codes from error output for clean display.

#### Spec conformance

- Type annotations are now **enforced** at declaration: a value that does not
  match its declared type (`Int`, `Number`, `String`, `Bool`, `List`, `Map`,
  `Object`, `Function`) raises a type error. Unknown/custom types are not enforced.
- Documented and tested that `when` watchers **re-fire** every time an assignment
  leaves the condition true (reactive semantics), rather than firing only once.
- Added `GOM_DISABLE_TARIFF` env hook to disable the random import tariff for
  deterministic runs and tests.

#### Examples

- Expanded the example suite from 26 to 48 programs (`27`–`48`), covering escape
  sequences, three-valued logic, recursion patterns, currency interpolation,
  `next` promises, `after` scheduling, confidence levels, random numbers,
  multi-file sections, persistent constants, list/map algorithms, factorials and
  combinatorics, string processing, stacks/queues, nested data structures, a
  reactive monitor, type annotations, and Unicode/emoji.

#### Tests

- Added regression coverage for enforced type annotations, the `previous`
  keyword, reactive `when` re-firing, fractional indexing, and extended emoji
  identifiers (now 204 passing).

# v1.0.0 — 2026-03-22

### Production release

- All features and documentation finalized for 1.0.0

# v1.0.1 — 2026-06-09

### Spec conformance alignment

#### Parser and grammar

- Added `import name from section!` parsing and runtime resolution to section-scoped exports.
- Added declaration confidence marker parsing (`~N~`) for `const`/`var` declarations.
- Enforced strict statement terminators (`!`, `!!`, `!!!`, or `?`) for non-scoped statements.
- Enforced indentation contract: tabs in indentation are now rejected; indentation must use multiples of 3 spaces.

#### Runtime semantics

- Implemented executable `after` statements with millisecond delay semantics.
- Aligned `sleep` to milliseconds (`sleep 1000!` ~= 1 second).
- Aligned `Boolean(number)` conversion: `0 -> false`, `1 -> true`, any other numeric value -> `maybe`.
- Aligned positive lifetime semantics: `<N>` is statement-count based; `<Ns>` is temporal seconds-based.
- Fixed lifetime parsing so `<N>` / `<Ns>` metadata is correctly captured for standard declarations.
- Updated `reverse` so replay does not prematurely terminate subsequent statements.

#### Import tariff

- Aligned tariff behavior to language reference intent:
	- import executes with a short random delay;
	- each import has a 25% chance to remove one future statement from the **importing** section.
- Added deterministic test hooks for tariff behavior (`GOM_FORCE_TARIFF_REMOVE`, `GOM_FORCE_TARIFF_INDEX`).

#### Tests

- Added regression coverage for:
	- `after` execution,
	- `import ... from ...`,
	- millisecond `sleep`,
	- numeric Boolean conversion,
	- line/temporal lifetimes,
	- `reverse` continuation and function/async edge behavior,
	- declaration confidence markers,
	- strict terminator and tab-indentation enforcement.

# Changelog

All notable changes to the Gulf of Mexico interpreter are documented here.

---

## v0.4.0 — 2026-03-21

### IDE overhaul — modern GUI, new editor features, configurable panels

#### IDE — visual and UX improvements

- **Modern stylesheet**: overhauled QSS with visible 5px drag handles between panels (accent-coloured on hover), dock title gradient with accent left border, tab close buttons turning red on hover, pill-style status bar labels, and improved focus rings on inputs.
- **Dock nesting**: panels can be tabbed together or freely nested via drag-and-drop (`setDockNestingEnabled`).
- **Closable panels**: Console and Variables docks now have a standard title-bar × close button (`DockWidgetClosable`); closed panels can be restored via View menu or toolbar toggle buttons.
- **Movable toolbar**: toolbar can be dragged to any window edge or detached as a floating window.
- **Panel toggle buttons**: "⬇ Console" and "⊞ Variables" checkable buttons added to the toolbar. Dock visibility and button / menu-check state are kept in sync bidirectionally.
- **Dock layout persistence**: dock and toolbar positions are saved to `~/.config/gom-ide/settings.json` on close and restored on next launch. First run uses sensible defaults (Console 220 px, Variables 260 px).
- **Animated transitions**: panel show/hide uses Qt's built-in animated dock resizing (`setAnimated(True)`).

#### IDE — editor features

- **Word wrap**: the word-wrap setting now correctly applies to all editor tabs via `QTextOption.WrapMode` enum (was previously broken).
- **Show / hide line numbers**: the line-number gutter can be toggled; hiding it returns the full column width to the editor.
- **Go to Line** (Ctrl+G): dialog with a spin-box jumps the cursor to any line number.
- **Duplicate Line** (Ctrl+D): duplicates the current line or selection below. Also available in the Edit menu.
- **Move Line Up** (Alt+↑) / **Move Line Down** (Alt+↓): swap the current line with the one above or below.
- **Tab right-click context menu**: Close, Close Others, Close All, Duplicate Tab, Copy File Path.
- **Auto-close bracket fix**: pressing a closing bracket when the next character is already the matching closer now skips over it instead of inserting a duplicate.
- **Selection count in status bar**: the cursor-position label appends `(N sel)` when text is selected.

#### IDE — execution and settings

- **Clear-console-on-run** setting: optionally wipe the console output before each run (Settings → Execution tab).
- **Console timestamps**: each run prints a `─── Run · HH:MM:SS ───` header so successive outputs are clearly separated.

#### Themes

- **Catppuccin Mocha** theme added (total: 7 built-in themes — One Dark, Dracula, Nord, Solarized Dark, GitHub Light, Monokai, Catppuccin Mocha).

#### Bug fixes

- Fixed `setWordWrapMode` crash: the method requires a `QTextOption.WrapMode` enum value, not a plain `int`. Passing `0`/`1` raised a `TypeError` on PySide6 ≥ 6.7.

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
