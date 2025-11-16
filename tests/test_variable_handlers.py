"""⚠️ EXPERIMENTAL - Unit tests for experimental variable handlers.

WARNING: These tests validate the EXPERIMENTAL variable handlers in
gulfofmexico/engine/handlers/variables.py, NOT the production interpreter.

The production interpreter handles variable declarations and assignments
via pattern matching in interpreter.py, not through these handlers.
"""

import unittest
from gulfofmexico.engine.handlers.variables import (
    VariableDeclarationHandler,
    VariableAssignmentHandler,
)
from gulfofmexico.processor.syntax_tree import (
    VariableDeclaration,
    VariableAssignment,
)
from gulfofmexico.context import ExecutionContext
from gulfofmexico.builtin import (
    GulfOfMexicoNumber,
    Variable,
    VariableLifetime,
)
from gulfofmexico.base import Token, TokenType
from gulfofmexico.processor.expression_tree import ValueNode


class TestVariableDeclarationHandler(unittest.TestCase):
    """Test cases for VariableDeclarationHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = VariableDeclarationHandler()
        self.context = ExecutionContext(
            filename="test.gom",
            code="var x = 5!",
            namespaces=[{}],
            async_statements=[],
            when_watchers=[{}],
            importable_names={},
            exported_names=[],
        )

    def test_can_handle_variable_declaration(self):
        """Test that handler recognizes VariableDeclaration."""
        stmt = VariableDeclaration(
            name=Token(TokenType.NAME, "x", 1, 4),
            modifiers=[Token(TokenType.NAME, "var", 1, 0)],
            type_annotation=None,
            lifetime=None,
            expression=ValueNode(GulfOfMexicoNumber(5)),
            debug=0,
            confidence=1,
        )

        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_statements(self):
        """Test that handler rejects non-VariableDeclaration."""
        stmt = VariableAssignment(
            name=Token(TokenType.NAME, "x", 1, 0),
            expression=ValueNode(GulfOfMexicoNumber(10)),
            debug=0,
            indexes=[],
            confidence=1,
        )

        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type_property(self):
        """Test that statement_type returns correct type."""
        self.assertEqual(self.handler.statement_type, VariableDeclaration)


class TestVariableAssignmentHandler(unittest.TestCase):
    """Test cases for VariableAssignmentHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = VariableAssignmentHandler()
        self.context = ExecutionContext(
            filename="test.gom",
            code="x = 10!",
            namespaces=[
                {
                    "x": Variable(
                        "x",
                        [
                            VariableLifetime(
                                GulfOfMexicoNumber(5), 100000000000, 0, True, True
                            )
                        ],
                        [],
                    )
                }
            ],
            async_statements=[],
            when_watchers=[{}],
            importable_names={},
            exported_names=[],
        )

    def test_can_handle_variable_assignment(self):
        """Test that handler recognizes VariableAssignment."""
        stmt = VariableAssignment(
            name=Token(TokenType.NAME, "x", 1, 0),
            expression=ValueNode(GulfOfMexicoNumber(10)),
            debug=0,
            indexes=[],
            confidence=1,
        )

        self.assertTrue(self.handler.can_handle(stmt))

    def test_cannot_handle_other_statements(self):
        """Test that handler rejects non-VariableAssignment."""
        stmt = VariableDeclaration(
            name=Token(TokenType.NAME, "y", 1, 4),
            modifiers=[Token(TokenType.NAME, "var", 1, 0)],
            type_annotation=None,
            lifetime=None,
            expression=ValueNode(GulfOfMexicoNumber(5)),
            debug=0,
            confidence=1,
        )

        self.assertFalse(self.handler.can_handle(stmt))

    def test_statement_type_property(self):
        """Test that statement_type returns correct type."""
        self.assertEqual(self.handler.statement_type, VariableAssignment)


if __name__ == "__main__":
    unittest.main()
