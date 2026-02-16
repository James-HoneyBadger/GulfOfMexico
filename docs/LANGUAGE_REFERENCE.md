# Gulf of Mexico — Language Reference

Complete reference for the Gulf of Mexico programming language.

## Syntax Fundamentals

### Statement Terminators

Every statement ends with one or more `!` marks. The number of `!` marks indicates confidence level:

- `!` — normal confidence (always executes)
- `!!` — high confidence (always executes)
- `!!!` — absolute confidence (always executes)
- `?` — debug terminator (prints debug output)

```
print "normal"!
print "confident"!!
print "debug mode"?
```

### Comments

```
// Single-line comment

/* Block comment
   spanning multiple lines */
```

### Indentation

Indentation must use multiples of 3 spaces. Tabs are not supported.

```
if true {
   print "3 spaces"!     // OK
   if true {
      print "6 spaces"!  // OK
   }
}
```

### Significant Whitespace

Whitespace between tokens controls operator binding. Tighter binding (less whitespace) groups operations first:

```
2 * 1+3    // = 2 * (1+3) = 8    — tight binding on +
2*1 + 3    // = (2*1) + 3 = 5    — tight binding on *
2 * 1 + 3  // = (2*1) + 3 = 5    — equal spacing, left-to-right
```

This also affects function call parsing. Single-whitespace between a function name and argument is a function call:

```
greet "World"      // calls greet("World")
func n - 1         // calls func(n) then subtracts 1
func  n - 1        // calls func(n - 1) — double space = wider gap
```

## Data Types

### Numbers

Standard integers and floats:

```
const a = 42!
const b = 3.14!
const c = -7!
```

Numbers are indexable by digit (-1 based):

```
const n = 12345!
n[-1]   // 1 (first digit)
n[0]    // 2 (second digit)
n[3]    // 5 (last digit)
```

### Strings

Strings use double or single quotes interchangeably:

```
const a = "hello"!
const b = 'hello'!     // identical
```

#### Interpolation

Three currency symbols work as interpolation prefixes:

```
const x = 42!
"value: ${x}"       // Dollar
"value: £{x}"       // Pound
"value: ¥{x}"       // Yen
```

Expressions inside interpolation are evaluated:

```
"sum: ${2 + 3}"     // "sum: 5"
```

#### Escape Sequences

`\n` (newline), `\t` (tab), `\r` (carriage return), `\\` (backslash), `\"` (double quote), `\'` (single quote), `\0` (null), `\b` (backspace), `\f` (form feed), `\v` (vertical tab).

#### String Operations

```
const s = "hello"!
s.length            // 5
-"hello"            // "olleh" (unary minus reverses)
"abc" + "def"       // "abcdef"
```

### Booleans (Three-Valued)

GOM has three boolean values:

| Value | Meaning |
|-------|---------|
| `true` | Always true |
| `false` | Always false |
| `maybe` | Probabilistic — evaluates to true ~50% of the time |

Boolean conversion from numbers:

```
Boolean(0)    // false
Boolean(1)    // true
Boolean(0.3)  // maybe (any non-0 non-1 value)
```

Logical NOT uses the semicolon prefix:

```
;true    // false
;false   // true
;maybe   // maybe
```

### Lists

```
const arr = [1, 2, 3]!
```

#### -1 Based Indexing

All indexing in GOM starts at -1:

```
const arr = [10, 20, 30]!
arr[-1]    // 10 (first element)
arr[0]     // 20 (second element)
arr[1]     // 30 (third element)
```

Valid index range for a list of length N: `-1` to `N - 2`.

#### List Methods

```
var list = [1, 2, 3]!
list.push(4)          // append element
list.pop()            // remove and return last element
list.length           // number of elements
```

#### List Operations

```
[1, 2] + [3, 4]      // [1, 2, 3, 4] (concatenation)
-[1, 2, 3]            // [3, 2, 1] (reverse)
```

### Maps

```
const m = Map()!
m.set("key", "value")!
m.get("key")          // "value"
```

### Undefined

```
const nothing = undefined!
```

## Variables

### Declaration

```
const x = 42!          // immutable — cannot be reassigned
var y = 10!            // mutable — can be reassigned
```

### Type Annotations

Optional type annotations (checked at declaration time):

```
var x: Int = 42!
var s: String = "hello"!
```

### Variable Lifetimes

Variables can have a lifetime — they expire after N statements:

```
var temp <3> = "alive"!
print temp!              // OK — line 1
print temp!              // OK — line 2
print temp!              // OK — line 3
print temp!              // Error — temp has expired
```

### Previous Values

Access the prior value of a variable:

```
var x = 100!
x = 200!
print x!                 // 200
print previous x!        // 100
```

### Delete

Remove a variable from scope:

```
var x = 42!
delete x!                // x no longer exists
```

## Operators

### Arithmetic

| Operator | Meaning |
|----------|---------|
| `+` | Addition, string/list concatenation |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division (always float) |
| `^` | Exponentiation |
| Unary `-` | Negate number, reverse string/list |

### Comparison

| Operator | Meaning |
|----------|---------|
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater or equal |
| `<=` | Less or equal |

### Tiered Equality

