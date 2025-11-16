# Gulf of Mexico User Guide

Welcome to the Gulf of Mexico, the *perfect* programming language! If you've ever thought "arrays should start at -1" or "I wish my variables could argue about their values," then congratulations—you've found your spiritual home.

## Table of Contents

1. [What is Gulf of Mexico?](#what-is-gulf-of-mexico)
2. [Your First Program](#your-first-program)
3. [Understanding the Basics](#understanding-the-basics)
4. [Working with Data](#working-with-data)
5. [Functions and Classes](#functions-and-classes)
6. [Advanced Features](#advanced-features)
7. [Common Pitfalls](#common-pitfalls)

## What is Gulf of Mexico?

Gulf of Mexico is a programming language that dares to ask: "What if we did everything *slightly wrong*?" It's a beautiful experiment in creative syntax, probabilistic computing, and the fine art of making programmers question their life choices.

Based on the conceptual design by [Lu Wilson (TodePond)](https://github.com/TodePond/GulfOfMexico), this implementation brings the chaos to life in Python.

### Philosophy

- **Arrays start at -1** because zero is overrated
- **Variables have confidence levels** because uncertainty is honest
- **Three-valued logic** because sometimes "maybe" is the only right answer
- **Time-limited variables** because permanence is an illusion
- **Reactive programming** because your code should care about changes

## Your First Program

Let's start with the traditional greeting:

```gom
print("Hello, Gulf of Mexico!")!
```

Notice the exclamation mark at the end? That's not excitement (though you should be excited)—it's how we end statements in Gulf of Mexico. Every statement needs its own little exclamation of existence!

### Running Your Program

Save your code as `hello.gom` and run:

```bash
python -m gulfofmexico hello.gom
```

Or try the interactive REPL:

```bash
python -m gulfofmexico
```

## Using the REPL

The REPL lets you experiment interactively and run files with import/export sections.

- Start the REPL:

```bash
python3 -m gulfofmexico.repl
```

- Try a few statements:

```gom
print "Hello from REPL"!
const x = 7!
print "x =", x!

function add(a, b) => {
   return a + b!
}!

const r = add 2, 3!
print "sum =", r!
```

- Load and run a file (also supports multi-file sections using `===== section =====`):

```text
:load programs/examples/01_hello_world.gom
```

- Handy commands (type `:help` inside REPL for the full list):

```text
:vars                # show current variables
:history [n]         # list or show a history block
:run [n|last]        # re-run a history block
:reset               # clear state
:load <file>         # load a .gom file (handles ===== sections)
:quit                # exit REPL
```

## Understanding the Basics

### Statements End with !

Every statement in Gulf of Mexico ends with an exclamation mark. It's like every line of code is shouting "I exist!"

```gom
const x 42!
print(x)!
```

### Variables: Three Flavors of Declaration

**Immutable Constants** - They never change, just like your ex's opinion of you:

```gom
const pi 3.14159!
const answer 42!
```

**Mutable Variables** - Change as often as you like:

```gom
var count 0!
count = 10!
count = 20!
```

**Const Var** - The reference is immutable, but the content can change. It's complicated:

```gom
const var list [1, 2, 3]!
list[-1] = 100!  // This works!
list = [4, 5, 6]!  // This doesn't!
```

### Comments

Use `//` for single-line comments:

```gom
// This is a comment
const x 42!  // So is this
```

## Working with Data

### Arrays: Starting at -1

In Gulf of Mexico, arrays start at index -1. Why? Because we can.

```gom
const numbers [10, 20, 30, 40]!

print(numbers[-1])!  // 10 (first element)
print(numbers[0])!   // 20 (second element)
print(numbers[1])!   // 30 (third element)
print(numbers[2])!   // 40 (fourth element)
```

Think of it as a gentle reminder that you're not in Kansas anymore.

### Fractional Indexing

Want to insert an element between two others? Use fractional indices!

```gom
const colors ["red", "blue"]!
colors[0.5] = "purple"!
// Now: ["red", "purple", "blue"]
```

It's like magic, but with more math.

### Strings

Strings work pretty much like you'd expect, with one delightful addition—interpolation!

```gom
const name "Alice"!
const age 25!
print("Hello, ${name}! You are ${age} years old.")!
```

You can use single quotes too:

```gom
const message 'This works!'!
```

### Numbers

Numbers are numbers. Revolutionary, we know.

```gom
const integer 42!
const floating 3.14!
const negative -10!
```

But wait! You can also use *word numbers*:

```gom
const myZero zero!
const myFive five!
const myTen ten!
const myTwenty twenty()!
const myFortyTwo forty() + two!
```

Because sometimes spelling it out feels right.

## Functions and Classes

### Defining Functions

Two syntaxes, same delicious functionality:

```gom
// Standard form
function add(a, b) => {
   return a + b!
}!

// Short form
fn multiply(x, y) => x * y!
```

Call them like normal:

```gom
const sum add(5, 3)!
const product multiply(4, 7)!
```

### Classes

Object-oriented programming, Gulf of Mexico style:

```gom
class Person {
   var name "Unknown"!
   var age 0!
   
   function greet() => {
      print("Hi, I'm ${name}!")!
   }!
   
   function birthday() => {
      age = age + 1!
   }!
}!

const alice new Person()!
alice.name = "Alice"!
alice.age = 25!
alice.greet()!
```

## Advanced Features

### Probabilistic Variables

Variables can have *confidence levels*. More exclamation marks = higher confidence = wins the debate:

```gom
var value 10!      // Confidence: 1
var value 20!!     // Confidence: 2 (overwrites 10)
var value 5!!!     // Confidence: 3 (overwrites 20)
```

It's democracy, but for data.

### Three-Valued Logic

Because the world isn't black and white:

```gom
const yes true!
const no false!
const uncertain maybe!

print(yes & no)!        // false
print(yes | maybe)!     // true (probably)
print(;maybe)!          // still maybe
```

The `;` operator is "not" (because `!` was taken by statements).

### Equality: Four Levels of Picky

```gom
const a 42!
const b 42.0!

a = b      // Approximate equality (very chill)
a == b     // Standard equality (normal)
a === b    // Strict equality (getting serious)
a ==== b   // Strictest equality (trust issues)
```

Each level gets progressively more paranoid about what "equal" means.

### Reactive Programming

Code that reacts to changes, like a good friend:

```gom
var temperature 20!

when temperature > 30 {
   print("It's hot!")!
}

temperature = 35!  // Triggers the when block
```

### Variable Lifetimes

**Line-based expiration:**

```gom
const temporary 100 = "I'll expire in 100 lines"!
```

**Time-based expiration:**

```gom
const brieflyHere <5.0> = "Gone in 5 seconds"!
```

All things must pass, including your variables.

### Async Functions

For when you need to pretend you're doing concurrent programming:

```gom
async function fetchData() => {
   return 42!
}!

const result await(fetchData())!
```

## Common Pitfalls

### Forgetting the Exclamation Mark

```gom
const x 42  // ❌ This won't work
const x 42! // ✓ Much better!
```

Every statement needs its moment to shine.

### Array Index Confusion

Remember, arrays start at -1:

```gom
const list [10, 20, 30]!
list[0]   // This is 20, not 10!
list[-1]  // This is 10, the first element
```

### Const vs Var vs Const Var

- `const` = "Never change"
- `var` = "Change whenever"
- `const var` = "You can change my content but not what I point to"

When in doubt, just use `var` and live dangerously.

### Overconfident Variables

```gom
var answer 42!
var answer 41!!!!!  // This wins with 5 exclamation marks
```

More exclamation marks = more confident. Choose wisely.

## Next Steps

Now that you understand the basics, check out:

- **[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** - Get everything set up
- **[TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)** - Deep dive into the details
- **[PROGRAMMING_GUIDE.md](PROGRAMMING_GUIDE.md)** - Best practices and patterns
- **programs/** - Example programs to explore

Welcome to the Gulf! The water's weird, but you'll get used to it.
