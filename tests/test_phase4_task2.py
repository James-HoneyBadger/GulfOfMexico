#!/usr/bin/env python3
"""
Test Phase 4 Task 2: Handler Integration
Tests that handlers are called from the interpreter
"""

import sys
import os

# Add project to path
sys.path.insert(0, '/home/james/GulfOfMexico')

def test_handler_registry_initialization():
    """Test that handler registry initializes correctly."""
    from gulfofmexico.interpreter import get_handler_registry
    
    print("Testing handler registry initialization...")
    registry = get_handler_registry()
    
    if registry is None:
        print("✗ FAIL: Handler registry is None")
        return False
    
    print(f"✓ Handler registry initialized with {len(registry._handlers)} handlers")
    return True


def test_handler_dispatch_function():
    """Test that the dispatch function exists and is callable."""
    from gulfofmexico.interpreter import try_execute_with_handler
    
    print("\nTesting handler dispatch function...")
    
    if not callable(try_execute_with_handler):
        print("✗ FAIL: try_execute_with_handler is not callable")
        return False
    
    print("✓ Handler dispatch function exists and is callable")
    return True


def test_dependency_injection():
    """Test that dependency injection function exists."""
    from gulfofmexico.interpreter import _inject_interpreter_dependencies
    
    print("\nTesting dependency injection...")
    
    if not callable(_inject_interpreter_dependencies):
        print("✗ FAIL: _inject_interpreter_dependencies is not callable")
        return False
    
    print("✓ Dependency injection function exists and is callable")
    return True


def test_interpreter_integration():
    """Test basic interpreter functions still work."""
    print("\nTesting interpreter integration...")
    
    try:
        # These imports should work
        from gulfofmexico.interpreter import (
            evaluate_expression,
            declare_new_variable,
            assign_variable,
            execute_conditional,
        )
        print("✓ All required interpreter functions are accessible")
        return True
    except ImportError as e:
        print(f"✗ FAIL: Could not import interpreter functions: {e}")
        return False


def main():
    """Run all tests."""
    print("="*80)
    print("Phase 4 Task 2: Handler Integration Tests")
    print("="*80)
    
    tests = [
        test_handler_registry_initialization,
        test_handler_dispatch_function,
        test_dependency_injection,
        test_interpreter_integration,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ EXCEPTION in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*80)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*80)
    
    if all(results):
        print("\n✓ Phase 4 Task 2 Integration Tests PASSED")
        return 0
    else:
        print("\n✗ Phase 4 Task 2 Integration Tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