Four levels of equality precision:

| Operator | Level | Behavior |
|----------|-------|----------|
| `=` | Approximate | Numbers within 10 are "equal" |
| `==` | Exact value | Standard value comparison |
| `===` | Type-strict | Same value and same type |
| `====` | Reference | Same object identity |

Corresponding inequality: `!=`, `!==`, `!===`.

```
10 = 11      // true  (within 10)
10 == 11     // false (not same value)
10 == 10     // true
10 === 10    // true  (same value, same type)
```

### Logical

| Operator | Meaning |
|----------|---------|
| `&&` | Logical AND |
| `\|\|` | Logical OR |
| `;` (prefix) | Logical NOT |

## Functions

### Definition

Functions use the `function` keyword (or `fn`, `func`, `f`) with `=>` and curly braces:

```
function add(a, b) => {
   return a + b!
}!

fn greet(name) => {
   print "Hello, ${name}!"!
}!
```

### Calling

```
// Parenthesized call (required for multi-arg)
add(3, 7)!

// Space syntax (single-arg only)
greet "World"!

// Both are equivalent for single-arg:
greet("World")!
greet "World"!
```

### Higher-Order Functions

Functions are first-class values:

```
function applyTwice(f, x) => {
   return f(f(x))!
}!

function double(n) => {
   return n * 2!
}!

applyTwice(double, 3)!   // 12
```

## Control Flow

### Conditionals

```
if condition {
   // body (3-space indent)
}
```

Else is not a keyword — use sequential if blocks with returns inside functions:

```
function describe(n) => {
   if n > 0 {
      return "positive"!
   }
   if n < 0 {
      return "negative"!
   }
   return "zero"!
}!
```

### Recursion

GOM has no loop constructs. Use recursion:

```
function factorial(n) => {
   if n <= 1 {
      return 1!
   }
   const sub = n - 1!
   return n * factorial(sub)!
}!
```

## Classes

One class = one instance. Each `new` call overwrites the previous instance.

```
class Dog {
   var name = "unnamed"!

   function bark() => {
      print "${name} says woof!"!
   }!
}!

const d = new Dog!
d.name = "Rex"!
d.bark()!             // "Rex says woof!"
```

## Word Numbers

English words for numbers are built-in:

### Literals (0–19)

`zero`, `one`, `two`, `three`, `four`, `five`, `six`, `seven`, `eight`, `nine`, `ten`, `eleven`, `twelve`, `thirteen`, `fourteen`, `fifteen`, `sixteen`, `seventeen`, `eighteen`, `nineteen`

### Functions (20+)

`twenty(n)`, `thirty(n)`, ..., `ninety(n)` — add n to the tens value:

```
twenty(1)     // 21
thirty(5)     // 35
```

`hundred(n)`, `thousand(n)`, `million(n)` — multiply:

```
hundred(5)     // 500
thousand(2)    // 2000
```

### Named Fractions

```
half       // 0.5
third      // 0.333...
quarter    // 0.25
```

## Reactive Features

### When Watchers

Execute a block when a condition becomes true:

```
var x = 0!
when x > 5 {
   print "x exceeded 5!"!
}
x = 10!    // triggers the when block
```

### Next Promises

Capture the next value a variable receives:

```
var x = 100!
const future = next x!
print future!          // undefined (not yet resolved)
x = 42!                // resolves the promise
print future!          // 42
```

### Signals (use)

Create a reactive signal with getter/setter:

```
const sig = use 0!     // initial value 0
sig 42!                // set to 42
print sig()!           // 42 (getter)
```

## Other Features

### Reverse

Replay all prior statements in the current scope in reverse order:

```
print "A"!
print "B"!
print "C"!
reverse!    // prints: C, B, A
```

### Noop

Do nothing:

```
noop!
```

### Import / Export

Split a file into sections with `=====` markers:

```
===== utils =====
const PI = 3.14159!
export PI to main!

===== main =====
import PI from utils!
print PI!
```

### Math Functions

| Function | Description |
|----------|-------------|
| `abs(x)` | Absolute value |
| `floor(x)` | Round down |
| `ceil(x)` | Round up |
| `round(x)` | Round to nearest |
| `sqrt(x)` | Square root |
| `sin(x)` | Sine (radians) |
| `cos(x)` | Cosine (radians) |
| `tan(x)` | Tangent (radians) |
| `log(x)` | Natural logarithm |
| `exp(x)` | e^x |
| `degrees(x)` | Radians to degrees |
| `radians(x)` | Degrees to radians |
| `pow(x, y)` | x raised to y |
| `min(x, y)` | Minimum of two values |
| `max(x, y)` | Maximum of two values |
| `random()` | Random float 0–1 |
| `randomInt(a, b)` | Random integer a–b |

### Type Conversions

```
String(42)       // "42"
Number("7")      // 7.0
Boolean(1)       // true
Boolean(0)       // false
Boolean(0.5)     // maybe
```

### I/O

```
print "output"!              // print to stdout
const input = read "prompt: "!  // read from stdin
write "file.txt", "content"!    // write to file
```

### Sleep

```
sleep 1000!    // pause for 1000 milliseconds
```
