# Example Programs

Forty-nine self-contained programs that walk through the Gulf of Mexico
language from first output to full algorithms. Every file runs on its own and
exits cleanly, so they double as a regression suite for the interpreter.

```bash
gom examples/01_hello_world.gom
gom examples/23_algorithms.gom
```

> Run them all at once with `pytest tests/test_examples.py`.

## Start here

| # | Program | What it teaches |
|---|---------|-----------------|
| 01 | [`01_hello_world.gom`](01_hello_world.gom) | `print` and statement terminators (`!`, `!!`, `!!!`) |
| 02 | [`02_variables.gom`](02_variables.gom) | `const`, `var`, reassignment, `previous`, type annotations |
| 03 | [`03_types.gom`](03_types.gom) | Numbers, strings, booleans, lists, `undefined`, conversions |
| 04 | [`04_operators.gom`](04_operators.gom) | Arithmetic and significant-whitespace precedence |

## Language fundamentals

| # | Program | What it teaches |
|---|---------|-----------------|
| 05 | [`05_tiered_equality.gom`](05_tiered_equality.gom) | `=` `==` `===` `====`, `;=`, and the `~` AEMI/ABI/AQMI operators |
| 06 | [`06_comparison_and_logic.gom`](06_comparison_and_logic.gom) | `>` `<` `>=` `<=`, `&`, `\|`, `;`, three-valued logic |
| 07 | [`07_control_flow.gom`](07_control_flow.gom) | `if` blocks and recursion instead of loops |
| 08 | [`08_functions.gom`](08_functions.gom) | Function declarations, space-call syntax, higher-order use |
| 09 | [`09_strings.gom`](09_strings.gom) | Interpolation, `.length`, reversal, `-1`-based indexing |
| 10 | [`10_lists.gom`](10_lists.gom) | `-1`-based indexing, `push`/`pop`, concatenation, reversal |
| 11 | [`11_maps.gom`](11_maps.gom) | `Map()`, bracket access, updates |
| 12 | [`12_classes.gom`](12_classes.gom) | `class`, `new`, the single-instance rule, methods |
| 13 | [`13_word_numbers.gom`](13_word_numbers.gom) | `zero`–`nineteen`, `twenty()`, `hundred()`, `half` |
| 14 | [`14_number_indexing.gom`](14_number_indexing.gom) | Digits of a number are indexable |
| 15 | [`15_lifetimes.gom`](15_lifetimes.gom) | `<N>` lives for N statements, `<-N>` hoists backwards |
| 16 | [`16_delete_and_confidence.gom`](16_delete_and_confidence.gom) | `delete`, `!`-priority overloading, `?` inspection |
| 17 | [`17_compound_assignment.gom`](17_compound_assignment.gom) | `+=` `-=` `*=` `/=` `^=` |
| 18 | [`18_emoji_identifiers.gom`](18_emoji_identifiers.gom) | Emoji names for variables and functions |
| 19 | [`19_reactive.gom`](19_reactive.gom) | `when` watchers, `reverse`, `use` signals |
| 20 | [`20_math_builtins.gom`](20_math_builtins.gom) | The 17 math built-ins |
| 21 | [`21_negative_indentation.gom`](21_negative_indentation.gom) | Cosmetic leading `}` |
| 22 | [`22_async_and_redefinition.gom`](22_async_and_redefinition.gom) | `async` functions and redefining number literals |
| 24 | [`24_comments.gom`](24_comments.gom) | `//` and `/* */` comments |
| 25 | [`25_regex.gom`](25_regex.gom) | `regex_match`, `regex_findall`, `regex_replace` |
| 26 | [`26_noop_and_misc.gom`](26_noop_and_misc.gom) | `noop`, the empty value `()`, boolean conversion |

## Strings, numbers, and values

