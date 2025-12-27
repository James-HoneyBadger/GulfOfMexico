#!/bin/bash
# Gulf of Mexico Examples Runner
# Runs all example programs with nice formatting

EXAMPLES_DIR="examples"
PYTHON_CMD="/home/james/GulfOfMexico/.venv/bin/python"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    GULF OF MEXICO PROGRAMMING LANGUAGE - EXAMPLE PROGRAMS    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Function to run a single example
run_example() {
    local file=$1
    local category=$2
    local name=$3
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  [$category] $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    $PYTHON_CMD -m gulfofmexico "$file" 2>&1 | grep -v "DB_PRINT"
    echo ""
}

# Category 01: Basics
echo "📚 CATEGORY 01: BASICS"
echo ""
run_example "$EXAMPLES_DIR/01_basics_hello_world.gom" "01" "Hello World"
run_example "$EXAMPLES_DIR/01_basics_variables.gom" "01" "Variables & Constants"
run_example "$EXAMPLES_DIR/01_basics_types.gom" "01" "Data Types"

# Category 02: Operators
echo "🔢 CATEGORY 02: OPERATORS"
echo ""
run_example "$EXAMPLES_DIR/02_operators_arithmetic.gom" "02" "Arithmetic"
run_example "$EXAMPLES_DIR/02_operators_comparison.gom" "02" "Comparison & Logic"
run_example "$EXAMPLES_DIR/02_operators_strings.gom" "02" "String Operations"

# Category 03: Control Flow
echo "🔀 CATEGORY 03: CONTROL FLOW"
echo ""
run_example "$EXAMPLES_DIR/03_control_if_else.gom" "03" "If/Else Statements"
run_example "$EXAMPLES_DIR/03_control_loops.gom" "03" "Loops & Recursion"

# Category 04: Functions
echo "⚙️  CATEGORY 04: FUNCTIONS"
echo ""
run_example "$EXAMPLES_DIR/04_functions_basics.gom" "04" "Function Basics"
run_example "$EXAMPLES_DIR/04_functions_advanced.gom" "04" "Advanced Patterns"

# Category 05: Data Structures
echo "📦 CATEGORY 05: DATA STRUCTURES"
echo ""
run_example "$EXAMPLES_DIR/05_data_arrays.gom" "05" "Arrays"
run_example "$EXAMPLES_DIR/05_data_strings.gom" "05" "Strings"

# Category 06: OOP
echo "🏗️  CATEGORY 06: OBJECT-ORIENTED PROGRAMMING"
echo ""
run_example "$EXAMPLES_DIR/06_oop_classes.gom" "06" "Classes Basics"
run_example "$EXAMPLES_DIR/06_oop_advanced.gom" "06" "Advanced Classes"

# Category 07: Special Features
echo "✨ CATEGORY 07: SPECIAL FEATURES"
echo ""
run_example "$EXAMPLES_DIR/07_special_three_valued.gom" "07" "Three-Valued Logic"
run_example "$EXAMPLES_DIR/07_special_probabilistic.gom" "07" "Probabilistic Values"

# Category 08: Mathematics
echo "📐 CATEGORY 08: MATHEMATICS & ALGORITHMS"
echo ""
run_example "$EXAMPLES_DIR/08_math_functions.gom" "08" "Math Functions"
run_example "$EXAMPLES_DIR/08_math_algorithms.gom" "08" "Algorithms"

# Category 09: Applications
echo "💻 CATEGORY 09: APPLICATIONS"
echo ""
run_example "$EXAMPLES_DIR/09_demo_calculator.gom" "09" "Calculator"
run_example "$EXAMPLES_DIR/09_demo_guessing_game.gom" "09" "Guessing Game"
run_example "$EXAMPLES_DIR/09_demo_todolist.gom" "09" "Todo List"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                     ALL EXAMPLES COMPLETE                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
