#!/bin/bash
# Organize and validate all GulfOfMexico programs

set -e

echo "=== Gulf of Mexico Programs: Organization & Validation ==="
echo ""

# Create new directory structure
echo "Creating organized directory structure..."
mkdir -p programs/01_basics
mkdir -p programs/02_features
mkdir -p programs/03_graphics
mkdir -p programs/04_satirical
mkdir -p programs/05_analysis
mkdir -p programs/06_compiler_tests

# Move files to organized structure
echo "Moving example files to organized folders..."

# Basics (01-07)
mv programs/examples/01_hello_world.gom programs/01_basics/ 2>/dev/null || true
mv programs/examples/02_variables.gom programs/01_basics/ 2>/dev/null || true
mv programs/examples/03_arrays.gom programs/01_basics/ 2>/dev/null || true
mv programs/examples/04_probabilistic.gom programs/01_basics/ 2>/dev/null || true
mv programs/examples/05_functions.gom programs/01_basics/ 2>/dev/null || true
mv programs/examples/06_classes.gom programs/01_basics/ 2>/dev/null || true
mv programs/examples/07_conditionals.gom programs/01_basics/ 2>/dev/null || true

# Features (08-15)
mv programs/examples/08_equality.gom programs/02_features/ 2>/dev/null || true
mv programs/examples/09_three_valued_logic.gom programs/02_features/ 2>/dev/null || true
mv programs/examples/10_reactive.gom programs/02_features/ 2>/dev/null || true
mv programs/examples/11_lifetimes.gom programs/02_features/ 2>/dev/null || true
mv programs/examples/12_async.gom programs/02_features/ 2>/dev/null || true
mv programs/examples/13_string_interpolation.gom programs/02_features/ 2>/dev/null || true
mv programs/examples/14_arithmetic.gom programs/02_features/ 2>/dev/null || true
mv programs/examples/15_word_numbers.gom programs/02_features/ 2>/dev/null || true

# Graphics (16-19)
mv programs/examples/16_graphics.gom programs/03_graphics/ 2>/dev/null || true
mv programs/examples/17_graphics_transforms.gom programs/03_graphics/ 2>/dev/null || true
mv programs/examples/18_generative_art.gom programs/03_graphics/ 2>/dev/null || true
mv programs/examples/19_mandelbrot.gom programs/03_graphics/ 2>/dev/null || true
mv programs/examples/mandelbrot_simple.gom programs/03_graphics/ 2>/dev/null || true

# Satirical (20-35)
mv programs/examples/20_procrastination.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/21_corporate_speak.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/22_satirical_showcase.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/23_emotional_programming.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/24_superstitious_programming.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/25_ultimate_satire.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/26_quantum_programming.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/27_time_travel.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/28_quantum_time_spectacular.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/29_gaslighting_variables.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/30_blockchain_satire.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/31_ai_buzzwords.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/32_agile_scrum.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/33_security_theater.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/34_devops_cargo_cult.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/35_startup_culture.gom programs/04_satirical/ 2>/dev/null || true
mv programs/examples/19_passive_aggressive_errors.gom programs/04_satirical/ 2>/dev/null || true

# Analysis (36-42)
mv programs/examples/36_base_numbers.gom programs/05_analysis/ 2>/dev/null || true
mv programs/examples/37_base_simple.gom programs/05_analysis/ 2>/dev/null || true
mv programs/examples/38_base_practical.gom programs/05_analysis/ 2>/dev/null || true
mv programs/examples/39_statistics.gom programs/05_analysis/ 2>/dev/null || true
mv programs/examples/40_financial.gom programs/05_analysis/ 2>/dev/null || true
mv programs/examples/41_business.gom programs/05_analysis/ 2>/dev/null || true
mv programs/examples/42_scientific.gom programs/05_analysis/ 2>/dev/null || true

# Keep showcase in examples
mv programs/examples/00_complete_showcase.gom programs/examples/ 2>/dev/null || true

# Compiler examples
cp compiler/examples/*.gom programs/06_compiler_tests/ 2>/dev/null || true

echo ""
echo "=== Directory Structure Created ==="
echo "programs/"
echo "  01_basics/          - Hello World, Variables, Functions, etc."
echo "  02_features/        - Advanced features (async, reactive, etc.)"
echo "  03_graphics/        - Canvas and graphics programs"
echo "  04_satirical/       - Comedy/satirical language features"
echo "  05_analysis/        - Math, stats, finance, science"
echo "  06_compiler_tests/  - C++ compiler test programs"
echo "  demos/              - Complete demo applications"
echo "  tests/              - Unit test programs"
echo ""

# Validate syntax of key programs
echo "=== Validating Program Syntax ==="
echo ""

validate_program() {
   local file="$1"
   if [ -f "$file" ]; then
      echo -n "Checking $file... "
      if timeout 3 python3 -m gulfofmexico "$file" >/dev/null 2>&1; then
         echo "✓ OK"
         return 0
      else
         echo "✗ FAILED"
         return 1
      fi
   fi
}

# Check a few key programs from each category
validate_program "programs/01_basics/01_hello_world.gom"
validate_program "programs/01_basics/05_functions.gom"
validate_program "programs/02_features/12_async.gom"
validate_program "programs/demos/grand_deluxe_demo.gom"

echo ""
echo "=== Organization Complete ==="
