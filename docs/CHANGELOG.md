# Changelog

## 2026-02-15 (v0.2.0)

### Major refactor and spec compliance

- **Architecture**: Split monolithic `interpreter.py` into 11 focused modules in `gulfofmexico/interpreter/` package: context, helpers, operators, namespaces, persistence, expressions, variables, watchers, dispatch, execution
- **Spec compliance**: Comprehensive 94-rule audit with 11 bugs found and fixed
- **Codebase cleanup**: Removed ~12,500 lines of non-spec features (handler dispatch, plugin system, profiling, benchmarking, engine, handlers_impl, language_config, watcher_manager, etc.)
- **Documentation**: Complete rewrite of all documentation to match current codebase

### Bug fixes

- **-1 based indexing**: Implemented across lists, numbers, and strings per spec (index -1 = first element)
- **Operator chars in strings**: Fixed crash when string literals contain operator characters (`+`, `-`, `*`, etc.)
- **Type annotations**: Fixed crash from wrong function signature in type annotation checker
- **When statement**: Fixed condition evaluation to use current variable values instead of stale copies from registration time
- **Next promise**: Fixed watcher key mismatch and added actual promise value resolution
- **use() signal**: Fixed getter mode to support variadic calling (0 args = get, 1 arg = set)
- **Math functions**: Added 17 built-in math functions (abs, floor, ceil, round, sqrt, sin, cos, tan, log, exp, degrees, radians, pow, min, max, random, randomInt)
- **Reverse statement**: Added parser support for standalone `reverse!` (no variable name)
- **If-block return propagation**: Created ReturnSentinel pattern to distinguish explicit returns from implicit expression results, preventing top-level if blocks from killing subsequent execution

### Examples

- 21 example programs created and verified passing
- 5 examples updated for -1 based indexing
- Spec compliance test expanded with regression tests for all fixed bugs

## 2025-12-03 (v0.1.6)

### Normalization and bugfixes

- Normalized example files to canonical no-paren calling style
- Fixed zero-argument dotted method invocations

## 2025-11-18 (v0.1.5)

### Documentation standardization

- Unified look and feel across documentation files
- Updated LICENSE to MIT License

## 2025-11-17 (v0.1.4)

### Release pipeline hardening

- Workflow now checks out the exact tag and supports manual dispatch

## 2025-11-17 (v0.1.3)

### PyPI publication

- First official release to PyPI (`pip install gulfofmexico`)

## 2025-11-17 (v0.1.2)

### First GitHub Release automation

- Added GitHub Actions workflow for builds and releases
- Console scripts wired: `gulfofmexico`, `gom`, `gom-ide`, `gomconfig`
- Repository cleanup
