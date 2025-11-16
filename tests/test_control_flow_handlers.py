"""⚠️ EXPERIMENTAL - Unit tests for experimental control flow handlers.

WARNING: These tests validate the EXPERIMENTAL control flow handlers in
gulfofmexico/engine/handlers/control_flow.py, NOT the production interpreter.

The production interpreter handles control flow (if/else, when, after, etc.)
via pattern matching in interpreter.py, not through these handlers.
"""

import unittest
from gulfofmexico.engine.handlers.control_flow import (
    ConditionalHandler,
    WhenStatementHandler,
    AfterStatementHandler,
)
from gulfofmexico.processor.syntax_tree import (
    ConditionalStatement,
    WhenStatement,
    AfterStatement,
    VariableDeclaration,
)


class TestConditionalHandler(unittest.TestCase):
    """Test cases for ConditionalHandler."""

    def setUp(self):
        self.handler = ConditionalHandler()

    def test_can_handle_conditional(self):
        """Test that handler recognizes ConditionalStatement."""
        stmt = ConditionalStatement(None, None, None, None, None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, ConditionalStatement)


class TestWhenStatementHandler(unittest.TestCase):
    """Test cases for WhenStatementHandler."""

    def setUp(self):
        self.handler = WhenStatementHandler()

    def test_can_handle_when(self):
        """Test that handler recognizes WhenStatement."""
        stmt = WhenStatement(None, None, None, None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, WhenStatement)


class TestAfterStatementHandler(unittest.TestCase):
    """Test cases for AfterStatementHandler."""

    def setUp(self):
        self.handler = AfterStatementHandler()

    def test_can_handle_after(self):
        """Test that handler recognizes AfterStatement."""
        stmt = AfterStatement(None, None, None, None, None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, AfterStatement)


if __name__ == "__main__":
    unittest.main()
