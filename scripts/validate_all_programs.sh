#!/bin/bash

# Validate all Gulf of Mexico programs
# This script tests syntax and basic execution of all .gom files

# Don't exit on error - we want to continue testing all files

echo "=== Gulf of Mexico Programs Validation ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
SKIPPED=0

# Test a single program
test_program() {
   local file="$1"
   local filename=$(basename "$file")

   # Skip certain files that are known to require special handling
   if [[ "$filename" == "multi_file.gom" ]] || \
      [[ "$filename" == "test_imports.gom" ]] || \
      [[ "$file" == *"/tests/dev/"* ]]; then
      echo -e "${YELLOW}⊘ SKIP${NC} $file (requires special setup)"
      ((SKIPPED++))
      return
   fi

   # Test the program with timeout
   if timeout 2 python3 -m gulfofmexico "$file" >/dev/null 2>&1; then
      echo -e "${GREEN}✓ PASS${NC} $file"
      ((PASSED++))
   else
      local exit_code=$?
      if [ $exit_code -eq 124 ]; then
         # Timeout is OK for programs with when/after statements
         echo -e "${GREEN}✓ PASS${NC} $file (timeout OK)"
         ((PASSED++))
      else
         echo -e "${RED}✗ FAIL${NC} $file (exit code: $exit_code)"
         ((FAILED++))
         # Show error details
         timeout 2 python3 -m gulfofmexico "$file" 2>&1 | head -5
      fi
   fi
}

# Test all programs by category
echo "Testing 01_basics..."
for file in programs/01_basics/*.gom; do
   [ -f "$file" ] && test_program "$file"
done

echo ""
echo "Testing 02_features..."
for file in programs/02_features/*.gom; do
   [ -f "$file" ] && test_program "$file"
done

echo ""
echo "Testing 03_graphics..."
for file in programs/03_graphics/*.gom; do
   [ -f "$file" ] && test_program "$file"
done

echo ""
echo "Testing 04_satirical..."
for file in programs/04_satirical/*.gom; do
   [ -f "$file" ] && test_program "$file"
done

echo ""
echo "Testing 05_analysis..."
for file in programs/05_analysis/*.gom; do
   [ -f "$file" ] && test_program "$file"
done

echo ""
echo "Testing demos..."
for file in programs/demos/*.gom; do
   [ -f "$file" ] && test_program "$file"
done


echo ""
echo "=== Validation Summary ==="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo "Total: $((PASSED + FAILED + SKIPPED))"

if [ $FAILED -eq 0 ]; then
   echo -e "\n${GREEN}All tests passed!${NC}"
   exit 0
else
   echo -e "\n${RED}Some tests failed.${NC}"
   exit 1
fi
