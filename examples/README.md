# Gulf of Mexico — Example Programs

A comprehensive demo suite covering every feature of the GOM language. Each program runs independently and exits cleanly.

Run any example:
```bash
python -m gulfofmexico examples/01_hello_world.gom
```

## Programs

| # | File | Features Covered |
|---|------|-----------------|
| 01 | `01_hello_world.gom` | `print`, statement terminators (`!`, `!!`, `!!!`) |
| 02 | `02_variables.gom` | `const`, `var`, reassignment, `previous`, type annotations |
| 03 | `03_types.gom` | Numbers, strings, booleans, lists, `undefined`, type conversion |
| 04 | `04_operators.gom` | Arithmetic, significant whitespace precedence, unary minus, `++`/`--` |
| 05 | `05_tiered_equality.gom` | `=`/`==`/`===`/`====`, `;=` (inequality), `~=`/`~==`/`~===` (AEMI/ABI/AQMI) |
| 06 | `06_comparison_and_logic.gom` | `>`/`<`/`>=`/`<=`, `&` (AND), `\|` (OR), `;` (NOT), three-valued logic |
| 07 | `07_control_flow.gom` | `if` blocks, recursion (no loops), sequential conditionals |
| 08 | `08_functions.gom` | `function`/`fn`, space call syntax, higher-order, multiple returns |
| 09 | `09_strings.gom` | String interpolation (`$`/`£`/`¥`), `.length`, reversal, indexing |
| 10 | `10_lists.gom` | -1-based indexing, `.push()`/`.pop()`/`.length`, concatenation, reversal |
| 11 | `11_maps.gom` | `Map()`, bracket notation, read/update |
| 12 | `12_classes.gom` | `class`, `new`, single-instance rule, properties, methods |
| 13 | `13_word_numbers.gom` | `zero`–`nineteen`, `twenty()`–`million()`, `half`/`third`/`quarter` |
| 14 | `14_number_indexing.gom` | Digit indexing on numbers with -1-based indices |
| 15 | `15_lifetimes.gom` | `<N>` variable lifetimes, `<-N>` negative lifetime hoisting |
| 16 | `16_delete_and_confidence.gom` | `delete`, confidence overloading (`!`/`!!`/`!!!`), `?` debug |
| 17 | `17_compound_assignment.gom` | `+=`, `-=`, `*=`, `/=`, `^=` |
| 18 | `18_emoji_identifiers.gom` | Emoji variable names, emoji function names |
| 19 | `19_reactive.gom` | `when` watchers, `reverse`, `use` signals |
| 20 | `20_math_builtins.gom` | `abs`, `floor`, `ceil`, `round`, `sqrt`, `sin`/`cos`/`tan`, `log`, `exp`, `pow`, `min`/`max`, `degrees`/`radians` |
| 21 | `21_negative_indentation.gom` | Cosmetic leading `}` (DreamBerd spec) |
| 22 | `22_async_and_redefinition.gom` | `async` functions, number literal redefinition |
| 23 | `23_algorithms.gom` | Fibonacci, recursive power, list sum, GCD |
| 24 | `24_comments.gom` | `//` single-line, `/* */` block comments |
| 25 | `25_regex.gom` | `regex_match`, `regex_findall`, `regex_replace` |
| 26 | `26_noop_and_misc.gom` | `noop`, empty value `()`, string multiply, boolean conversion |

## Feature Coverage

These 26 programs collectively demonstrate:
- All 4 statement terminators
- All 8 data types
- All arithmetic, comparison, and logical operators
- Tiered equality (4 levels + 3 tilde variants)
- Significant whitespace operator precedence
- Three-valued boolean logic
- -1-based indexing (lists, strings, numbers)
- Variable lifetimes and negative lifetime hoisting
- Variable confidence overloading
- Compound assignment operators
- Emoji identifiers
- Negative indentation
- Async functions and number redefinition
- Recursive algorithms (no loops)
- Classes with single-instance rule
- Reactive primitives (when, reverse, use)
- Word numbers and named fractions
- String interpolation with 3 currency symbols
- 17 math built-in functions
- Regular expressions
- Comments (single-line and block)
- Type conversions
- Delete
- Noop and empty value
