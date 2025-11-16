# Utility Scripts

This directory contains development and maintenance scripts for the Gulf of Mexico interpreter.

## Scripts

### `run_programs_via_repl.py`
Batch runner that loads each `programs/**/*.gom` file into the interactive REPL using `:load <file>` and then exits. This verifies REPL parity with the direct interpreter.

**Usage:**
```bash
python3 scripts/run_programs_via_repl.py
```

**Notes:**
- Handles multi-file `.gom` demos that use `===== section =====` markers
- Classifies results based on clean REPL exit and absence of errors

### `run_all_programs.py`
Batch runner that executes all `.gom` programs in the `programs/` directory and reports results.

**Usage:**
```bash
python3 scripts/run_all_programs.py
```

**Output:**
- `PASS` - Program executed successfully with expected output
- `PASS-TIMEOUT` - Program executed but timed out (expected for reactive programs with `when`/`after`)
- `UNKNOWN` - Unexpected output or behavior
- `ERROR` - Execution failed

### `fix_function_calls.py`
Automated script to normalize function call syntax (remove parentheses from multi-arg calls).

**Usage:**
```bash
python3 scripts/fix_function_calls.py
```

### `fix_indentation.py`
Script to fix indentation issues in `.gom` files.

**Usage:**
```bash
python3 scripts/fix_indentation.py
```

### `benchmarks.py`
Performance benchmarks for the **experimental** engine components.

**⚠️ WARNING:** These benchmarks test experimental caching infrastructure (`gulfofmexico/engine/`), NOT the production interpreter. Performance improvements shown apply only to experimental code.

**Usage:**
```bash
python3 scripts/benchmarks.py
```

## Development Workflow

1. Make changes to interpreter or programs
2. Run batch tests: `python3 scripts/run_all_programs.py`
3. Fix any issues
4. Use utility scripts to normalize syntax if needed
5. Re-run tests to verify

## Notes

- All scripts assume they're run from the repository root
- The batch runner has a 6-second timeout per file (normal for reactive programs)
- Scripts in this directory are for development; end users should use `run_gom.py` directly
