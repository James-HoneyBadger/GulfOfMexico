"""⚠️ EXPERIMENTAL - Unit tests for experimental special statement handlers.

WARNING: These tests validate the EXPERIMENTAL special handlers in
gulfofmexico/engine/handlers/special.py, NOT the production interpreter.

The production interpreter handles special statements (import, export, etc.)
via pattern matching in interpreter.py, not through these handlers.
"""

import unittest
from gulfofmexico.engine.handlers.special import (
    DeleteStatementHandler,
    ReverseStatementHandler,
    ImportStatementHandler,
    ExportStatementHandler,
    ReturnStatementHandler,
    ExpressionStatementHandler,
)
from gulfofmexico.processor.syntax_tree import (
    DeleteStatement,
    ReverseStatement,
    ImportStatement,
    ExportStatement,
    ReturnStatement,
    ExpressionStatement,
    VariableDeclaration,
)


class TestDeleteStatementHandler(unittest.TestCase):
    """Test cases for DeleteStatementHandler."""

    def setUp(self):
        self.handler = DeleteStatementHandler()

    def test_can_handle_delete(self):
        """Test that handler recognizes DeleteStatement."""
        stmt = DeleteStatement(None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, DeleteStatement)


class TestReverseStatementHandler(unittest.TestCase):
    """Test cases for ReverseStatementHandler."""

    def setUp(self):
        self.handler = ReverseStatementHandler()

    def test_can_handle_reverse(self):
        """Test that handler recognizes ReverseStatement."""
        stmt = ReverseStatement(None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, ReverseStatement)


class TestImportStatementHandler(unittest.TestCase):
    """Test cases for ImportStatementHandler."""

    def setUp(self):
        self.handler = ImportStatementHandler()

    def test_can_handle_import(self):
        """Test that handler recognizes ImportStatement."""
        stmt = ImportStatement(None, None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, ImportStatement)


class TestExportStatementHandler(unittest.TestCase):
    """Test cases for ExportStatementHandler."""

    def setUp(self):
        self.handler = ExportStatementHandler()

    def test_can_handle_export(self):
        """Test that handler recognizes ExportStatement."""
        stmt = ExportStatement(None, None, None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, ExportStatement)


class TestReturnStatementHandler(unittest.TestCase):
    """Test cases for ReturnStatementHandler."""

    def setUp(self):
        self.handler = ReturnStatementHandler()

    def test_can_handle_return(self):
        """Test that handler recognizes ReturnStatement."""
        stmt = ReturnStatement(None, None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, ReturnStatement)


class TestExpressionStatementHandler(unittest.TestCase):
    """Test cases for ExpressionStatementHandler."""

    def setUp(self):
        self.handler = ExpressionStatementHandler()

    def test_can_handle_expression(self):
        """Test that handler recognizes ExpressionStatement."""
        stmt = ExpressionStatement(None, None)
        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_types(self):
        """Test that handler rejects other statement types."""
        stmt = VariableDeclaration(None, None, None, None, None, None, None)
        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type(self):
        """Test that statement_type property is correct."""
        self.assertEqual(self.handler.statement_type, ExpressionStatement)


if __name__ == "__main__":
    unittest.main()
