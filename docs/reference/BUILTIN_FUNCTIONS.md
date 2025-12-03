# Gulf of Mexico — Built-in Functions Reference

Quick reference for all built-in functions: type conversions, math, statistics, financial, business, and scientific functions.

## Type Conversions
```javascript
Number("42.5")      // → 42.5
String(123)         // → "123"
Boolean(1)          // → true
Map()               // → {}
```

## Math Functions
```javascript
sin(1.5708)         // → 1.0 (π/2)
cos(0)              // → 1.0
tan(0.785)          // → 1.0 (π/4)
sqrt(144)           // → 12.0
abs(-42)            // → 42.0
floor(3.7)          // → 3.0
ceil(3.2)           // → 4.0
round(3.5)          // → 4.0
log(2.718)          // → 1.0 (natural log)
log10(100)          // → 2.0
exp(1)              // → 2.718 (e)
pow(2, 8)           // → 256.0
```

## Statistical Functions
```javascript
const data = [10, 20, 30, 40, 50]!

mean(data)          // → 30.0
median(data)        // → 30.0
stdev(data)         // → 15.811388
variance(data)      // → 250.0
min_val(data)       // → 10.0
max_val(data)       // → 50.0
sum_list(data)      // → 150.0
```

## Financial Functions
```javascript
// Compound Interest
compound_interest(1000, 0.05, 10, 12)
// principal=1000, rate=5%, time=10 years, compounded monthly
// → 1647.01

// Simple Interest
simple_interest(1000, 0.05, 10)
// principal=1000, rate=5%, time=10 years
// → 1500.0

// Payment Calculation
pmt(0.05, 12, 1000)
// rate=5%, periods=12, present_value=1000
// → 112.83
```

## Business Functions
```javascript
// Return on Investment
roi(1500, 1000)
// gain=1500, cost=1000
// → 50.0% ROI

// Profit Margin
profit_margin(1500, 1000)
// revenue=1500, cost=1000
// → 33.33% margin

// Compound Annual Growth Rate
cagr(1000, 2000, 5)
// begin=1000, end=2000, years=5
// → 14.87% annual growth
```

## Scientific Functions
```javascript
// Linear Regression
const x = [1, 2, 3, 4, 5]!
const y = [2, 4, 6, 8, 10]!
linear_regression(x, y)
// → [2.0, 0.0]  (slope, intercept)
// y = 2.0x + 0.0

// Quadratic Solver
quadratic_solve(1, -5, 6)
// Solve: x² - 5x + 6 = 0
// → [3.0, 2.0]  (roots)
```

## Array Operations
```javascript
const arr = [1, 2, 3, 4, 5]!
arr[0]              // → 1 (first element)
arr[-1]             // → 5 (last element)
arr[-2]             // → 4 (second from last)
```

## Map Operations
```javascript
const m = Map()!    // Create empty map
// Map access via string keys (future feature)
```

## Satirical Keywords
```javascript
happy {
    print("Happy code!")!
}

blockchain {
    print("Decentralized!")!
}

ai_powered {
    print("Machine learning!")!
}

sprint {
    print("Agile!")!
}

synergize {
    print("Corporate synergy!")!
}

lucky {
    print("Fingers crossed!")!
}
```

## Operators
```javascript
x == y              // Equal
x === y             // Triple equal (strict)
x ==== y            // Quad equal (very strict)
x ~= y              // Approximately equal (±0.01)
x != y              // Not equal
x < y               // Less than
x > y               // Greater than
x <= y              // Less or equal
x >= y              // Greater or equal
x && y              // Logical AND
x || y              // Logical OR
!x                  // Logical NOT
```

## Complete Example
```javascript
// Analyze sales data
const sales = [1200, 1500, 1800, 1600, 2000]!

print("Sales Analysis")!
print("Mean: ")!
print(mean(sales))!              // → 1620.0

print("Median: ")!
print(median(sales))!            // → 1600.0

print("Std Dev: ")!
print(stdev(sales))!             // → 286.18

blockchain {
    print("Data stored on blockchain!")!
}

// Financial projection
const investment = 10000!
const rate = 0.08!
const years = 5!

print("Investment Growth:")!
print(compound_interest(investment, rate, years, 12))!
// → 14898.46

// Business metrics
print("ROI: ")!
print(roi(14898, 10000))!
print("%")!                      // → 48.98%

ai_powered {
    // Predictive model
    const x_data = [1, 2, 3, 4, 5]!
    const y_data = [1200, 1500, 1800, 1600, 2000]!

    const model = linear_regression(x_data, y_data)!
    print("Sales trend model: ")!
    print(model)!                // → [slope, intercept]
}

print("Analysis complete!")!
```

---

## Notes

- All numeric functions return `GomValue` (double internally)
- Arrays are 0-indexed with -1 support for last element
- Statistical functions work on arrays of numbers
- Financial functions use decimal rates (0.05 = 5%)
- Linear regression returns `[slope, intercept]`
- Quadratic solver returns `[root1, root2]`
- All satirical keywords execute their blocks normally

## Compilation

```bash
./gomcc program.gom -o program.cpp
g++ -std=c++17 program.cpp -o program
./program
```

---

**Gulf of Mexico - Programming with personality!** 🌊
