# Changelog

All notable changes to this project will be documented in this file.

The format is simple date-based entries. Dates use ISO-8601 (YYYY-MM-DD).

## 2025-11-17

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

