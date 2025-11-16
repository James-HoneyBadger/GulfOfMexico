# Gulf of Mexico Programs

This directory contains examples, tests, and demonstrations for the Gulf of Mexico programming language.

## Directory Structure

```
programs/
├── examples/     # Basic examples demonstrating individual features
├── tests/        # Test files for language functionality
└── demos/        # Advanced demonstrations and real-world scenarios
```

## Examples

Educational examples covering core language features:

- **01_hello_world.gom** - The simplest program
- **02_variables.gom** - Variable declarations (const, var, const var)
- **03_arrays.gom** - Arrays starting at -1 and fractional indexing
- **04_probabilistic.gom** - Probabilistic variables with confidence levels
- **05_functions.gom** - Function definitions and calls
- **06_classes.gom** - Class definitions and object creation
- **07_conditionals.gom** - If statements
- **08_equality.gom** - Multiple equality operators (=, ==, ===, ====)
- **09_three_valued_logic.gom** - true, false, and maybe
- **10_reactive.gom** - Reactive when statements
- **11_lifetimes.gom** - Variable lifetimes (line-based and time-based)
- **12_async.gom** - Async functions and await
- **13_string_interpolation.gom** - String interpolation with ${...}
- **14_arithmetic.gom** - Arithmetic operations
- **15_word_numbers.gom** - Word-based number variables

## Tests

Test files validating language features:

- **test_variables.gom** - Variable declaration and assignment
- **test_array_indexing.gom** - Array indexing starting at -1
- **test_fractional_indexing.gom** - Fractional array insertion
- **test_probabilistic.gom** - Probabilistic variable confidence
- **test_functions.gom** - Function definitions and calls
- **test_classes.gom** - Class behavior
- **test_conditionals.gom** - If statement execution
- **test_equality.gom** - Equality operator levels
- **test_three_valued_logic.gom** - Boolean logic with maybe
- **test_reactive.gom** - When statement reactivity
- **test_string_interpolation.gom** - String interpolation
- **test_arithmetic.gom** - Arithmetic operations
- **test_async.gom** - Async/await functionality

## Demos

Advanced demonstrations:

- **calculator.gom** - Basic calculator with multiple operations
- **task_manager.gom** - Task tracking with classes
- **reactive_counter.gom** - Counter with reactive milestones
- **multi_file.gom** - Multi-file program with import/export
- **banking_system.gom** - Banking system with transfers
- **async_pipeline.gom** - Async data processing pipeline
- **rpg_character.gom** - RPG character with stats and abilities
- **feature_showcase.gom** - Comprehensive feature demonstration

## Running Programs

### Single file
```bash
python -m gulfofmexico programs/examples/01_hello_world.gom
```

### Multi-file program
```bash
python -m gulfofmexico programs/demos/multi_file.gom
```

### In the REPL
```bash
python -m gulfofmexico
```

### Using the IDE
```bash
python -m gulfofmexico.ide
```
