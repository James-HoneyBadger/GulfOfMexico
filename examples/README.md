# Gulf of Mexico — Example Programs

21 programs demonstrating all language features. Run any example:

```bash
python -m gulfofmexico examples/01_hello_world.gom
```

Run all examples:

```bash
for f in examples/*.gom; do
  echo "--- $(basename "$f") ---"
  python -m gulfofmexico "$f"
done
```

## Program Index

### Fundamentals

| File | Concepts |
|------|----------|
| `01_hello_world.gom` | Print statements, `!` confidence levels, `?` debug terminator |
| `02_variables_and_types.gom` | `const`/`var`, booleans, `undefined`, type conversions |
| `03_operators.gom` | Arithmetic, comparison, logical, string operations, significant whitespace |
| `04_tiered_equality.gom` | `=` (approximate), `==` (exact), `===` (type-strict), `====` (reference) |
| `05_control_flow.gom` | `if` blocks, recursion as the only loop mechanism |

### Functions and Data

| File | Concepts |
|------|----------|
| `06_functions.gom` | Definition, space vs paren calling, higher-order functions, recursion |
| `07_lists.gom` | -1 based indexing, push/pop, concatenation, recursive algorithms |
| `08_strings.gom` | Interpolation (`${}`, `£{}`, `¥{}`), escape sequences, reversal |
| `09_three_valued_logic.gom` | `true`, `false`, `maybe`; probabilistic execution; `;` (NOT) |
| `10_classes.gom` | Class declaration, single-instance rule, dot access, methods |

### Advanced Features

| File | Concepts |
|------|----------|
| `11_word_numbers.gom` | `zero`–`nineteen` literals, `twenty(n)`, `hundred(n)`, `half`/`quarter` |
| `12_delete.gom` | `delete` keyword — removing variables, values, even language keywords |
| `13_maps.gom` | `Map()` creation, set/get, iteration patterns |
| `14_algorithms.gom` | Factorial, fibonacci, array searching — all via recursion |
| `15_debug_and_confidence.gom` | `?` debug output, `!`/`!!`/`!!!` confidence levels, `noop` |

### Specialized

| File | Concepts |
|------|----------|
| `16_lifetimes.gom` | `var x <N> = val!` — variables that expire after N statements |
| `17_multiple_returns.gom` | Returning lists as multiple values, destructuring patterns |
| `18_number_indexing.gom` | Indexing individual digits of numbers (-1 based) |
| `19_string_interpolation_currencies.gom` | `${}`, `£{}`, `¥{}` interpolation with all currency symbols |

### Applications

| File | Concepts |
|------|----------|
| `20_bank_simulation.gom` | Full application: classes, methods, control flow combined |
| `21_sorting.gom` | Insertion sort — functional style, no mutation |

## Key Language Rules Demonstrated

- **-1 based indexing**: See `07_lists.gom`, `18_number_indexing.gom`
- **Significant whitespace**: See `03_operators.gom`
- **Three-valued booleans**: See `09_three_valued_logic.gom`
- **Tiered equality**: See `04_tiered_equality.gom`
- **No loops**: See `05_control_flow.gom`, `14_algorithms.gom`
- **Single-instance classes**: See `10_classes.gom`
- **Variable lifetimes**: See `16_lifetimes.gom`
