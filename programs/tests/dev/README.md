# Development Test Files

This directory contains small test programs used during interpreter development and debugging.

## Purpose

These are **development tests** - minimal programs created to verify specific features or debug issues during interpreter development. They complement the comprehensive test suite in the parent directory.

## Files

- `minimal_return.gom` - Minimal test for return statements
- `test_func_ref.gom` - Test function references (not calls)
- `test_greet_simple.gom` - Simple function with argument
- `test_no_parens.gom` - Call syntax without parentheses
- `test_return.gom` - Zero-arg function return
- `test_return_arg.gom` - Function with "return" as parameter name
- `test_return_var.gom` - Return with variable
- `test_single_arg.gom` - Single argument function
- `test_web_ide_example.gom` - Web IDE demo example

## Usage

Run individual tests:
```bash
python3 run_gom.py programs/tests/dev/test_return.gom
```

These files are included in the batch test runner along with the main test suite.

## Note

For comprehensive feature tests, see the main test suite in `programs/tests/`.
For example programs, see `programs/examples/`.
For complete demos, see `programs/demos/`.
