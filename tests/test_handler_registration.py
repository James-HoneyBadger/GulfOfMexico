#!/usr/bin/env python3
"""Test script to validate handler registration during Phase 4."""

import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_handler_imports():
    """Test that all handlers can be imported individually."""
    
    handlers_to_test = [
        ("gulfofmexico.handlers_impl.variable_declaration", "VariableDeclarationHandler"),
        ("gulfofmexico.handlers_impl.variable_assignment", "VariableAssignmentHandler"),
        ("gulfofmexico.handlers_impl.return_statement", "ReturnStatementHandler"),
        ("gulfofmexico.handlers_impl.conditional", "ConditionalHandler"),
        ("gulfofmexico.handlers_impl.when_statement", "WhenStatementHandler"),
        ("gulfofmexico.handlers_impl.for_loop", "ForLoopHandler"),
        ("gulfofmexico.handlers_impl.while_loop", "WhileLoopHandler"),
        ("gulfofmexico.handlers_impl.function_definition", "FunctionDefinitionHandler"),
        ("gulfofmexico.handlers_impl.class_declaration", "ClassDeclarationHandler"),
        ("gulfofmexico.handlers_impl.advanced_statements", "AfterStatementHandler"),
    ]
    
    successful = []
    failed = []
    
    for module_name, class_name in handlers_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            handler_class = getattr(module, class_name)
            instance = handler_class()
            successful.append(f"{class_name}")
            print(f"✓ {class_name:35s} OK")
        except Exception as e:
            failed.append((class_name, str(e)))
            print(f"✗ {class_name:35s} FAILED: {e}")
    
    print("\n" + "="*80)
    print(f"Handler Import Summary:")
    print(f"  ✓ Successful: {len(successful)}/10")
    print(f"  ✗ Failed: {len(failed)}/10")
    
    if failed:
        print("\nFailed handlers:")
        for class_name, error in failed:
            print(f"  - {class_name}: {error}")
        return False
    
    print("\n✓ All handlers imported successfully!")
    return True

if __name__ == "__main__":
    success = test_handler_imports()
    sys.exit(0 if success else 1)
