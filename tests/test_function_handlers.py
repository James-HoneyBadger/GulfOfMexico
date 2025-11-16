"""⚠️ EXPERIMENTAL - Unit tests for experimental function handlers.

WARNING: These tests validate the EXPERIMENTAL function handlers in
gulfofmexico/engine/handlers/functions.py, NOT the production interpreter.

The production interpreter handles function definitions and calls
via pattern matching in interpreter.py, not through these handlers.
"""

import unittest
from gulfofmexico.engine.handlers.functions import (
    FunctionDefinitionHandler,
    ClassDeclarationHandler,
)
from gulfofmexico.processor.syntax_tree import (
    FunctionDefinition,
    ClassDeclaration,
    VariableDeclaration,
)


class TestFunctionDefinitionHandler(unittest.TestCase):
    """Test cases for FunctionDefinitionHandler."""

    def setUp(self):
        self.handler = FunctionDefinitionHandler()

    def test_can_handle_function_definition(self):
        """Test that handler recognizes FunctionDefinition."""
        stmt = FunctionDefinition(None, None, None, None, None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, FunctionDefinition)


class TestClassDeclarationHandler(unittest.TestCase):
    """Test cases for ClassDeclarationHandler."""

    def setUp(self):
        self.handler = ClassDeclarationHandler()

    def test_can_handle_class_declaration(self):
        """Test that handler recognizes ClassDeclaration."""
        stmt = ClassDeclaration(None, None, None, None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, ClassDeclaration)


if __name__ == "__main__":
    unittest.main()
