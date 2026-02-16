# Gulf of Mexico — Example Programs

21 programs demonstrating every language feature, from basic output to sorting algorithms.

---

## Running Examples

```bash
# Run a single example
gom examples/01_hello_world.gom

# Run all examples sequentially
for f in examples/*.gom; do
  echo "=== $(basename "$f") ==="
  gom "$f"
  echo
done
```

All examples are also run automatically by the test suite (`python -m pytest`).

---

## Program Index

### Fundamentals

These examples cover the core syntax and basic concepts needed to write GOM programs.

| # | File | Concepts Demonstrated |
|---|------|----------------------|
| 01 | [01_hello_world.gom](01_hello_world.gom) | `print` statements, `!` / `!!` / `!!!` confidence levels, `?` debug terminator |
| 02 | [02_variables_and_types.gom](02_variables_and_types.gom) | `const` / `var` declarations, booleans, `undefined`, type conversions with `String()`, `Number()`, `Boolean()` |
| 03 | [03_operators.gom](03_operators.gom) | Arithmetic (`+`, `-`, `*`, `/`, `^`), comparison (`>`, `<`), logical (`&&`, `||`, `;`), string operations, **significant whitespace** binding |
| 04 | [04_tiered_equality.gom](04_tiered_equality.gom) | Four equality levels: `=` (approximate), `==` (exact), `===` (type-strict), `====` (reference identity) |
| 05 | [05_control_flow.gom](05_control_flow.gom) | `if` blocks, recursion as the only loop mechanism, function-based branching |

### Functions and Data Structures

These examples explore function definitions, calling conventions, and data types.

| # | File | Concepts Demonstrated |
|---|------|----------------------|
| 06 | [06_functions.gom](06_functions.gom) | `function` / `fn` / `func` / `f` definition, space vs parenthesized calling, higher-order functions, recursion |
| 07 | [07_lists.gom](07_lists.gom) | List creation, **-1-based indexing**, `push` / `pop`, `length`, list concatenation (`+`), list reversal (`-`), recursive list algorithms |
| 08 | [08_strings.gom](08_strings.gom) | String interpolation (`${}`, `£{}`, `¥{}`), escape sequences (`\n`, `\t`, etc.), `length`, string reversal, character indexing |
| 09 | [09_three_valued_logic.gom](09_three_valued_logic.gom) | `true`, `false`, `maybe`; probabilistic execution; AND/OR/NOT truth tables; `;` (semicolon NOT) |
| 10 | [10_classes.gom](10_classes.gom) | Class declaration, `new` instantiation, single-instance-per-class rule, dot-access properties, methods |

### Advanced Features

These examples cover GOM's more unusual language features.

| # | File | Concepts Demonstrated |
|---|------|----------------------|
| 11 | [11_word_numbers.gom](11_word_numbers.gom) | `zero`–`nineteen` literals, `twenty(n)`–`ninety(n)` functions, `hundred(n)`, `thousand(n)`, `million(n)`, named fractions (`half`, `quarter`, `third`) |
| 12 | [12_delete.gom](12_delete.gom) | `delete` keyword — removing variables, values, and even built-in language keywords from scope |
| 13 | [13_maps.gom](13_maps.gom) | `Map()` creation, bracket-notation set/get, iteration patterns |
| 14 | [14_algorithms.gom](14_algorithms.gom) | Factorial, Fibonacci, array searching — all implemented via recursion (no loops) |
| 15 | [15_debug_and_confidence.gom](15_debug_and_confidence.gom) | `?` debug terminator output, `!` / `!!` / `!!!` confidence levels, `noop` statement |

### Specialized Features

These examples demonstrate features unique to Gulf of Mexico.

| # | File | Concepts Demonstrated |
|---|------|----------------------|
| 16 | [16_lifetimes.gom](16_lifetimes.gom) | `var x <N> = val!` — variables that automatically expire after N statements |
| 17 | [17_multiple_returns.gom](17_multiple_returns.gom) | Returning lists as multiple return values, destructuring at the call site |
| 18 | [18_number_indexing.gom](18_number_indexing.gom) | Indexing individual digits of numbers using -1-based indexing |
| 19 | [19_string_interpolation_currencies.gom](19_string_interpolation_currencies.gom) | All currency interpolation prefixes: `${}`, `£{}`, `¥{}` |

### Applications

These examples combine multiple features into more complete programs.

| # | File | Concepts Demonstrated |
|---|------|----------------------|
| 20 | [20_bank_simulation.gom](20_bank_simulation.gom) | Full banking application: classes, methods, control flow, string interpolation, state management |
| 21 | [21_sorting.gom](21_sorting.gom) | Insertion sort — functional style with no mutation, recursive list building |

---

## Key Language Rules by Example

| Concept | Best Example | Quick Explanation |
|---------|-------------|-------------------|
| -1-based indexing | [07](07_lists.gom), [18](18_number_indexing.gom) | `arr[-1]` is the first element |
| Significant whitespace | [03](03_operators.gom) | `2 * 1+3` ≠ `2*1 + 3` |
| Three-valued booleans | [09](09_three_valued_logic.gom) | `maybe` is true ~50% of the time |
| Tiered equality | [04](04_tiered_equality.gom) | `=` ≠ `==` ≠ `===` ≠ `====` |
| No loops | [05](05_control_flow.gom), [14](14_algorithms.gom) | All iteration via recursion |
| Single-instance classes | [10](10_classes.gom) | One object per class at a time |
| Variable lifetimes | [16](16_lifetimes.gom) | Variables can auto-expire |
| Word numbers | [11](11_word_numbers.gom) | `five` = 5, `hundred(3)` = 300 |
| Currency interpolation | [19](19_string_interpolation_currencies.gom) | `${}`, `£{}`, `¥{}` in strings |

---

*For the complete language specification, see [docs/LANGUAGE_REFERENCE.md](../docs/LANGUAGE_REFERENCE.md).*
