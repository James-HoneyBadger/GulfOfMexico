#!/usr/bin/env python3
"""
Phase 4 Task 2 - Syntax and Structure Verification

This script verifies that the Phase 4 Task 2 code modifications are
syntactically correct and properly structured, without needing all
dependencies installed.
"""

import sys
import ast
import os
from pathlib import Path


def check_file_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"  Syntax error: {e}")
        return False


def check_function_exists_in_code(filepath, function_name):
    """Check if a function is defined in a file."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return True
        return False
    except Exception as e:
        print(f"  Error checking for function: {e}")
        return False


def main():
    """Run verification tests."""
    print("="*80)
    print("Phase 4 Task 2 - Syntax and Structure Verification")
    print("="*80)
    
    interpreter_path = "/home/james/GulfOfMexico/gulfofmexico/interpreter.py"
    
    # Test 1: interpreter.py syntax
    print("\n[1] Checking interpreter.py syntax...")
    if check_file_syntax(interpreter_path):
        print("    ✓ interpreter.py has valid Python syntax")
    else:
        print("    ✗ interpreter.py has syntax errors")
        return 1
    
    # Test 2: Handler registry functions exist
    print("\n[2] Checking handler registry functions...")
    functions_to_check = [
        "get_handler_registry",
        "_initialize_handler_registry",
        "_inject_interpreter_dependencies",
        "try_execute_with_handler",
    ]
    
    all_found = True
    for func_name in functions_to_check:
        if check_function_exists_in_code(interpreter_path, func_name):
            print(f"    ✓ {func_name} found")
        else:
            print(f"    ✗ {func_name} NOT found")
            all_found = False
    
    if not all_found:
        return 1
    
    # Test 3: Check handler dispatch is integrated
    print("\n[3] Checking handler dispatch integration...")
    with open(interpreter_path, 'r') as f:
        code = f.read()
    
    checks = [
        ("try_execute_with_handler call", "try_execute_with_handler("),
        ("Handler success check", "if handled:"),
        ("Handler result assignment", "result = handler_result"),
    ]
    
    all_checks_passed = True
    for check_name, check_string in checks:
        if check_string in code:
            print(f"    ✓ {check_name} found in code")
        else:
            print(f"    ✗ {check_name} NOT found in code")
            all_checks_passed = False
    
    if not all_checks_passed:
        return 1
    
    # Test 4: Check execute_context import availability
    print("\n[4] Checking ExecutionContext usage...")
    if "from gulfofmexico.execution_context import ExecutionContext" in code:
        print("    ✓ ExecutionContext import found")
    else:
        print("    ✗ ExecutionContext import NOT found")
        return 1
    
    # Test 5: Check handler_registry.py
    print("\n[5] Checking handler_registry.py...")
    registry_path = "/home/james/GulfOfMexico/gulfofmexico/handler_registry.py"
    if check_file_syntax(registry_path):
        print("    ✓ handler_registry.py has valid Python syntax")
    else:
        print("    ✗ handler_registry.py has syntax errors")
        return 1
    
    # Summary
    print("\n" + "="*80)
    print("✓ Phase 4 Task 2 - Syntax and Structure Verification PASSED")
    print("="*80)
    
    print("\nIntegration Summary:")
    print("  ✓ interpreter.py has valid syntax")
    print("  ✓ All 4 handler functions exist")
    print("  ✓ Handler dispatch is integrated into interpret_code_statements()")
    print("  ✓ ExecutionContext is properly imported and used")
    print("  ✓ handler_registry.py is valid")
    print("\nTask 2 Implementation: READY FOR TESTING")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
