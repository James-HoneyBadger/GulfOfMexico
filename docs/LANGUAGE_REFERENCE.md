# Gulf of Mexico — Language Reference

Complete syntax and semantics reference for the Gulf of Mexico programming language (v1.0.0).

> **Notation**: Code examples use `// comment` to annotate expected output or behavior. The arrow `→` indicates the result of an expression.

---

## Table of Contents

1. [Syntax Fundamentals](#1-syntax-fundamentals)
2. [Data Types](#2-data-types)
3. [Variables](#3-variables)
4. [Operators](#4-operators)
5. [Functions](#5-functions)
6. [Control Flow](#6-control-flow)
7. [Classes](#7-classes)
8. [Reactive Features](#8-reactive-features)
9. [Word Numbers and Fractions](#9-word-numbers-and-fractions)
10. [Math Functions](#10-math-functions)
11. [Type Conversions](#11-type-conversions)
12. [I/O](#12-io)
13. [Multi-File Programs](#13-multi-file-programs)
14. [Miscellaneous](#14-miscellaneous)
15. [DreamBerd Extensions](#15-dreamberd-extensions)
16. [Environment Variables](#16-environment-variables)
17. [Grammar Summary](#17-grammar-summary)
18. [Standard Helpers (Prelude)](#18-standard-helpers-prelude)

---

## 1. Syntax Fundamentals

### 1.1 Statement Terminators

Every statement must end with one or more `!` marks (the *confidence terminator*) or a `?` mark (the *debug terminator*). The number of `!` marks expresses confidence level:

| Terminator | Meaning |
|------------|---------|
| `!` | Normal confidence — always executes |
| `!!` | High confidence — always executes |
| `!!!` | Absolute confidence — always executes |
| `?` | Debug — executes and prints debug info to stderr |

```
print "normal"!
print "confident"!!
print "very confident"!!!
const x = 42?            // assigns and prints debug info
```

All confidence levels currently execute identically. The distinction is semantic and may gain behavioral meaning in future versions.

#### 1.1.1 Automatic Insertion (AEMI, ABI, AQMI)

The spec's "AI" features are implemented as error recovery, so forgotten
punctuation is repaired instead of rejected:

| Feature | Name | What it does |
|---------|------|--------------|
| AEMI | Automatic Exclamation Mark Insertion | A statement with no `!`/`?` gets one at the end of its line. |
| ABI | Automatic Bracket Insertion | Unclosed `(`, `[`, and `{` are closed at end of file. |
| AQMI | Automatic Quotation Marks Insertion | An unterminated string is closed at the end of its line (or end of file for triple-quoted strings). |

```
print("Hello world")     // AEMI adds the !
print("Hello world"      // ABI adds the )
print("Hello world       // AQMI adds the "
```

### 1.2 Comments

```
// Single-line comment (everything after // is ignored)

/* Block comment
   spanning multiple
   lines */
```

### 1.3 Indentation

Indentation **must** use multiples of **3 spaces**. Tabs are not supported.

```
if true {
   print "3 spaces"!        // ✓ correct
   if true {
      print "6 spaces"!     // ✓ correct
   }
}
```

Using any other indentation (e.g. 2 or 4 spaces) is a parse error.

### 1.4 Significant Whitespace

Whitespace between tokens controls operator precedence. In binary expressions, **tighter spacing binds first**:

```
2 * 1+3       // → 2 * (1+3) → 8     (+ binds tighter — no spaces)
2*1 + 3       // → (2*1) + 3 → 5     (* binds tighter — no spaces)
2 * 1 + 3     // → (2*1) + 3 → 5     (equal spacing — normal precedence)
```

When two operators have exactly the same surrounding whitespace, normal
operator precedence breaks the tie (`*` before `+`, arithmetic before
comparison, comparison before equality, and so on). This is what makes the
spec's `2 + 2 === 5` evaluate as `(2 + 2) === 5`.

This also affects function call parsing. A **single space** between a name and an argument is interpreted as a function call:

```
greet "World"       // calls greet("World")
func n - 1          // calls func(n), then subtracts 1
func  n - 1         // calls func(n - 1) — double space = wider gap
```

### 1.5 Parentheses

Parentheses act as whitespace, but a parenthesised group is evaluated as a
single unit. This preserves the spec's claim that parentheses "do nothing"
(`add)3, 2(!` still calls `add(3, 2)`) while making the spec's worked examples
behave as written:

```
add(3, 2)          // parenthesised call
add 3, 2           // space-separated call — same result
(add (3, 2))       // extra parentheses are harmless
add)3, 2(!         // stray parentheses are treated as whitespace
add(3, (add (5, 6)))   // nested calls build nested groups
print(1 + 2*3)     // → 7   (the group is the argument to print)
```

Stray, unmatched parentheses are ignored. This means the Lisp-style forms in
the spec (and the deliberately mismatched ones) all evaluate the same way.

---

## 2. Data Types

### 2.1 Numbers

Standard integers and floating-point numbers:

```
const a = 42!
const b = 3.14!
const c = -7!
```

Numbers are **indexable by digit** using -1-based indexing:

```
const n = 12345!
n[-1]     // → 1  (first digit)
n[0]      // → 2  (second digit)
n[1]      // → 3
n[3]      // → 5  (last digit)
```

Precision constant: integers are represented as floats internally. Values within `1e-9` of a whole number are coerced to integer display.

### 2.2 Strings

Strings use double or single quotes interchangeably:

```
const a = "hello"!
const b = 'hello'!      // identical to above
```

Strings may use **any number of quotes**, and the number of opening quotes
must match the number of closing quotes. This allows embedding quotes without
escaping:

```
const a = 'Lu'!                 // Lu
const b = '''Lu'''!             // Lu
const c = """"Luke""""!         // Luke
const s = ""she said "hi"""!    // she said "hi"
const empty = ""!               // empty string
```

A quote run with no matching closing run is an empty string when it is even
in length, and an unterminated string is auto-closed (AQMI) otherwise. A bare
word with no quotes at all (`const name = Luke!`) is also a string.

#### 2.2.1 String Interpolation

Currency symbols mark interpolated expressions inside strings:

| Prefix | Symbol | Example |
|--------|--------|---------|
| Dollar | `$` | `"value: ${x}"` |
| Pound | `£` | `"value: £{x}"` |
| Yen | `¥` | `"value: ¥{x}"` |
| Euro | `€` | `"value: {x}€"` (postfix) |
| Cape Verdean escudo | `$` | `"Hello {player$name}!"` (property access) |

Expressions inside braces are evaluated:

```
const x = 42!
print "${x + 1}"!     // "43"
print "£{x * 2}"!     // "84"
```

The Cape Verdean escudo form places `$` in the decimal-separator position and
acts as property access, so `{player$name}` reads `player.name`:

```
const player = { name: "Lu" }!
print "Hello {player$name}!"!    // Hello Lu!
```

#### 2.2.2 Escape Sequences

| Sequence | Character |
|----------|-----------|
| `\n` | Newline |
| `\t` | Tab |
| `\r` | Carriage return |
| `\\` | Backslash |
| `\"` | Double quote |
| `\'` | Single quote |
| `\0` | Null |
| `\b` | Backspace |
| `\f` | Form feed |
| `\v` | Vertical tab |

#### 2.2.3 String Operations

```
const s = "hello"!
s.length              // → 5
"abc" + "def"         // → "abcdef"  (concatenation)
-"hello"              // → "olleh"   (unary minus reverses)
s[-1]                 // → "h"       (first character, -1-based)
```

Strings also answer to the following methods. They are reached with a dot,
either on a name (`s.upper()`) or directly on a literal (`"a,b".split(",")`):

| Method | Result |
|--------|--------|
| `length` | number of characters (property) |
| `split(sep)` | list of the pieces around `sep` |
| `upper()` / `lower()` | case conversion |
| `trim()` | leading/trailing whitespace removed |
| `replace(old, new)` | every occurrence replaced |
| `contains(part)` | boolean |
| `startsWith(prefix)` / `endsWith(suffix)` | boolean |
| `indexOf(part)` | -1-based index, or `undefined` |
| `push(value)` / `pop()` | mutate in place (as for lists) |

### 2.3 Booleans (Three-Valued)

GOM implements three-valued logic with the following boolean values:

| Value | Meaning |
|-------|---------|
| `true` | Always true |
| `false` | Always false |
| `maybe` | Probabilistic — evaluates to `true` approximately 50% of the time |

`maybe` is the distinguishing feature of GOM's type system. Conditions involving `maybe` execute probabilistically:

```
if maybe {
   print "coin flip!"!    // prints ~50% of the time
}
```

Boolean conversion from numbers:

| Input | Result |
|-------|--------|
| `Boolean(0)` | `false` |
| `Boolean(1)` | `true` |
| `Boolean(0.3)` | `maybe` (any non-0, non-1 value) |

Logical NOT uses the **semicolon** prefix:

```
;true     // → false
;false    // → true
;maybe    // → maybe
```

### 2.4 Lists

```
const arr = [1, 2, 3]!
const empty = []!
```

#### 2.4.1 -1-Based Indexing

**All indexing in GOM starts at -1.** This applies to lists, strings, and numbers.

```
const arr = [10, 20, 30]!
arr[-1]     // → 10  (first element)
arr[0]      // → 20  (second element)
arr[1]      // → 30  (third element)
```

For a list of length N, valid indices are `-1` through `N - 2`.

#### 2.4.2 List Methods

```
var list = [1, 2, 3]!
list.push 4!             // append → [1, 2, 3, 4]  (space syntax)
list.pop()!              // remove last → [1, 2, 3], returns 4
list.length              // → 3  (property, not method)
```

| Method | Result |
|--------|--------|
| `push(value)` / `pop()` | append / remove the last element (mutates) |
| `insert(index, value)` | insert at a -1-based index (mutates) |
| `sort()` / `reverse()` | sort / reverse in place (mutates) |
| `indexOf(value)` | -1-based index, or `undefined` |
| `contains(value)` | boolean |
| `slice(from, to)` | new list from `from` up to `to` |
| `join(separator)` | string |
| `length` | element count (property) |

#### 2.4.3 List Operations

```
[1, 2] + [3, 4]         // → [1, 2, 3, 4]  (concatenation)
-[1, 2, 3]              // → [3, 2, 1]      (reverse)
```

### 2.5 Maps

Key-value data structure. Maps can be created with `Map()` or with an object
literal using braces:

```
var m = Map()!
m["key"] = "value"!       // set via bracket notation
print m["key"]!            // → "value"

const player = { name: "Lu", age: 29 }!
print player["name"]!      // → "Lu"
print player.name!         // → "Lu"  (dot access)
```

Maps have methods too. Methods win over entries when a name collides:

| Method | Result |
|--------|--------|
| `keys()` | list of keys |
| `values()` | list of values |
| `has(key)` | boolean |
| `delete(key)` | remove the entry (mutates) |
| `length` | entry count (property) |

### 2.6 Undefined

The absence of a value:

```
const nothing = undefined!
```

### 2.7 Type Summary

| Type | Literal Syntax | Mutable | Indexable |
|------|---------------|---------|-----------|
| Number | `42`, `3.14`, `-7` | No | By digit |
| String | `"hello"`, `'world'` | No | By character |
| Boolean | `true`, `false`, `maybe` | No | No |
| List | `[1, 2, 3]` | Yes | By element |
| Map | `Map()`, `{ key: value }` | Yes | By key / property |
| Function | `function f() => { ... }!` | No | No |
| Object | `new ClassName` | Yes | By property |
| Undefined | `undefined` | No | No |

---

## 3. Variables

### 3.1 Declaration

There are four declaration forms, built from the `const` and `var` keywords.
The first keyword controls **re-assignment** (via `=`) and the last controls
**editing** (mutating a value in place, e.g. `list.push`):

| Form | Re-assignable | Editable | Example |
|------|---------------|----------|---------|
| `const const` | No | No | `const const name = "Luke"!` |
| `const var` | No | Yes | `const var name = "Luke"! name.pop()!` |
| `var const` | Yes | No | `var const name = "Luke"! name = "Lu"!` |
| `var var` | Yes | Yes | `var var name = "Luke"! name.push("e")!` |

A single `const` declares an immutable binding and a single `var` a mutable
one:

```
const x = 42!          // immutable — cannot be reassigned
var y = 10!            // mutable — can be reassigned
```

Attempting a disallowed operation raises an error. Three `const`s make a
value permanently persistent (see §3.8).

### 3.2 Reassignment

Mutable variables are reassigned with a bare assignment (no keyword):

```
var counter = 0!
counter = counter + 1!
```

### 3.3 Type Annotations

Optional type annotations can be added at declaration. They are checked at the
time of declaration — a value that does not match its declared type raises a
type error:

```
var x: Int = 42!
var s: String = "hello"!
var b: Bool = true!

var bad: Int = "oops"!   // ✗ Error — type mismatch
```

Recognized annotations are `Int`, `Number`/`Float`, `String`, `Bool`, `List`,
`Map`, `Object`, and `Function`. Annotations naming an unknown or custom type
are not enforced and serve purely as documentation.

### 3.4 Variable Lifetimes

Variables can be given a **lifetime** — they automatically expire after N statements:

```
var temp <3> = "alive"!
print temp!              // ✓ statement 1
print temp!              // ✓ statement 2
print temp!              // ✓ statement 3
print temp!              // ✗ Error — temp has expired
```

Lifetimes can also be specified in seconds by appending `s`:

```
var flash <2.5s> = "brief"!    // expires after 2.5 seconds
```

### 3.5 Confidence Levels

Variables can be declared with a confidence percentage:

```
var x ~80~ = "probably here"!   // 80% confidence
```

### 3.6 Previous, Current, and Next Values

Access the prior value of a variable using `previous`, the present value with
`current`, and the next value with `next`:

```
var x = 100!
x = 200!
print x!                  // → 200
print previous x!         // → 100
print current x!          // → 200

const future = next x!    // promise for the next assigned value
x = 42!
print future!             // → 42
```

Postfix `++` and `--` update a variable in place, which also records a
`previous` value:

```
var score = 5!
score++!                  // score → 6
print previous score!     // → 5
score--!                  // score → 5
```

### 3.7 Delete

Remove a variable from scope:

```
var x = 42!
delete x!                 // x no longer exists
print x!                  // Error — x is not defined
```

`delete` can also remove values and even built-in keywords.

### 3.8 Const Const Const (Persistent Immutables)

Triple-const variables persist across program runs — they are saved to disk:

```
const const const PI = 3.14159!    // saved permanently
```

On subsequent runs, `PI` is loaded from the persistent store. These values survive interpreter restarts.

---

## 4. Operators

### 4.1 Arithmetic

| Operator | Operation | Example |
|----------|-----------|---------|
| `+` | Addition / concatenation | `3 + 4` → `7`, `"a" + "b"` → `"ab"` |
| `-` | Subtraction | `10 - 3` → `7` |
| `*` | Multiplication | `4 * 5` → `20` |
| `/` | Division (always float) | `10 / 3` → `3.333...` |
| `^` | Exponentiation | `2 ^ 10` → `1024` |
| Unary `-` | Negate / reverse | `-5` → `-5`, `-"abc"` → `"cba"`, `-[1,2]` → `[2,1]` |

### 4.2 Comparison

| Operator | Meaning |
|----------|---------|
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater than or equal |
| `<=` | Less than or equal |

Comparison returns a GOM boolean (`true`, `false`, or `maybe`).

### 4.3 Tiered Equality

GOM provides **four levels** of equality precision:

| Operator | Level | Behavior |
|----------|-------|----------|
| `=` | Approximate | Numbers: absolute difference ≤ 10. Strings: ~70% similar (fuzzy). |
| `==` | Loose | Same type: normal value equality. Different types: coerced (string) comparison. |
| `===` | Precise | Same value **and** same type. Mutable objects: same reference. |
| `====` | Most precise | The same literal expression / object identity. |

Inequality counterpart: `;=` (semicolon-equals, not `!=`).

```
10 = 15        // → true   (|15 − 10| = 5 ≤ 10)
10 = 25        // → false  (|25 − 10| = 15 > 10)
3.14 == "3.14" // → true   (loose — different types are coerced)
10 == 10.0     // → true   (same numeric value)
3.14 === "3.14" // → false  (precise — types differ)
10 === 10      // → true   (same type and value)
"hi" === 42    // → false  (different types)
const pi = 3.14!
3.14 ==== 3.14  // → true   (the same literal)
3.14 ==== pi    // → false  (a literal is not the variable's value)
10 ;= 5        // → true   (not approximately equal)
10 ;= 10       // → false  (approximately equal)
```

### 4.4 Tilde Equality (Approximate Match Operators)

GOM also provides three **tilde equality** operators for fuzzy comparison:

| Operator | Name | Behavior |
|----------|------|----------|
| `~=` | AEMI (Are Even Meaningfully Identical?) | Same type → `true`, different type → `maybe` |
| `~==` | ABI (Are Basically Identical?) | Case-insensitive string comparison, cross-type coercion |
| `~===` | AQMI (Are Quite Meaningfully Identical?) | Numbers within 1%, strings with normalized whitespace |

```
5 ~= 10              // → true   (same type)
5 ~= "hello"         // → maybe  (different types)
"Hello" ~== "hello"  // → true   (case-insensitive)
5 ~== "5"            // → true   (cross-type coercion)
100 ~=== 100.5       // → true   (within 1%)
100 ~=== 200         // → false  (not within 1%)
"hello  world" ~=== "hello world"  // → true (whitespace normalized)
```

> **Note**: Tilde equality expressions require double-space before the left operand when used with `print`: `print  5 ~= 10!`

### 4.5 Logical Operators

| Operator | Meaning | Notes |
|----------|---------|-------|
| `&` | Logical AND | Short-circuits. `maybe & maybe` → probabilistic |
| `\|` | Logical OR | Short-circuits. `maybe \| false` → probabilistic |
| `;` (prefix) | Logical NOT | `;true` → `false`, `;maybe` → `maybe` |

Three-valued logic truth tables:

**AND (`&`)**:
| | true | maybe | false |
|---|---|---|---|
| **true** | true | maybe | false |
| **maybe** | maybe | maybe | false |
| **false** | false | false | false |

**OR (`|`)**:
| | true | maybe | false |
|---|---|---|---|
| **true** | true | true | true |
| **maybe** | true | maybe | maybe |
| **false** | true | maybe | false |

### 4.6 Compound Assignment

Modify-in-place operators (requires a re-assignable binding):

| Operator | Equivalent |
|----------|------------|
| `x += 5!` | `x = x + 5!` |
| `x -= 3!` | `x = x - 3!` |
| `x *= 2!` | `x = x * 2!` |
| `x /= 4!` | `x = x / 4!` |
| `x ^= 2!` | `x = x ^ 2!` |
| `x++!` | `x = x + 1!` (postfix, updates the variable) |
| `x--!` | `x = x - 1!` (postfix, updates the variable) |

```
var var score = 100!
score += 50!
score -= 20!
score++!
print score!     // → 131
```

---

## 5. Functions

### 5.1 Definition

Functions may be declared with *any letters of the word `function` in order*:
`function`, `functi`, `func`, `fun`, `fn`, and `f` all work (as do
combinations such as `functn`). A function is followed by `=>` and either a
curly-brace body or a single expression:

```
function add(a, b) => {
   return a + b!
}!

fn double(n) => {
   return n * 2!
}!
```

### 5.2 Calling Conventions

Two call syntaxes:

```
// Parenthesized call (required for multiple arguments)
add(3, 7)!

// Space syntax (single argument only)
greet "World"!

// These are equivalent for single-arg functions:
greet("World")!
greet "World"!
```

### 5.3 Return Values

Functions return via `return`:

```
function square(n) => {
   return n * n!
}!
const result = square(5)!     // → 25
```

Functions without an explicit `return` return `undefined`.

### 5.4 Higher-Order Functions

Functions are first-class values — they can be passed as arguments and returned:

```
function applyTwice(f, x) => {
   return f(f(x))!
}!

function double(n) => {
   return n * 2!
}!

print applyTwice(double, 3)!   // → 12
```

### 5.5 Multiple Return Values

Return a list and destructure (or index) at the call site:

```
function divmod(a, b) => {
   return [a / b, a - b * (a / b)]!
}!

const result = divmod(17, 5)!
print result[-1]!     // quotient
print result[0]!      // remainder
```

---

## 6. Control Flow

### 6.1 Conditionals

```
if condition {
   // body — indented 3 spaces
}
```

There is no `else` keyword. Use sequential `if` blocks with early returns:

```
function classify(n) => {
   if n > 0 {
      return "positive"!
   }
   if n < 0 {
      return "negative"!
   }
   return "zero"!
}!
```

### 6.2 Recursion (No Loops)

GOM has **no loop constructs** (`for`, `while`, `do`). All iteration is done via recursion.

> **Important**: Recursive calls with computed arguments require intermediate variables. `factorial(n - 1)` will cause infinite recursion — use `const prev = n - 1!` then `factorial(prev)!` instead.

```
function factorial(n) => {
   if n <= 1 {
      return 1!
   }
   const prev = n - 1!
   return n * factorial(prev)!
}!

print factorial(5)!    // → 120
```

```
function forEach(list, fn, idx) => {
   const limit = list.length - 1!
   if idx < limit {
      fn(list[idx])!
      const next = idx + 1!
      forEach(list, fn, next)!
   }
}!
```

---

## 7. Classes

### 7.1 Declaration

```
class Dog {
   var name = "unnamed"!

   function bark() => {
      print "${name} says woof!"!
   }!
}!
```

### 7.2 Instantiation

Use `new` to create an instance:

```
const d = new Dog!
d.name = "Rex"!
d.bark()!              // → "Rex says woof!"
```

### 7.3 Single-Instance Rule

GOM enforces **one instance per class**. To create a second instance, `delete` the first:

```
var a = new Dog!
a.name = "Rex"!

delete a!              // free the instance slot
var b = new Dog!
b.name = "Fido"!
```

### 7.4 Property Access

Properties are accessed and set via dot notation:

```
const c = new Counter!
c.count = 10!
print c.count!
```

---

## 8. Reactive Features

### 8.1 When Watchers

Execute a block when a condition becomes true:

```
var x = 0!
when x > 5 {
   print "x exceeded 5!"!
}
x = 10!    // → triggers the when block
```

A `when` block is *armed* when it is declared and runs on the next mutation of
the values it reads — never at registration, even if the condition is already
true. It is re-evaluated after every assignment and runs each time an assignment
leaves the condition true, so it can fire repeatedly as the watched state keeps
qualifying.

```
var health = 10!
when health == 0 {
   print "You lose"!
}
// nothing runs here
health = 0!    // → You lose
```

> Use `==` in conditions. The approximate `=` operator treats values within 10
> as equal, so `when health = 0` is true for any `health` up to 10.

### 8.2 Next Promises

Capture the **next** value a variable will receive:

```
var x = 100!
const future = next x!
print future!           // → undefined (not yet resolved)
x = 42!                 // resolves the promise
print future!           // → 42
```

### 8.3 After Statements

`after` **schedules** a block; it does not block the current code. Scheduled
blocks run when their deadline arrives, in deadline order, and the program
waits for pending blocks before exiting:

```
print "start"!
after 1000 {
   print "one second later"!
}
print "end"!
// Output: start, end, one second later
```

Use `sleep` when you actually want to block (see §14.5).

### 8.4 Signals (`use`)

Create a reactive signal with getter/setter semantics:

```
const sig = use 0!       // initial value 0
sig 42!                  // set to 42
print sig()!             // → 42 (get)
```

### 8.5 Reverse

Replay all prior statements in the current scope in reverse order:

```
print "A"!
print "B"!
print "C"!
reverse!       // → prints C, B, A
```

---

## 9. Word Numbers and Fractions

### 9.1 Word Number Literals (0–19)

The following English words are built-in number literals:

`zero` (0), `one` (1), `two` (2), `three` (3), `four` (4), `five` (5), `six` (6), `seven` (7), `eight` (8), `nine` (9), `ten` (10), `eleven` (11), `twelve` (12), `thirteen` (13), `fourteen` (14), `fifteen` (15), `sixteen` (16), `seventeen` (17), `eighteen` (18), `nineteen` (19)

```
print five!         // → 5
print thirteen!     // → 13
```

### 9.2 Word Number Functions (20+)

Tens, hundreds, thousands, and millions are **functions** that add or multiply:

```
twenty(1)         // → 21
thirty(5)         // → 35
forty(0)          // → 40
hundred(3)        // → 300
thousand(2)       // → 2000
million(1)        // → 1000000
```

### 9.3 Named Fractions

```
half              // → 0.5
third             // → 0.333...
quarter           // → 0.25
```

---

## 10. Math Functions

17 built-in math functions:

| Function | Description | Example |
|----------|-------------|---------|
| `abs(x)` | Absolute value | `abs(-5)` → `5` |
| `floor(x)` | Round down | `floor(3.7)` → `3` |
| `ceil(x)` | Round up | `ceil(3.2)` → `4` |
| `round(x)` | Round to nearest | `round(3.5)` → `4` |
| `sqrt(x)` | Square root | `sqrt(16)` → `4` |
| `sin(x)` | Sine (radians) | `sin(0)` → `0` |
| `cos(x)` | Cosine (radians) | `cos(0)` → `1` |
| `tan(x)` | Tangent (radians) | `tan(0)` → `0` |
| `log(x)` | Natural logarithm | `log(1)` → `0` |
| `exp(x)` | e^x | `exp(0)` → `1` |
| `degrees(x)` | Radians → degrees | `degrees(3.14159)` → `~180` |
| `radians(x)` | Degrees → radians | `radians(180)` → `~3.14159` |
| `pow(x, y)` | x raised to y | `pow(2, 10)` → `1024` |
| `min(x, y)` | Minimum | `min(3, 7)` → `3` |
| `max(x, y)` | Maximum | `max(3, 7)` → `7` |
| `random()` | Random float [0, 1) | `random()` → `0.7291...` |
| `randomInt(a, b)` | Random integer [a, b] | `randomInt(1, 6)` → `4` |

---

## 11. Type Conversions

Explicit type conversion functions:

| Function | Description | Example |
|----------|-------------|---------|
| `String(x)` | Convert to string | `String(42)` → `"42"` |
| `Number(x)` | Convert to number | `Number("7")` → `7` |
| `Boolean(x)` | Convert to boolean | `Boolean(1)` → `true` |

Boolean conversion rules:

| Input | Result |
|-------|--------|
| `0` | `false` |
| `1` | `true` |
| Any other number | `maybe` |
| Empty string `""` | `false` |
| Non-empty string | `true` |

---

## 12. I/O

### 12.1 Output

```
print "hello"!              // print to stdout with newline
```

### 12.2 Input

```
const name = read "Enter name: "!    // read line from stdin
```

### 12.3 File I/O

```
write "file.txt", "content"!         // write string to file
```

### 12.4 Sleep

```
sleep 1000!                 // pause execution for 1000 milliseconds
```

---

## 13. Multi-File Programs

Source files can contain multiple named sections separated by `=====` markers:

```
===== utils =====
const PI = 3.14159!
export PI to main!

===== main =====
import PI from utils!
print PI!                   // → 3.14159
```

Each section is tokenized and executed independently. Data flows between sections via `export`/`import` statements. The section names in the markers determine the import namespace.

### 13.1 Import Tariff

Imports in GOM are subject to a **25% tariff**: when an `import` statement executes, the interpreter sleeps for a short random duration and may randomly remove one statement from the importing section. This is a deliberate language feature.

---

## 14. Miscellaneous

### 14.1 Noop

Do nothing — a valid statement:

```
noop!
```

### 14.2 Regex

Built-in regex functions for string matching. Each takes a **single string argument** with comma-separated parts:

```
// regex_match "pattern,string" → first match or undefined
const result = regex_match "\\d+,abc123def"!

// regex_findall "pattern,string" → list of all matches
const all = regex_findall "\\d+,a1b2c3"!

// regex_replace "pattern,replacement,string" → new string
const replaced = regex_replace "\\d,X,a1b2"!
```

### 14.3 Empty Value

`()` represents the empty value (equivalent to `undefined` in most contexts).

### 14.4 Sleep

`sleep N` blocks for N milliseconds. Use it when ordering matters; prefer
`after` (§8.3) for scheduling work without stopping the program.

```
print "waiting"!
sleep 500!
print "half a second later"!
```

### 14.5 Inverted Exclamation Mark

`¡` is an inverted exclamation mark. It acts as a statement terminator with
*negative priority*, so a declaration ending in `¡` loses to otherwise
equal declarations (see §15.6).

---

## 15. DreamBerd Extensions

These features align GOM with the [DreamBerd / Gulf of Mexico](https://github.com/TodePond/GulfOfMexico)
specification.

### 15.1 Emoji Identifiers

Emoji characters are valid in variable and function names:

```
const 🎉 = 42!
print 🎉!              // → 42

function 🚀(n) => {
   return n * 2!
}!
print 🚀(5)!           // → 10
```

### 15.2 Negative Lifetime Hoisting

A variable with a negative lifetime `<-N>` is **hoisted** — it becomes available N lines *before* its declaration:

```
print name!                    // Works! — hoisted from below
const const name<-1> = "Luke"!
```

### 15.3 Number Literal Redefinition

You can redefine what a number literal evaluates to:

```
const const 5 = 4!
print 2 + 5!           // → 6  (because 5 is now worth 4)
```

### 15.4 Negative Indentation

Leading `}` characters are cosmetic and ignored by the parser. This allows so-called "negative indentation":

```
}}}if true {
   print "deeply outdented"!
}
```

### 15.5 Async Interleaving

Functions declared with `async` queue their bodies for deferred execution:

```
async function later() => {
   print "second"!
}!
later()!
print "first"!
// Output: first, second
```

### 15.6 Variable Overloading

Declaring a variable that already exists with `const`/`var` creates a new binding that shadows the previous one. The value from `previous` still accesses the old value.

### 15.7 Object Literals

Braces create maps, and `$` inside an interpolated brace performs property
access (Cape Verdean escudo syntax from the spec):

```
const player = { name: "Lu", age: 29 }!
print player.name!                // → Lu
print "Hello {player$name}!"!     // → Hello Lu!
```

### 15.8 Signals

`use(value)` creates a signal. Calling it with a value sets it and calling it
with no arguments gets it. Signals can be destructured into a getter/setter
pair, and the split can be nested arbitrarily:

```
const var score = use(0)!
score(9)!          // set
print score()!     // → 9 (get)

const var [[getScore, setScore], setScore2] = use(0)!
setScore(4)!
print getScore()!  // → 4
```

### 15.9 Automatic Insertion (AEMI / ABI / AQMI)

Missing terminators, brackets, and quotes are repaired automatically. See
§1.1.1. AEMI applies at the end of every line; ABI and AQMI apply at the end
of the file (AQMI also closes a simple string at end of line).

### 15.10 Reference Equality (`====`)

`====` compares literal expressions rather than runtime values:

```
const pi = 3.14!
print 3.14 ==== 3.14!   // → true  (same literal)
print 3.14 ==== pi!     // → false (literal vs variable)
print pi ==== pi!       // → true  (same expression)
```

### 15.11 What Is Not Implemented

The upstream specification also contains deliberately unimplementable or
meta features. These are **not** part of the interpreter:

- DBX (`<div>Hello</div>`) and rich-text identifiers — GOM is a terminal
  interpreter, not a browser framework.
- SI/AI auto-completion that e-mails unfinished code to the language author.
- Vision Pro, edutainment, and installation-inception jokes.

Everything else in the specification's language sections is implemented.

---

## 16. Environment Variables

| Variable | Effect |
|----------|--------|
| `GULFOFMEXICO_DEBUG` | Set to any value to print internal debug messages to stderr |
| `GULFOFMEXICO_VERBOSE` | Set to any value to show completion messages |
| `GULFOFMEXICO_WAIT` | Set to any value to wait for pending after-statements at exit |
| `GOM_DISABLE_TARIFF` | Set to `1` to disable the random import tariff in §13.1 |
| `GOM_NO_PRELUDE` | Set to `1` to skip the standard helpers in §18 |
| `GOM_HOME` | Directory holding runtime state (default `~`) |
| `GOM_RECURSION_LIMIT` | Maximum interpreter recursion depth (default `10000`) |
| `GOM_ALLOW_LEGACY_PICKLE` | Set to `1` once to migrate a pre-1.2 pickle store to JSON |

---

## 17. Grammar Summary

This is a simplified description of GOM's grammar. The actual parser handles many edge cases described above.

```
program        := section*
section        := ("=====" name "=====")? statement*
statement      := stmt_body terminator?          // AEMI inserts a missing terminator
terminator     := "!" | "!!" | "!!!" | "?" | "¡"
stmt_body      := declaration | assignment | conditional | function_def
               |  class_decl | return_stmt | delete_stmt | reverse_stmt
               |  when_stmt | after_stmt | export_stmt | import_stmt
               |  expression

declaration    := ("const" | "var") name ("<" lifetime ">")? ("~" confidence "~")?
                  (":" type)? "=" expression
assignment     := name "=" expression
               |  name "[" expression "]" "=" expression
               |  name "." name "=" expression
               |  name ("+=" | "-=" | "*=" | "/=" | "^=") expression
               |  name ("++" | "--")
conditional    := "if" expression "{" statement* "}"
function_def   := ("function"|"fn"|"func"|"f") name "(" params? ")" "=>" "{" statement* "}"
class_decl     := "class" name "{" (declaration | function_def)* "}"
return_stmt    := "return" expression?
delete_stmt    := "delete" expression
reverse_stmt   := "reverse"
when_stmt      := "when" expression "{" statement* "}"
after_stmt     := "after" expression "{" statement* "}"
export_stmt    := "export" name "to" name
import_stmt    := "import" name "from" name
expression     := ... (see expression_tree.py for the full expression grammar)
map_literal    := "{" (name ":" expression ("," name ":" expression)*)? "}"
```

## 18. Standard Helpers (Prelude)

GOM has no loops, so list work is written as recursion — and the same five
recursive helpers get rewritten in every program. They are loaded into the base
namespace at startup, written in GOM itself, so they behave exactly like user
code and can be shadowed by any declaration.

| Helper | Result |
|--------|--------|
| `range(n)` | `[0, 1, ... n-1]` |
| `rangeFrom(start, count)` | `count` numbers starting at `start` |
| `map(list, fn)` | transform every element |
| `filter(list, fn)` | keep elements where `fn` is true |
| `reduce(list, fn, acc)` | fold left |
| `zip(a, b)` | pairs of elements |
| `take(list, n)` | first `n` elements |
| `reverseOf(list)` | reversed copy |
| `concat(a, b)` | `a + b` |
| `sortBy(list, fn)` | stable sort by a key function |
| `sum(list)`, `maxOf(list)`, `minOf(list)` | aggregates |

```
function double(n) => {
   return n * 2!
}!

const numbers = map(range(5), double)!
print numbers!        // → [0, 2, 4, 6, 8]
print sum(numbers)!   // → 20
```

Set `GOM_NO_PRELUDE=1` for a bare namespace.

---

---

*This reference describes Gulf of Mexico v1.2.0. For architectural details, see [ARCHITECTURE.md](ARCHITECTURE.md). For installation instructions, see [INSTALLATION.md](INSTALLATION.md).*
