"""EXPERIMENTAL control flow statement handlers.

⚠️ WARNING: These handlers are NOT used in production! ⚠️

The actual Gulf of Mexico interpreter uses pattern matching in interpreter.py
to handle control flow statements. These handlers exist as a proof-of-concept
for an alternative modular architecture.
"""

from typing import Optional, Type
from gulfofmexico.handlers import StatementHandler
from gulfofmexico.processor.syntax_tree import (
    CodeStatement,
    Conditional,
    WhenStatement,
    AfterStatement,
)
from gulfofmexico.context import ExecutionContext
from gulfofmexico.builtin import GulfOfMexicoValue


class ConditionalHandler(StatementHandler):
    """Handler for conditional statements (if/when expressions)."""

    def can_handle(self, statement: CodeStatement) -> bool:
        """Check if this is a conditional statement.

        Args:
            statement: Statement to check

        Returns:
            True if this is a Conditional
        """
        return isinstance(statement, Conditional)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a conditional statement.

        Args:
            statement: The conditional statement
            context: Execution context

        Returns:
            Optional return value from conditional code
        """
        from gulfofmexico.interpreter import (
            evaluate_expression,
            execute_conditional,
        )

        assert isinstance(statement, Conditional)

        # Evaluate condition
        condition = evaluate_expression(
            statement.expression,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        # Execute conditional code
        result = execute_conditional(
            condition,
            statement.code,
            context.namespaces,
            context.when_watchers,
            context.importable_names,
            context.exported_names,
        )

        return result

    @property
    def statement_type(self) -> Type[CodeStatement]:
        """Return the statement type this handler processes.

        Returns:
            Conditional class
        """
        return Conditional


class WhenStatementHandler(StatementHandler):
    """Handler for reactive 'when' statements."""

    def can_handle(self, statement: CodeStatement) -> bool:
        """Check if this is a when statement.

        Args:
            statement: Statement to check

        Returns:
            True if this is a WhenStatement
        """
        return isinstance(statement, WhenStatement)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a when statement (register watcher).

        Args:
            statement: The when statement
            context: Execution context

        Returns:
            None (when statements register watchers, don't return)
        """
        from gulfofmexico.interpreter import register_when_statement

        assert isinstance(statement, WhenStatement)

        # Register the when statement watcher
        register_when_statement(
            statement.expression,
            statement.code,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
            context.importable_names,
            context.exported_names,
        )

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        """Return the statement type this handler processes.

        Returns:
            WhenStatement class
        """
        return WhenStatement


class AfterStatementHandler(StatementHandler):
    """Handler for 'after' statements (event listeners)."""

    def can_handle(self, statement: CodeStatement) -> bool:
        """Check if this is an after statement.

        Args:
            statement: Statement to check

        Returns:
            True if this is an AfterStatement
        """
        return isinstance(statement, AfterStatement)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute an after statement (register event listener).

        Args:
            statement: The after statement
            context: Execution context

        Returns:
            None (after statements register listeners, don't return)
        """
        from gulfofmexico.interpreter import (
            evaluate_expression,
            execute_after_statement,
        )

        assert isinstance(statement, AfterStatement)

        # Evaluate the event expression
        event = evaluate_expression(
            statement.expression,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        # Register the after statement listener
        execute_after_statement(
            event,
            statement.code,
            context.namespaces,
            context.when_watchers,
            context.importable_names,
            context.exported_names,
        )

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        """Return the statement type this handler processes.

        Returns:
            AfterStatement class
        """
        return AfterStatement
