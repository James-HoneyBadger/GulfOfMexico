#!/usr/bin/env python3
"""
Verify Phase 4 Task 1: HandlerRegistry Registration

This script checks that:
1. All handler class files exist
2. They have been updated in create_production_registry()
3. The registry code compiles and is syntactically correct
"""

import sys
import os
from pathlib import Path

def check_handler_files():
    """Verify all handler files exist."""
    base_path = Path("/home/james/GulfOfMexico/gulfofmexico/handlers_impl")
    
    required_handlers = {
        "variable_declaration.py": "VariableDeclarationHandler",
        "variable_assignment.py": "VariableAssignmentHandler",
        "return_statement.py": "ReturnStatementHandler",
        "conditional.py": "ConditionalHandler",
        "when_statement.py": "WhenStatementHandler",
        "for_loop.py": "ForLoopHandler",
        "while_loop.py": "WhileLoopHandler",
        "function_definition.py": "FunctionDefinitionHandler",
        "class_declaration.py": "ClassDeclarationHandler",
        "advanced_statements.py": "AfterStatementHandler",
    }
    
    print("Checking handler files:")
    print("=" * 80)
    
    all_exist = True
    for filename, class_name in required_handlers.items():
        filepath = base_path / filename
        exists = filepath.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {filename:35s} -> {class_name}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_registry_code():
    """Check that create_production_registry() includes all handlers."""
    registry_path = Path("/home/james/GulfOfMexico/gulfofmexico/handler_registry.py")
    
    content = registry_path.read_text()
    
    required_imports = [
        "VariableDeclarationHandler",
        "VariableAssignmentHandler",
        "ReturnStatementHandler",
        "ConditionalHandler",
        "WhenStatementHandler",
        "ForLoopHandler",
        "WhileLoopHandler",
        "FunctionDefinitionHandler",
        "ClassDeclarationHandler",
        "AfterStatementHandler",
    ]
    
    print("\n\nChecking handler_registry.py registrations:")
    print("=" * 80)
    
    all_present = True
    for handler_name in required_imports:
        present = handler_name in content
        status = "✓" if present else "✗"
        print(f"  {status} {handler_name:35s} - {'registered' if present else 'MISSING'}")
        if not present:
            all_present = False
    
    return all_present

def check_registry_syntax():
    """Check that handler_registry.py is syntactically correct."""
    registry_path = Path("/home/james/GulfOfMexico/gulfofmexico/handler_registry.py")
    
    print("\n\nChecking handler_registry.py syntax:")
    print("=" * 80)
    
    try:
        with open(registry_path) as f:
            code = f.read()
        compile(code, str(registry_path), "exec")
        print("  ✓ handler_registry.py - syntax is valid")
        return True
    except SyntaxError as e:
        print(f"  ✗ handler_registry.py - SYNTAX ERROR: {e}")
        return False

def main():
    """Run all checks."""
    print("\n" + "="*80)
    print("Phase 4 Task 1: HandlerRegistry Registration Validation")
    print("="*80 + "\n")
    
    files_ok = check_handler_files()
    registry_ok = check_registry_code()
    syntax_ok = check_registry_syntax()
    
    print("\n" + "="*80)
    print("Summary:")
    print("="*80)
    print(f"  Handler files:     {'✓ PASS' if files_ok else '✗ FAIL'}")
    print(f"  Registry code:     {'✓ PASS' if registry_ok else '✗ FAIL'}")
    print(f"  Syntax valid:      {'✓ PASS' if syntax_ok else '✗ FAIL'}")
    
    all_pass = files_ok and registry_ok and syntax_ok
    
    if all_pass:
        print(f"\n✓ Phase 4 Task 1 VALIDATION PASSED")
        print(f"\nAll 10 handlers are registered in create_production_registry()")
        print(f"Ready for Task 2: Interpreter.py Modification")
    else:
        print(f"\n✗ Phase 4 Task 1 VALIDATION FAILED")
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
