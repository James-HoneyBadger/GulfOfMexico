"""EXPERIMENTAL variable declaration and assignment handlers.

⚠️ WARNING: These handlers are NOT used in production! ⚠️

The actual Gulf of Mexico interpreter uses pattern matching in interpreter.py
to handle variable declarations and assignments. These handlers exist as a
proof-of-concept for an alternative modular architecture.
"""

from typing import Optional, Type
from gulfofmexico.handlers import StatementHandler
from gulfofmexico.processor.syntax_tree import (
    CodeStatement,
    VariableDeclaration,
    VariableAssignment,
)
from gulfofmexico.context import ExecutionContext
from gulfofmexico.builtin import GulfOfMexicoValue


class VariableDeclarationHandler(StatementHandler):
    """Handler for variable declarations (var x = 5!)."""

    def can_handle(self, statement: CodeStatement) -> bool:
        """Check if this is a variable declaration.

        Args:
            statement: Statement to check

        Returns:
            True if this is a VariableDeclaration
        """
        return isinstance(statement, VariableDeclaration)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a variable declaration.

        Args:
            statement: The variable declaration statement
            context: Execution context

        Returns:
            None (declarations don't return values)
        """
        # Import here to avoid circular dependencies
        from gulfofmexico.interpreter import (
            evaluate_expression,
            declare_new_variable,
        )

        # Type assertion for type checker
        assert isinstance(statement, VariableDeclaration)

        # Evaluate the expression
        value = evaluate_expression(
            statement.expression,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        # Declare the variable
        declare_new_variable(
            statement,
            value,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        """Return the statement type this handler processes.

        Returns:
            VariableDeclaration class
        """
        return VariableDeclaration


class VariableAssignmentHandler(StatementHandler):
    """Handler for variable assignments (x = 10!)."""

    def can_handle(self, statement: CodeStatement) -> bool:
        """Check if this is a variable assignment.

        Args:
            statement: Statement to check

        Returns:
            True if this is a VariableAssignment
        """
        return isinstance(statement, VariableAssignment)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a variable assignment.

        Args:
            statement: The variable assignment statement
            context: Execution context

        Returns:
            None (assignments don't return values)
        """
        # Import here to avoid circular dependencies
        from gulfofmexico.interpreter import (
            evaluate_expression,
            assign_variable,
        )

        # Type assertion for type checker
        assert isinstance(statement, VariableAssignment)

        # Evaluate index expressions
        indexes = [
            evaluate_expression(
                expr,
                context.namespaces,
                context.async_statements,
                context.when_watchers,
            )
            for expr in statement.indexes
        ]

        # Evaluate the new value
        new_value = evaluate_expression(
            statement.expression,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        # Perform the assignment
        assign_variable(
            statement,
            indexes,
            new_value,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        """Return the statement type this handler processes.

        Returns:
            VariableAssignment class
        """
        return VariableAssignment
