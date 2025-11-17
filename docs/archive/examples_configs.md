# Example: Using Custom Language Configurations

This directory demonstrates how to use custom language configurations with Gulf of Mexico programs.

## Example 1: Python-Like Syntax

**Configuration:** `demo_basic.json`
**Features:**
- `def` instead of `function`
- `output` instead of `print`
- 0-based array indexing

**Code:** `example_pythonic.gom`
```gom
// Using Python-like syntax via demo_basic.json config
// Run with: python -m gulfofmexico --config demo_basic.json example_pythonic.gom

def greet(name) {
    output("Hello, ${name}!")!
}

greet("World")!

// Note: Arrays start at 0 in this config
numbers = List(10, 20, 30, 40, 50)!
output(numbers[0])!  // Prints: 10
output(numbers[4])!  // Prints: 50
