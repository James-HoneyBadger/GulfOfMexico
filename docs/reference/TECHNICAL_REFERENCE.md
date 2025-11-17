# Gulf of Mexico Technical Reference

The definitive (and slightly ridiculous) technical specification for the *perfect* programming language.

## Table of Contents

1. [Lexical Structure](#lexical-structure)
2. [Data Types](#data-types)
3. [Variables and Constants](#variables-and-constants)
4. [Operators](#operators)
5. [Control Flow](#control-flow)
6. [Functions](#functions)
7. [Classes](#classes)
8. [Arrays](#arrays)
9. [Reactive Programming](#reactive-programming)
10. [Async/Await](#asyncawait)
11. [Multi-File Programs](#multi-file-programs)
12. [Built-in Functions](#built-in-functions)
13. [Special Features](#special-features)

## Lexical Structure

### Tokens

Gulf of Mexico source code consists of:

- **Keywords**: Reserved words with special meaning
- **Identifiers**: Names for variables, functions, classes
- **Literals**: Numbers, strings, booleans
- **Operators**: Symbols for operations
- **Delimiters**: Parentheses, brackets, braces
- **Statement terminators**: The almighty `!`

### Comments

Single-line comments begin with `//`:

```gom
// This is a comment
const x 42!  // End-of-line comment
```

Multi-line comments are not supported. Just use multiple single-line comments like a champion.

### Statement Terminator

Every statement MUST end with `!`:

```gom
const x 42!
print(x)!
```

Forgetting the `!` will result in parse errors and existential sadness.

### Whitespace

- **Indentation**: Use 3 spaces (yes, three) for code blocks
- **Line breaks**: Separate statements
- **Spaces**: Generally ignored except for readability

Example:

```gom
if x > 10 {
   print("x is big")!
   print("very big")!
}
```

Note the 3-space indentation. Two is too few, four is too many.

### Identifiers

Variable, function, and class names:

- Must start with a letter or underscore
- Can contain letters, numbers, underscores
- Case-sensitive

```gom
const myVariable 42!
const _private 99!
const camelCase "style"!
const snake_case "also_fine"!
```

## Data Types

### Numbers

**Integers**:
```gom
const answer 42!
const negative -17!
```

**Floating-point**:
```gom
const pi 3.14159!
const tiny 0.001!
```

Numbers support standard arithmetic operations.

### Strings

Enclosed in single or double quotes:

```gom
const name "Alice"!
const message 'Hello'!
```

**String interpolation** with `${}`:

```gom
const greeting "Hello, ${name}!"!
const math "2 + 2 = ${2 + 2}"!
```

### Booleans

Three values (yes, three):

```gom
const yes true!
const no false!
const uncertain maybe!
```

The `maybe` value represents uncertainty. Because life is complicated.

### Arrays

Ordered collections starting at index -1:

```gom
const numbers [1, 2, 3, 4]!
const mixed [42, "text", true]!
const nested [[1, 2], [3, 4]]!
```

See [Arrays](#arrays) for details.

### Objects

Created from classes:

```gom
class Thing { var value 0! }!
const obj new Thing()!
```

### None/Null

Currently implicit. Variables without values don't exist yet.

## Variables and Constants

### Const - Immutable

```gom
const x 42!
const name "Bob"!
```

Cannot be reassigned. Attempting to do so results in errors and judgmental looks from your computer.

### Var - Mutable

```gom
var count 0!
count = 10!
count = 20!
```

Can be reassigned freely. Live your truth.

### Const Var - Immutable Reference, Mutable Content

```gom
const var list [1, 2, 3]!
list[-1] = 100!     // ✓ Modify content
list = [4, 5, 6]!   // ✗ Can't reassign
```

The reference is constant, but the content can change. It's philosophical.

### Confidence Levels (Probabilistic Variables)

Variables can be declared with multiple confidence levels:

```gom
var value 10!       // Confidence: 1
var value 20!!      // Confidence: 2 (wins)
var value 15!!!     // Confidence: 3 (wins)
var value 5!!!!     // Confidence: 4 (wins)
```

The declaration with the most `!` marks wins. Democracy in action.

### Variable Lifetimes

**Line-based**:

```gom
const temp 100 = 999!  // Expires after 100 lines
```

**Time-based**:

```gom
const brief <5.0> = "Poof"!  // Expires after 5 seconds
```

After expiration, the variable becomes undefined. All things must pass.

## Operators

### Arithmetic

| Operator | Meaning | Example |
|----------|---------|---------|
| `+` | Addition | `a + b` |
| `-` | Subtraction | `a - b` |
| `*` | Multiplication | `a * b` |
| `/` | Division | `a / b` |
| `^` | Exponentiation | `a ^ b` |

### Comparison

| Operator | Meaning | Example |
|----------|---------|---------|
| `<` | Less than | `a < b` |
| `>` | Greater than | `a > b` |
| `<=` | Less than or equal | `a <= b` |
| `>=` | Greater than or equal | `a >= b` |

### Equality (Four Levels of Paranoia)

| Operator | Strictness | Description |
|----------|------------|-------------|
| `=` | Approximate | Very loose, coerces types freely |
| `==` | Standard | Normal equality you'd expect |
| `===` | Strict | Type-aware, more careful |
| `====` | Strictest | Absolutely no funny business |

Examples:

```gom
42 = "42"      // true (approximate)
42 == "42"     // false (standard)
42 === 42.0    // false (strict about types)
42 ==== 42     // true (exactly the same)
```

### Logical

| Operator | Meaning | Example |
|----------|---------|---------|
| `&` | AND | `a & b` |
| `\|` | OR | `a \| b` |
| `;` | NOT | `;a` |

Works with three-valued logic:

```gom
true & false    // false
true | maybe    // true
;maybe          // maybe
```

### Assignment

| Operator | Meaning |
|----------|---------|
| `=` | Assign value |

```gom
x = 42!
list[0] = 100!
obj.field = "value"!
```

## Control Flow

### If Statements

```gom
if condition {
   // code
}
```

No `else` clause. Keep it simple. If you need branching, use multiple `if` statements:

```gom
if x > 10 {
   print("big")!
}

if x <= 10 {
   print("small")!
}
```

**Nested if**:

```gom
if x > 0 {
   if x < 100 {
      print("in range")!
   }
}
```

### When Statements (Reactive)

Triggers whenever the condition becomes true:

```gom
var count 0!

when count > 5 {
   print("Exceeded 5!")!
}

count = 10!  // Triggers the when block
```

See [Reactive Programming](#reactive-programming).

### After Statements (Delayed)

Execute after a time delay:

```gom
after <2.0> {
   print("2 seconds later...")!
}
```

Accepts time in seconds as a floating-point number.

## Functions

### Function Declaration

**Standard form**:

```gom
function name(param1, param2) => {
   // body
   return value!
}!
```

**Short form** (single expression):

```gom
fn name(param) => expression!
```

### Examples

```gom
function add(a, b) => {
   return a + b!
}!

fn square(x) => x * x!

function greet(name) => {
   const msg "Hello, ${name}!"!
   print(msg)!
   return msg!
}!
```

### Calling Functions

**Call Syntax Rules:**

Gulf of Mexico uses a hybrid call syntax that depends on the number of arguments:

1. **Functions with arguments** - Use space-separated syntax:
   ```gom
   const result add 5 3!
   const sq square 10!
   greet "Alice"!
   ```

2. **Zero-argument functions** - Require parentheses to disambiguate from name references:
   ```gom
   const value getValue()!
   doSomething()!
   ```

3. **Parenthesized syntax** - Also valid for any function call:
   ```gom
   const result add(5, 3)!
   const sq square(10)!
   greet("Alice")!
   const value getValue()!
   ```

**Why this rule?** Without parentheses, `getValue!` would be interpreted as referencing the function itself rather than calling it. The parser requires explicit parentheses for zero-arg calls.

**Method calls** follow the same rules:
```gom
obj.method()!        // Zero args - parentheses required
obj.method arg!      // One arg - space-separated or parentheses
obj.method(arg)!     // One arg - parentheses form
```

### Return Values

Use `return` to return a value:

```gom
function getValue() => {
   return 42!
}!
```

Functions without explicit `return` return nothing (implicitly).

## Classes

### Class Declaration

```gom
class ClassName {
   var field1 initial_value!
   var field2 initial_value!
   
   function method1() => {
      // body
   }!
   
   function method2(param) => {
      // body
   }!
}!
```

### Creating Instances

Use `new` with the class name:

```gom
const obj = new ClassName!
```

**With Constructor Arguments:**

If a class defines an `init` method, you can pass arguments during instantiation using parenthesized syntax:

```gom
class Person {
   var name = "Unknown"!
   var age = 0!
   
   function init(n, a) => {
      name = n!
      age = a!
   }!
}!

const alice = new(Person, "Alice", 30)!
```

**Note**: Constructor calls with arguments require parentheses: `new(Class, arg1, arg2)`. Space-separated syntax `new Class arg1 arg2` is not supported due to parser limitations.

Classes without an `init` method work as before - instances are created with default field values.

### Accessing Fields and Methods

```gom
obj.field1 = value!
const x obj.field2!
obj.method1()!
```

### Example

```gom
class Counter {
   var count 0!
   
   function increment() => {
      count = count + 1!
   }!
   
   function getValue() => {
      return count!
   }!
}!

const c new Counter()!
c.increment()!
c.increment()!
print(c.getValue())!  // 2
```

### Scope

Inside methods, `field` refers to the instance field. No `this` or `self` keyword needed—context is implicit.

## Arrays

### Indexing Starts at -1

The first element is at index -1:

```gom
const arr [10, 20, 30, 40]!

arr[-1]  // 10 (first)
arr[0]   // 20 (second)
arr[1]   // 30 (third)
arr[2]   // 40 (fourth)
```

### Fractional Indexing

Insert elements between existing indices:

```gom
const list ["a", "c"]!
list[0.5] = "b"!
// Result: ["a", "b", "c"]
```

The interpreter finds the fractional position and inserts accordingly.

### Assignment

```gom
const var nums [1, 2, 3]!
nums[0] = 99!
// Result: [1, 99, 3]
```

### Multi-dimensional Arrays

```gom
const matrix [[1, 2], [3, 4]]!
const val matrix[0][0]!  // 2 (remember, indexing at -1!)
```

## Reactive Programming

### When Statements

React to changes in variables:

```gom
var x 0!

when x > 10 {
   print("x exceeded 10!")!
}

x = 15!  // Triggers the when block
```

Multiple `when` blocks can watch the same variable.

### Execution Model

When a watched variable changes, all relevant `when` blocks are evaluated. If the condition is true, the block executes.

### Example

```gom
var temp 20!

when temp > 30 {
   print("Hot!")!
}

when temp < 10 {
   print("Cold!")!
}

temp = 35!  // Prints "Hot!"
temp = 5!   // Prints "Cold!"
```

## Async/Await

### Async Functions

Declare a function as `async`:

```gom
async function fetchData() => {
   return 42!
}!
```

### Await Expression

Use `await()` to wait for an async function:

```gom
const result await(fetchData())!
```

### Example

```gom
async function getData() => {
   return 100!
}!

async function process(value) => {
   return value * 2!
}!

const data await(getData())!
const processed await(process(data))!
print(processed)!  // 200
```

### Note

The current implementation executes async functions synchronously (they're not truly asynchronous). It's the thought that counts.

## Multi-File Programs

### File Sections

Use `===== filename =====` to define file sections:

```gom
===== utilities =====

function helper() => 42!
export helper to main!

===== main =====

import helper!
print(helper())!
```

### Export Statement

```gom
export name to target_file!
```

Exports `name` (variable or function) to `target_file`.

### Import Statement

```gom
import name!
```

Imports `name` from another file section.

### Example

```gom
===== math =====

function add(a, b) => a + b!
const pi 3.14159!

export add to main!
export pi to main!

===== main =====

import add!
import pi!

print(add(2, 3))!
print(pi)!
```

## Built-in Functions

### I/O

| Function | Description |
|----------|-------------|
| `print(value)` | Print to stdout |
| `read(filename)` | Read file contents |
| `write(filename, content)` | Write to file |

### Type Conversion

| Function | Description |
|----------|-------------|
| `Number(value)` | Convert to number |
| `String(value)` | Convert to string |
| `Boolean(value)` | Convert to boolean |

### Utilities

| Function | Description |
|----------|-------------|
| `Map()` | Create a dictionary/map |
| `sleep(seconds)` | Pause execution |
| `exit(code)` | Exit program |

### Math Functions

| Function | Description |
|----------|-------------|
| `sin(x)`, `cos(x)`, `tan(x)` | Trigonometry |
| `sqrt(x)` | Square root |
| `log(x)`, `log10(x)` | Logarithms |
| `abs(x)` | Absolute value |
| `floor(x)`, `ceil(x)`, `round(x)` | Rounding |

### Regex Functions

| Function | Description |
|----------|-------------|
| `regex_match(pattern, text)` | Match pattern |
| `regex_findall(pattern, text)` | Find all matches |
| `regex_replace(pattern, replacement, text)` | Replace matches |

### Word Numbers

Constants and functions for numeric values:

```gom
zero, one, two, three, ... nineteen  // Constants 0-19
twenty(), thirty(), forty(), ...     // Functions for 20, 30, 40...
```

Example:

```gom
const x five!             // 5
const y twenty() + three! // 23
```

## Special Features

### Debug Levels

Add `?` marks to statements for debug output:

```gom
const x 10?       // Level 1 debug
const y 20??      // Level 2 debug
const z 30???     // Level 3 debug
const w 40????    // Level 4 debug
```

Higher levels print more detailed information.

### Previous Values

Access previous values of variables:

```gom
var x 10!
x = 20!
const old previous(x)!  // 10
```

### Reverse Function

Reverse strings or arrays:

```gom
const backwards reverse("hello")!  // "olleh"
const revArray reverse([1, 2, 3])! // [3, 2, 1]
```

### Delete Operator

Remove elements from arrays:

```gom
const var list [1, 2, 3]!
delete list[0]!  // Remove second element
// Result: [1, 3]
```

## Grammar Summary

Simplified grammar notation:

```
Program       := FileSection* Statement*
FileSection   := "=====" Identifier "=====" Statement*
Statement     := Declaration | Assignment | FunctionCall | 
                 IfStmt | WhenStmt | AfterStmt | 
                 ClassDecl | FunctionDecl | Return | 
                 Import | Export | Delete "!"
                 
Declaration   := ("const" | "var" | "const var") Identifier Expression "!"
Assignment    := LValue "=" Expression "!"
IfStmt        := "if" Expression "{" Statement* "}"
WhenStmt      := "when" Expression "{" Statement* "}"
AfterStmt     := "after" "<" Number ">" "{" Statement* "}"

Expression    := Literal | Identifier | BinaryOp | UnaryOp | 
                 FunctionCall | ArrayAccess | MemberAccess | 
                 StringInterpolation | ArrayLiteral
```

## Error Handling

Gulf of Mexico has... creative error handling. Errors are printed to stderr with context when possible. There's no `try/catch` mechanism. Embrace the chaos.

## Performance Notes

- Interpreted, not compiled
- No optimization (yet)
- Reactive watchers add overhead
- Async is synchronous (paradox!)

Don't use this for production. Unless you're feeling *very* adventurous.

## Limitations and Known Issues

- No `else` clause for `if`
- No loops (use recursion like it's 1958)
- No exceptions/error handling
- Classes lack constructors with parameters
- Async isn't actually async
- Fractional indexing can be slow
- Three-space indentation is mandatory

But hey, it's *perfect*, remember?

## Compliance

This implementation is based on the conceptual design by [Lu Wilson (TodePond)](https://github.com/TodePond/GulfOfMexico). Some features may differ from other implementations. This is fine. Embrace variety.

## Example Programs

The repository includes **80+ example programs** organized by category:

- **Basics**: `programs/01_basics/` - Hello world through conditionals
- **Features**: `programs/02_features/` - Equality, logic, reactive, async, lifetimes
- **Graphics**: `programs/03_graphics/` - Canvas, transforms, generative art
- **Satirical**: `programs/04_satirical/` - Emotional, quantum, time travel programming
- **Analysis**: `programs/05_analysis/` - Statistics, finance, business, scientific
- **Compiler Examples**: `compiler/examples/` - C++ compiler validation
- **Demos**: `programs/demos/` - Complete applications (banking, RPG, task manager)
- Internal GOM test programs were removed in Nov 2025. Python unit tests live in `tests/`.

See [programs/README.md](programs/README.md) for complete documentation and [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for validation results.

---

*You've now mastered the technical depths of Gulf of Mexico. Use this knowledge wisely, or foolishly. Both are valid.*
