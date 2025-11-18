# Gulf of Mexico — Programming Guide

Best practices, patterns, and practical guidance for writing effective code.

> Note (Nov 2025): Internal GOM test programs used for designing/debugging the language were removed. Use user-facing examples in `programs/examples/`, demos in `programs/demos/`, and Python unit tests in `tests/`.

## Table of Contents

1. [Philosophy and Mindset](#philosophy-and-mindset)
2. [Code Style](#code-style)
3. [Common Patterns](#common-patterns)
4. [Working with Arrays](#working-with-arrays)
5. [Class Design](#class-design)
6. [Reactive Programming Patterns](#reactive-programming-patterns)
7. [Error Prevention](#error-prevention)
8. [Performance Tips](#performance-tips)
9. [Testing Strategies](#testing-strategies)
10. [Debugging Techniques](#debugging-techniques)

## Philosophy and Mindset

### Embrace the Weird

Gulf of Mexico is intentionally unconventional. Don't fight it—lean into the chaos. Arrays starting at -1? That's not a bug, it's a *feature*. Probabilistic variables? Sounds like democracy to us.

### Think Declaratively

With reactive `when` statements and immutable-by-default variables, Gulf of Mexico encourages declarative thinking. Describe *what* you want, not always *how* to get it.

### Keep It Simple

With no loops, limited control flow, and no exceptions, complexity is harder to hide. This is good. Simple code is maintainable code, even when it's weird code.

## Code Style

### Naming Conventions

Choose clear, descriptive names:

```gom
// Good
const playerScore 100!
var currentLevel 1!

// Less good
const x 100!
var l 1!
```

Use `camelCase` or `snake_case` consistently:

```gom
const myVariable 42!
const my_variable 42!  // Pick one style and stick with it
```

### Indentation

**Use 3 spaces.** Not 2, not 4, not tabs. Three. The language insists.

```gom
if condition {
   print("correct")!
   if nested {
      print("still correct")!
   }
}
```

### Line Length

Keep lines under 80-100 characters when possible. Break long expressions:

```gom
const longCalculation 
   (value1 + value2) * multiplier ^ exponent!
```

### Comments

Comment the "why," not the "what":

```gom
// Good: Explains reasoning
// Use confidence level 3 to override default settings
var config "custom"!!!

// Less useful: States the obvious
// Set config to custom with 3 exclamation marks
var config "custom"!!!
```

### Spacing

Add spaces around operators for readability:

```gom
// Good
const sum a + b!
if x > 10 {

// Cramped
const sum a+b!
if x>10{
```

## Common Patterns

### Function Call Syntax

Gulf of Mexico uses hybrid call syntax:

**With arguments** - Space-separated (recommended) or parentheses:
```gom
const result add 5 3!         // Space-separated
const result add(5, 3)!       // Parentheses (also valid)
```

**Zero arguments** - Parentheses required:
```gom
const value getValue()!       // ✓ Correct
const value getValue!         // ✗ Wrong - references function, doesn't call it
```

**Method calls** - Same rules apply:
```gom
obj.method()!                 // Zero-arg - parentheses required
obj.method arg!               // One arg - space-separated
obj.process data config!      // Multi-arg - space-separated
```

**Why?** The parser needs parentheses to distinguish zero-arg calls from name references. Without them, `getValue!` means "the function getValue" not "call getValue".

### Counter Pattern

Since there are no loops, use recursive functions for repetition:

```gom
function countTo(n, current) => {
   if current <= n {
      print(current)!
      countTo(n, current + 1)!
   }
}!

countTo(10, 1)!
```

### Accumulator Pattern

```gom
function sumArray(arr, index, total) => {
   if index < 3 {  // Assuming 4 elements (indices -1 to 2)
      const newTotal total + arr[index]!
      return sumArray(arr, index + 1, newTotal)!
   }
   return total!
}!

const numbers [10, 20, 30, 40]!
const result sumArray(numbers, -1, 0)!
```

### Conditional Assignment

No ternary operator, so use explicit branches:

```gom
var message "default"!

if score > 100 {
   message = "High score!"!
}

if score <= 100 {
   message = "Keep trying"!
}
```

### Factory Pattern

Create objects with initial state:

```gom
function createPlayer(name, level) => {
   const p new Player()!
   p.name = name!
   p.level = level!
   p.health = 100!
   return p!
}!

const hero createPlayer("Alice", 1)!
```

## Working with Arrays

### Remember: Index -1 is First

Always start counting from -1:

```gom
const items ["first", "second", "third"]!

const first items[-1]!   // ✓ Correct
const first items[0]!    // ✗ This is the second element!
```

### Iterating with Recursion

```gom
function processArray(arr, index, length) => {
   if index < length {
      print(arr[index])!
      processArray(arr, index + 1, length)!
   }
}!

const data [1, 2, 3, 4]!
processArray(data, -1, 3)!  // Indices: -1, 0, 1, 2
```

### Building Arrays Dynamically

```gom
const var result []!

result[-1] = 10!   // First element
result[0] = 20!    // Second element
result[1] = 30!    // Third element
```

### Fractional Indexing for Insertion

Use fractional indices to insert elements in sorted order:

```gom
const var sorted [10, 30]!
sorted[0.5] = 20!
// Result: [10, 20, 30]
```

### Array Helper Functions

```gom
// Get array length (approximately)
function arrayLength(arr) => {
   var count 0!
   // You'll need to know the max index or count manually
   // Gulf of Mexico doesn't have a built-in length property
   return count!
}!

// Reverse an array (built-in)
const reversed reverse([1, 2, 3])!
```

## Class Design

### Keep Classes Focused

One responsibility per class:

```gom
// Good: Single purpose
class Timer {
   var seconds 0!
   
   function tick() => {
      seconds = seconds + 1!
   }!
   
   function reset() => {
      seconds = 0!
   }!
}!
```

### Initialize in Creation

Since constructors with parameters don't exist, initialize after creation:

```gom
function createTimer(initial) => {
   const t new Timer()!
   t.seconds = initial!
   return t!
}!
```

### Use Methods for Behavior

Encapsulate operations inside methods:

```gom
class BankAccount {
   var balance 0!
   
   function deposit(amount) => {
      balance = balance + amount!
   }!
   
   function withdraw(amount) => {
      if balance >= amount {
         balance = balance - amount!
         return true!
      }
      return false!
   }!
}!
```

### Composition Over Inheritance

Gulf of Mexico doesn't have inheritance. Use composition:

```gom
class Engine {
   var running false!
   function start() => { running = true! }!
}!

class Car {
   var engine null!
   
   function initialize() => {
      engine = new Engine()!
   }!
   
   function start() => {
      engine.start()!
   }!
}!
```

## Reactive Programming Patterns

### State Monitoring

Use `when` to react to state changes:

```gom
var playerHealth 100!

when playerHealth <= 0 {
   print("Game Over!")!
}

when playerHealth < 20 {
   print("Warning: Low health!")!
}
```

### Threshold Detection

```gom
var temperature 20!

when temperature > 30 {
   print("Too hot!")!
}

when temperature < 10 {
   print("Too cold!")!
}
```

### Avoiding Repeated Triggers

Use flags to prevent multiple triggers:

```gom
var count 0!
var alerted false!

when count > 10 {
   if ;alerted {
      print("Threshold exceeded!")!
      alerted = true!
   }
}
```

### Cascading Reactions

```gom
var input 0!
var processed 0!

when input > 0 {
   processed = input * 2!
}

when processed > 100 {
   print("Processed value is high!")!
}
```

## Error Prevention

### Always End Statements with !

The most common error. Double-check:

```gom
const x 42!  // ✓
print(x)!    // ✓
```

### Check Array Bounds Mentally

Since arrays start at -1:

```gom
const arr [10, 20, 30]!
// Valid indices: -1, 0, 1
// Invalid: 2, 3, -2
```

### Validate Before Operations

No exception handling, so validate first:

```gom
function safeDivide(a, b) => {
   if b == 0 {
      print("Cannot divide by zero!")!
      return 0!
   }
   return a / b!
}!
```

### Initialize Variables Properly

```gom
var count 0!        // ✓ Good
var count null!     // ✗ Might cause issues
```

### Use Const by Default

Prefer `const` unless you need mutability:

```gom
const pi 3.14159!    // Won't change
var counter 0!       // Will change
```

## Performance Tips

### Minimize Reactive Watchers

Each `when` statement adds overhead. Use sparingly:

```gom
// Avoid excessive watchers
when x > 10 { }
when x > 11 { }
when x > 12 { }

// Better: Consolidate logic
when x > 10 {
   if x > 12 {
      // Handle 12+
   }
   if x > 11 {
      // Handle 11+
   }
   // Handle 10+
}
```

### Avoid Deep Recursion

Recursion replaces loops, but deep recursion can be slow:

```gom
// Be cautious with large ranges
function countTo(n, current) => {
   if current <= n {
      print(current)!
      countTo(n, current + 1)!  // 1000+ iterations might be slow
   }
}!
```

### Cache Computed Values

```gom
// Inefficient: Recompute each time
function area(radius) => {
   return 3.14159 * radius * radius!
}!

// Better: Cache constant
const pi 3.14159!
function area(radius) => {
   return pi * radius * radius!
}!
```

### Use Fractional Indexing Wisely

Fractional insertion is convenient but slower than direct assignment:

```gom
// Slower for many insertions
arr[0.5] = value!

// Faster if you know the index
arr[1] = value!
```

## Testing Strategies

### Write Test Files

Create `.gom` files to test features:

```gom
// test_math.gom
function add(a, b) => a + b!

const result add(2, 3)!

if result == 5 {
   print("PASS: add function")!
}

if result !== 5 {
   print("FAIL: add function")!
}
```

### Test Each Feature Independently

```gom
// test_arrays.gom
const arr [10, 20, 30]!

if arr[-1] == 10 {
   print("PASS: First element")!
}

if arr[0] == 20 {
   print("PASS: Second element")!
}
```

### Use Print for Assertions

No testing framework, so rely on output:

```gom
const expected 42!
const actual myFunction()!

if actual == expected {
   print("✓ Test passed")!
}

if actual !== expected {
   print("✗ Test failed: expected ${expected}, got ${actual}")!
}
```

### Organize Examples by Category

User-facing programs are organized for learning and exploration:

```
programs/
├── 01_basics/      # Hello world, variables, arrays, functions, classes, conditionals
├── 02_features/    # Equality, three-valued logic, reactive, lifetimes, async, strings, arithmetic
├── 03_graphics/    # Canvas, transforms, generative art, mandelbrot
├── 04_satirical/   # Satirical/comedy features
├── 05_analysis/    # Statistics, finance, business, scientific
└── demos/          # Complete demo applications
```

Note: Internal GOM test programs were removed in Nov 2025. Use the examples/demos above or Python test suite in `tests/`.

## Debugging Techniques

### Use Debug Levels

Add `?` marks for debug output:

```gom
const x 42?           // Level 1: Basic info
const y [1, 2, 3]??   // Level 2: More detail
const z "test"???     // Level 3: Everything
```

Higher levels provide more verbose output.

### Print Intermediate Values

No debugger, so use strategic prints:

```gom
function calculate(x) => {
   const step1 x * 2!
   print("step1: ${step1}")!
   
   const step2 step1 + 10!
   print("step2: ${step2}")!
   
   return step2!
}!
```

### Isolate Problems

Simplify to the smallest failing case:

```gom
// Original: Complex and broken
const result complexFunction(data, options, flags)!

// Simplified: Test each part
const result1 step1(data)!
print("After step1: ${result1}")!

const result2 step2(result1, options)!
print("After step2: ${result2}")!
```

### Check Array Indices

Common mistake—verify index alignment:

```gom
const arr [10, 20, 30]!
print("Index -1: ${arr[-1]}")!  // Should be 10
print("Index 0: ${arr[0]}")!    // Should be 20
```

### Validate Input

Print function parameters:

```gom
function process(value) => {
   print("process called with: ${value}")!
   // ... rest of function
}!
```

### Use the REPL

Test snippets interactively:

```bash
python -m gulfofmexico
```

```gom
> const x 42!
> print(x)!
42
> const arr [1, 2, 3]!
> print(arr[-1])!
1
```

### Comment Out Code

Binary search for bugs:

```gom
// print("Debug 1")!
const a process1()!
// print("Debug 2")!
const b process2(a)!
// print("Debug 3")!
```

## Advanced Patterns

### State Machine

```gom
class StateMachine {
   var state "idle"!
   
   function transition(newState) => {
      print("Transitioning: ${state} -> ${newState}")!
      state = newState!
   }!
}!

const machine new StateMachine()!
machine.transition("running")!
machine.transition("stopped")!
```

### Observer Pattern (with When)

```gom
var subject 0!

// Multiple observers
when subject > 10 {
   print("Observer 1: value exceeded 10")!
}

when subject > 20 {
   print("Observer 2: value exceeded 20")!
}

subject = 15!  // Triggers observer 1
subject = 25!  // Triggers both
```

### Builder Pattern

```gom
class ConfigBuilder {
   var host "localhost"!
   var port 8080!
   var debug false!
   
   function setHost(h) => {
      host = h!
      return this!
   }!
   
   function setPort(p) => {
      port = p!
      return this!
   }!
}!

// Note: Method chaining doesn't work in current implementation
// Use step-by-step:
const config new ConfigBuilder()!
config.setHost("example.com")!
config.setPort(3000)!
```

### Memoization

Cache expensive computations:

```gom
const var cache Map()!

function expensiveCalc(n) => {
   // Check cache (conceptually)
   const result n * n!
   // Store in cache
   return result!
}!
```

## Multi-File Organization

### Separate Concerns

```gom
===== math_utils =====

function add(a, b) => a + b!
function multiply(a, b) => a * b!

export add to main!
export multiply to main!

===== string_utils =====

function uppercase(s) => {
   // Implementation
   return s!
}!

export uppercase to main!

===== main =====

import add!
import multiply!
import uppercase!

// Use imported functions
```

### Module Pattern

Each file section acts as a module:

```gom
===== database =====

var connection null!

function connect() => {
   connection = "connected"!
}!

function query(sql) => {
   // Execute query
   return "result"!
}!

export connect to main!
export query to main!

===== main =====

import connect!
import query!

connect()!
const result query("SELECT * FROM users")!
```

## Best Practices Summary

1. **Always end statements with `!`**
2. **Remember arrays start at -1**
3. **Use 3-space indentation**
4. **Prefer `const` over `var`**
5. **Comment the "why," not the "what"**
6. **Use recursion instead of loops**
7. **Validate inputs before operations**
8. **Test incrementally**
9. **Use debug levels (`?`) liberally**
10. **Embrace the weird**

## Final Thoughts

Gulf of Mexico is a language that challenges conventions and makes you think differently. Don't fight it—enjoy the journey into the absurd. Write clear code, test thoroughly, and remember: it's *perfect* by design.

## Learning Resources

Explore the organized example programs:

- **Start here**: `programs/01_basics/` - Core language features
- **Advanced**: `programs/02_features/` - Reactive, async, three-valued logic
- **Visual**: `programs/03_graphics/` - Canvas and generative art
- **Fun**: `programs/04_satirical/` - Emotional, quantum, time travel programming
- **Practical**: `programs/05_analysis/` - Statistics, finance, business analysis
- **Complete showcase**: `programs/demos/grand_deluxe_demo.gom`

See [programs/README.md](../../programs/README.md) for the complete catalog and syntax guidelines.

Happy coding! 🌊