| # | Program | What it teaches |
|---|---------|-----------------|
| 27 | [`27_escape_sequences.gom`](27_escape_sequences.gom) | `\n`, `\t`, `\\`, `\"` and friends |
| 28 | [`28_three_valued_logic.gom`](28_three_valued_logic.gom) | Reasoning about the third truth value |
| 30 | [`30_currency_interpolation.gom`](30_currency_interpolation.gom) | `$` `£` `¥` `€` interpolation forms |
| 33 | [`33_confidence_levels.gom`](33_confidence_levels.gom) | Confidence terminators and `?` |
| 34 | [`34_output_formatting.gom`](34_output_formatting.gom) | Printing values and interpolation |
| 35 | [`35_random_numbers.gom`](35_random_numbers.gom) | `random`, `randomInt`, simulated coin flips |
| 48 | [`48_unicode_and_emoji.gom`](48_unicode_and_emoji.gom) | Unicode inside identifiers and strings |

## Control flow and time

| # | Program | What it teaches |
|---|---------|-----------------|
| 29 | [`29_recursion_patterns.gom`](29_recursion_patterns.gom) | Countdown, accumulation, mutual recursion |
| 31 | [`31_next_promises.gom`](31_next_promises.gom) | `next` and deferred values |
| 32 | [`32_after_statements.gom`](32_after_statements.gom) | `after N { … }` scheduled blocks |
| 36 | [`36_sleep_and_timing.gom`](36_sleep_and_timing.gom) | Blocking delays and scheduled ticks |
| 45 | [`45_guessing_game.gom`](45_guessing_game.gom) | A self-playing simulation driven by `when` |
| 46 | [`46_reactive_monitor.gom`](46_reactive_monitor.gom) | Threshold alerts with reactive `when` |

## Programs and data

| # | Program | What it teaches |
|---|---------|-----------------|
| 23 | [`23_algorithms.gom`](23_algorithms.gom) | Fibonacci, recursive power, list sum, GCD |
| 37 | [`37_multifile_sections.gom`](37_multifile_sections.gom) | `=====` sections with `export`/`import` |
| 38 | [`38_persistent_constants.gom`](38_persistent_constants.gom) | `const const const` values that outlive a run |
| 39 | [`39_list_algorithms.gom`](39_list_algorithms.gom) | Recursive sum, max, search, reversal |
| 40 | [`40_map_frequency.gom`](40_map_frequency.gom) | Frequency counting with `Map()` |
| 41 | [`41_factorial_combinatorics.gom`](41_factorial_combinatorics.gom) | Factorials, permutations, combinations |
| 42 | [`42_string_processing.gom`](42_string_processing.gom) | Length, reversal, palindromes, regex |
| 43 | [`43_stack_queue.gom`](43_stack_queue.gom) | Stack and queue implementations |
| 44 | [`44_nested_data_structures.gom`](44_nested_data_structures.gom) | Lists of lists, maps of lists, lists of maps |
| 47 | [`47_type_annotations.gom`](47_type_annotations.gom) | `Int`, `Number`, `String`, `Bool`, `List` |

## Spec conformance

| # | Program | What it teaches |
|---|---------|-----------------|
| 49 | [`49_dreamb_spec.gom`](49_dreamb_spec.gom) | Examples lifted from the upstream specification: the four declaration forms, arbitrary quoting, parentheses-as-whitespace, loose/precise/literal equality, object literals, Cape Verdean interpolation, signals, and automatic insertion (AEMI/ABI/AQMI) |

## Feature coverage

Across the 49 programs, every documented language feature appears at least once:

- **Syntax** — all four terminators, automatic insertion, comments, 3-space
  indentation, negative indentation, significant whitespace, parentheses
- **Declarations** — `const const`, `const var`, `var const`, `var var`,
  `const const const`, lifetimes, hoisting, confidence overloading, `delete`
- **Types** — numbers, strings, booleans (`true`/`false`/`maybe`), lists, maps,
  object literals, functions, classes, `undefined`, `noop`, the empty value
- **Operators** — arithmetic, unary minus/reversal, comparison, logical
  operators, four equality tiers, three tilde operators, `;=`, compound
  assignment, postfix `++`/`--`
- **Text** — arbitrary quote counts, escape sequences, regex, five currency
  interpolation forms including `{obj$prop}`
- **Flow** — `if`, recursion, `async`, `after`, `when`, `reverse`, `next`,
  `use` signals, `export`/`import` across named sections
- **Libraries** — 17 math built-ins, word numbers and fractions, type
  conversions, file I/O, random numbers
