# Changelog

All notable changes to this project will be documented in this file.

The format is simple date-based entries. Dates use ISO-8601 (YYYY-MM-DD).

## 2025-11-18 (v0.1.5)

### Documentation standardization
- Unified look and feel across all documentation files
- Standardized titles to "Gulf of Mexico — <Topic>" format
- Added concise one-line introductions to all docs
- Created comprehensive docs style guide in DOCUMENTATION.md
- Added table of contents to DOCUMENTATION.md for easier navigation
- Normalized headings, links, and formatting across 20+ documentation files
- Updated LICENSE to MIT License with Honey Badger Universe copyright
- Reformatted CODE_OF_CONDUCT.md with clear headings and professional tone
- Added "Community & Policies" section to README and DOCUMENTATION
- Created docs/guides/README.md index for user guides
- Fixed example paths to use programs/examples/ and programs/demos/
- Updated .markdownlint.json to align with new documentation style
- Comprehensive updates to:
  - All reference docs (TECHNICAL_REFERENCE, FEATURE_PARITY, BUILTIN_FUNCTIONS, etc.)
  - All guide docs (INSTALL_GUIDE, USER_GUIDE, PROGRAMMING_GUIDE)
  - All compiler docs (README, EXPERIMENTAL_STATUS, CONSOLIDATION_*)
  - Central docs (README, DOCUMENTATION, CODE_OF_CONDUCT, configs/README)

## 2025-11-17 (v0.1.4)

### Release pipeline hardening
- Workflow now checks out the exact tag and supports manual dispatch (workflow_dispatch)
- Re-run friendly: you can manually run release for a given tag in Actions
- Improves reliability for GitHub Release creation and PyPI publish

## 2025-11-17 (v0.1.3)

### PyPI Publication
- First official release to PyPI (https://pypi.org/project/gulfofmexico/)
- Automated GitHub Release + PyPI publish via GitHub Actions
- Package installable via `pip install gulfofmexico`

## 2025-11-17 (v0.1.2)

### First GitHub Release automation
- Added GitHub Actions workflow to build wheels/sdist on version tags and create a GitHub Release with attached artifacts
- Release body sourced from `CHANGELOG.md`
- Optional PyPI publish via `pypa/gh-action-pypi-publish` using `PYPI_API_TOKEN` secret
- Console scripts wired: `gulfofmexico`, `gom`, `gom-ide`, `gomconfig`
### Repository cleanup and docs alignment
- Removed internal GOM test programs used for designing/debugging the language:
  - Deleted `programs/tests/` and `programs/06_compiler_tests/`
  - Removed stray root-level scratch files: `drawing_test.gom`, `gradient_test.gom`, `simple_graphics_test.gom`, `mandelbrot_art.gom`, `mandelbrot_final.gom`
  - Removed misplaced `executables/mandelbrot.gom`
- Updated runnable scripts:
  - `validate_all_programs.sh` no longer scans internal test directories
  - `organize_and_validate.sh` no longer creates/copies compiler test programs
- Updated active documentation to reflect user-facing program layout:
  - `README.md`, `DOCUMENTATION.md`, `docs/guides/PROGRAMMING_GUIDE.md`
  - `docs/reference/TECHNICAL_REFERENCE.md`, `SPEC_PARITY_STATUS.md`, `ASYNC_SCHEDULER_STATUS.md`
- Marked historical documents as archived (pre-cleanup structure):
  - Banners added to files under `docs/archive/` and `README_OLD.md`
- Clarified current user-facing directories:
  - `programs/examples/`, `programs/demos/` for examples
  - `compiler/examples/` for compiler-specific samples
  - Python unit tests live in `tests/`

## 2025-12-03 (v0.1.6)

### No-paren normalization sweep & bugfixes
- Normalized many example and program source files to the canonical "no-paren" calling style.
- Fixed a subtle but important edge case: dotted zero-argument method invocations like `obj.method !` return the method object and do not invoke it; such occurrences were converted to `obj.method()!` to execute the method body.
- Added a detection script and tests to prevent future regressions: `scripts/check_zeroarg_calls.py`, `tests/test_no_zeroarg_dotted_calls.py`.
- Added a CI step and pre-commit hooks to detect (and optionally fix) zero-argument dotted method occurrences.
