# Gulf of Mexico Programming Language - Example Programs

This directory contains a comprehensive collection of example and demo programs demonstrating all features of the Gulf of Mexico (GOM) programming language, organized by category and complexity level.

## 📚 Quick Index

### Category 01: Basics
- [01_hello_world.gom](#01-basics) - Getting started with print statements
- [02_variables.gom](#01-basics) - Variable and constant declarations
- [03_types.gom](#01-basics) - Data types and array operations

### Category 02: Operators
- [01_arithmetic.gom](#02-operators) - Arithmetic operations and precedence
- [02_comparison.gom](#02-operators) - Comparison and logical operators
- [03_strings.gom](#02-operators) - String operations and concatenation

### Category 03: Control Flow
- [01_if_else.gom](#03-control-flow) - Conditional statements
- [02_loops.gom](#03-control-flow) - Loop structures using recursion

### Category 04: Functions
- [01_function_basics.gom](#04-functions) - Basic function definition and calls
- [02_function_advanced.gom](#04-functions) - Advanced function patterns

### Category 05: Data Structures
- [01_arrays.gom](#05-data-structures) - Array operations and manipulation
- [02_strings.gom](#05-data-structures) - String manipulation

### Category 06: Object-Oriented Programming
- [01_classes_basics.gom](#06-oop) - Basic class definition
- [02_classes_advanced.gom](#06-oop) - Advanced class patterns

### Category 07: Special Features
- [01_three_valued_logic.gom](#07-special-features) - GOM's unique three-valued logic
- [02_probabilistic_variables.gom](#07-special-features) - Probabilistic variables

### Category 08: Mathematics
- [01_mathematical_functions.gom](#08-mathematics) - Math functions
- [02_algorithms.gom](#08-mathematics) - Common algorithms

### Category 09: Applications
- [01_todolist.gom](#09-applications) - Todo list application
- [02_calculator.gom](#09-applications) - Calculator application
- [03_guessing_game.gom](#09-applications) - Guessing game

---

## 01. BASICS

### 01_hello_world.gom
**Purpose**: The simplest GOM program - printing to the console.

**Key Features**:
- Print statements
- String literals

**Run**: `python -m gulfofmexico examples/01_basics_hello_world.gom`

---

### 02_variables.gom
**Purpose**: Declaring and using variables and constants.

**Key Features**:
- `const` declarations (immutable)
- `var` declarations (mutable)
- String interpolation with `${}`

**Example Output**:
```
Constants:
PI = 3.14159
NAME = Gulf of Mexico
VERSION = 1

Variables:
counter = 0
message = Welcome
temperature = 25.5

After modification:
counter = 10
```

**Key Concepts**:
- Constants cannot be reassigned
- Variables can be modified with new declarations
- String interpolation embeds expressions in strings

---

### 03_types.gom
**Purpose**: Understanding GOM's type system and array features.

**Key Features**:
- Integer and float numbers
- Strings
- Booleans (three-valued: true/false/maybe)
- Arrays
- Negative array indexing (-1 for last element)

**Special GOM Features**:
- Arrays support -1 based indexing (arr[-1] = last element)
- Three-valued logic: `true`, `false`, `maybe`

---

## 02. OPERATORS

### 01_arithmetic.gom
**Purpose**: Arithmetic operations with correct operator precedence.

**Operators**:
- Addition (`+`)
- Subtraction (`-`)
- Multiplication (`*`)
- Division (`/`)
- Power (`^`)
- Unary negation (`-`)

**Key Concepts**:
- Power has highest precedence
- Multiplication/Division before Addition/Subtraction
- Parentheses override precedence

---

### 02_comparison.gom
**Purpose**: Comparison and logical operators with three-valued logic.

**Operators**:
- Equality: `==`, `!=`
- Comparison: `<`, `>`, `<=`, `>=`
- Logical: `&&` (AND), `||` (OR), `!` (NOT)

**Special Feature - Three-Valued Logic**:
```
true && true = true
true && false = false
true && maybe = maybe
false && maybe = false
maybe && maybe = maybe
```

---

### 03_strings.gom
**Purpose**: String manipulation and concatenation.

**Operations**:
- String concatenation with `+`
- String interpolation with `${expression}`
- String properties (`.length`)
- Type conversion via concatenation

---

## 03. CONTROL FLOW

### 01_if_else.gom
**Purpose**: Conditional execution of code blocks.

**Features**:
- `if` statements
- Nested `if`
- Ternary operator: `condition ? trueValue : falseValue`

**Pattern**:
```gom
if condition {
   // execute if true
}

// Ternary
const result = condition ? "yes" : "no"!
```

---

### 02_loops.gom
**Purpose**: Iteration using recursive functions (GOM's loop mechanism).

**Patterns**:
- Recursive loops
- Array iteration
- Factorial and sum calculations

**Key Pattern**:
```gom
function recursiveFunction(n) => {
   if n <= 0 {
      return baseCase!
   }
   return recursiveCall(n - 1)!
}!
```

---

## 04. FUNCTIONS

### 01_function_basics.gom
**Purpose**: Function definition and invocation.

**Syntax**:
```gom
function functionName(param1, param2) => {
   // function body
   return value!
}!

const result = functionName(arg1, arg2)!
```

**Features**:
- Functions with no parameters
- Functions with parameters
- Return statements
- Function calls in expressions

---

### 02_function_advanced.gom
**Purpose**: Advanced function patterns and higher-order functions.

**Patterns**:
- Functions returning functions
- Higher-order functions (functions as parameters)
- Function composition
- Array transformation

**Example Pattern**:
```gom
function makeAdder(x) => {
   function adder(y) => {
      return x + y!
   }!
   return adder!
}!
```

---

## 05. DATA STRUCTURES

### 01_arrays.gom
**Purpose**: Array creation, access, and manipulation.

**Features**:
- Array literals: `[1, 2, 3]`
- Array indexing: `arr[0]`
- Negative indexing: `arr[-1]` (last element)
- Array methods: `.push()`, `.pop()`
- Array concatenation: `[1, 2] + [3, 4]`
- Nested arrays
- Array length: `.length`

**GOM Special Feature**:
- Negative indices work intuitively
- -1 = last element
- -2 = second to last, etc.

---

### 02_strings.gom
**Purpose**: String operations and manipulation.

**Features**:
- String concatenation
- String interpolation
- String length property
- Character access via indexing
- String comparison
- Dynamic string building

---

## 06. OBJECT-ORIENTED PROGRAMMING

### 01_classes_basics.gom
**Purpose**: Defining and using classes and objects.

**Syntax**:
```gom
class ClassName {
   var property1 = defaultValue!
   var property2 = defaultValue!

   function methodName() => {
      // implementation
   }!
}!

const obj = new ClassName!
obj.property1 = value!
obj.methodName()!
```

**Features**:
- Class definition
- Properties with default values
- Methods with `this` implicitly bound
- Object instantiation with `new`
- Property and method access with dot notation

---

### 02_classes_advanced.gom
**Purpose**: Complex class patterns and real-world examples.

**Examples**:
- Bank account system
- Student grade tracking
- Game state management

**Patterns**:
- Encapsulation of state
- Methods that modify object state
- Return values from methods

---

## 07. SPECIAL FEATURES

### 01_three_valued_logic.gom
**Purpose**: Explore GOM's unique three-valued logic system.

**Boolean Values**:
- `true` - definitely true
- `false` - definitely false
- `maybe` - uncertain/unknown

**Truth Table Examples**:
```
true AND true = true
true AND maybe = maybe
false AND anything = false
true OR anything = true
false OR maybe = maybe
```

**Use Cases**:
- Representing uncertain information
- Probabilistic decision making
- Handling missing or incomplete data

---

### 02_probabilistic_variables.gom
**Purpose**: Using floating-point values as confidence scores.

**Patterns**:
- Probability scores (0.0 to 1.0)
- Combining probabilities
- Decision making based on confidence

**Example**:
```gom
const confidence = 0.75!
const decision = confidence > 0.5 ? true : false!
```

---

## 08. MATHEMATICS

### 01_mathematical_functions.gom
**Purpose**: Implementing mathematical functions in GOM.

**Functions**:
- Absolute value
- Power/exponentiation
- Greatest Common Divisor (GCD)
- Min/max
- Average

**Recursive Implementation**:
All mathematical functions use recursion since GOM doesn't have traditional loops.

---

### 02_algorithms.gom
**Purpose**: Implementing classic algorithms.

**Algorithms**:
- Linear search
- Counting occurrences
- Array reversal
- Sorting verification
- Finding maximum

**Key Pattern**:
```gom
function recursiveAlgorithm(arr, idx) => {
   if idx >= arr.length {
      return baseResult!
   }
   // process arr[idx]
   return combine(processElement, recursiveAlgorithm(arr, idx + 1))!
}!
```

---

## 09. APPLICATIONS

### 01_todolist.gom
**Purpose**: A practical todo list management system.

**Features**:
- TodoItem class with task, completion status, priority
- Mark tasks complete
- Display task status
- Count completed tasks

**Demonstrates**:
- Class design
- Object collections
- Recursive array processing

---

### 02_calculator.gom
**Purpose**: A simple calculator application.

**Operations**:
- Add, subtract, multiply, divide
- Clear state
- Display result

**Demonstrates**:
- State management in classes
- Method chaining patterns
- Input validation

---

### 03_guessing_game.gom
**Purpose**: An interactive number guessing game.

**Features**:
- Secret number
- Attempt counter
- Game state management
- Feedback on guesses

**Demonstrates**:
- Game loop simulation with recursion
- State mutation
- Win condition checking

---

## 🎯 Learning Path

### Beginner
1. Start with **01_hello_world.gom**
2. Learn about **02_variables.gom**
3. Explore **03_types.gom**
4. Practice with **02_operators_arithmetic.gom**

### Intermediate
5. **03_control_if_else.gom** - Conditionals
6. **04_functions_basics.gom** - Function definition
7. **05_data_arrays.gom** - Working with data
8. **06_oop_classes.gom** - Objects and classes

### Advanced
9. **04_functions_advanced.gom** - Advanced patterns
10. **07_special_three_valued.gom** - Unique GOM features
11. **08_math_algorithms.gom** - Complex algorithms
12. **09_demo_*.gom** - Real applications

---

## 🚀 Running Examples

### Run a single example:
```bash
python -m gulfofmexico examples/01_basics_hello_world.gom
```

### Run all examples:
```bash
for file in examples/*.gom; do
    echo "=== Running $file ==="
    python -m gulfofmexico "$file"
    echo ""
done
```

### Run in interactive REPL:
```bash
python -m gulfofmexico
# Type commands interactively
```

### Use the IDE:
```bash
python -m gulfofmexico.ide
# Open http://localhost:5000
```

---

## 📝 Key Language Concepts

### Variables and Scoping
- `const` creates immutable bindings
- `var` creates mutable bindings with shadowing
- Variables are function-scoped
- Nested functions capture outer scope

### Functions
- Arrow syntax: `function name(params) => { body }!`
- All functions are first-class values
- Recursion is the primary iteration mechanism
- Functions can return functions

### Classes
- Properties initialized in class body
- Methods can access and modify object state
- Objects created with `new ClassName`
- No inheritance (currently)

### Arrays
- Zero-indexed: `arr[0]` first element
- Negative indexing: `arr[-1]` last element
- Methods: `.push()`, `.pop()`, `.length`
- Concatenation with `+`

### Three-Valued Logic
- Unique to GOM
- `true`, `false`, `maybe` values
- Enables uncertain reasoning
- Special AND/OR semantics

---

## 💡 Common Patterns

### Recursive Array Processing
```gom
function processArray(arr, idx) => {
   if idx >= arr.length {
      return result!
   }
   // process arr[idx]
   return processArray(arr, idx + 1)!
}!
```

### Object-Oriented State
```gom
class Container {
   var state = initialValue!
   
   function mutate(value) => {
      var state = state + value!
   }!
   
   function getState() => {
      return state!
   }!
}!
```

### Conditional Logic
```gom
if condition1 {
   result = value1!
}

if condition2 {
   result = value2!
}

// Or ternary
const result = condition ? trueValue : falseValue!
```

---

## 📖 Additional Resources

- [Language Documentation](../DOCUMENTATION.md)
- [User Guide](../docs/guides/USER_GUIDE.md)
- [Language Features](../docs/language/)
- [IDE Usage](../docs/guides/IDE_GUIDE.md)

---

## ✅ Feature Checklist

All major GOM features are covered by these examples:

- [x] Variables and constants
- [x] All data types
- [x] Arithmetic operators
- [x] Comparison operators
- [x] Logical operators (including 3-valued)
- [x] String operations
- [x] Array operations
- [x] Function definition and calls
- [x] Recursion
- [x] Classes and objects
- [x] Control flow (if/else)
- [x] String interpolation
- [x] Ternary operators
- [x] Probabilistic values
- [x] Mathematical algorithms
- [x] Practical applications

---

**Last Updated**: December 27, 2025
**Language Version**: Gulf of Mexico Interpreter (Phase 5)
