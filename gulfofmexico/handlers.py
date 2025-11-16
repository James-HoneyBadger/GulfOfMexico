"""EXPERIMENTAL base classes for statement handlers.

⚠️ WARNING: This handler system is NOT used in production! ⚠️

The actual Gulf of Mexico interpreter uses pattern matching in interpreter.py
to execute statements. This experimental module demonstrates how a handler-based
architecture could work for potential future refactoring.
"""

from abc import ABC, abstractmethod
from typing import Optional, Type
from gulfofmexico.processor.syntax_tree import CodeStatement
from gulfofmexico.builtin import GulfOfMexicoValue


class StatementHandler(ABC):
    """EXPERIMENTAL abstract base class for statement handlers.

    ⚠️ WARNING: Handlers are NOT used in production! ⚠️

    The actual Gulf of Mexico interpreter uses pattern matching, not handlers.
    This class demonstrates how a handler system could work in an alternative
    architecture where each statement type has a corresponding handler.
    """

    @abstractmethod
    def can_handle(self, statement: CodeStatement) -> bool:
        """Check if this handler can process the given statement.

        Args:
            statement: The statement to check

        Returns:
            True if this handler can process the statement
        """
        pass

    @abstractmethod
    def execute(
        self,
        statement: CodeStatement,
        context: "ExecutionContext",  # noqa: F821
    ) -> Optional[GulfOfMexicoValue]:
        """Execute the statement.

        Args:
            statement: The statement to execute
            context: The execution context

        Returns:
            Optional return value from statement execution
        """
        pass

    @property
    @abstractmethod
    def statement_type(self) -> Type[CodeStatement]:
        """The statement type this handler processes.

        Returns:
            The CodeStatement subclass this handler handles
        """
        pass


class HandlerRegistry:
    """Registry for statement handlers.

    Manages all registered statement handlers and routes statements
    to the appropriate handler.
    """

    def __init__(self):
        """Initialize the handler registry."""
        self._handlers: list[StatementHandler] = []
        self._type_cache: dict[Type[CodeStatement], StatementHandler] = {}

    def register(self, handler: StatementHandler) -> None:
        """Register a new statement handler.

        Args:
            handler: The handler to register
        """
        self._handlers.append(handler)
        # Clear cache when new handler is registered
        self._type_cache.clear()

    def get_handler(self, statement: CodeStatement) -> Optional[StatementHandler]:
        """Get the appropriate handler for a statement.

        Args:
            statement: The statement to find a handler for

        Returns:
            The handler if found, None otherwise
        """
        stmt_type = type(statement)

        # Check cache first
        if stmt_type in self._type_cache:
            return self._type_cache[stmt_type]

        # Find handler
        for handler in self._handlers:
            if handler.can_handle(statement):
                self._type_cache[stmt_type] = handler
                return handler

        return None

    def execute_statement(
        self,
        statement: CodeStatement,
        context: "ExecutionContext",  # noqa: F821
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a statement using the appropriate handler.

        Args:
            statement: The statement to execute
            context: The execution context

        Returns:
            Optional return value from statement execution

        Raises:
            ValueError: If no handler found for statement type
        """
        handler = self.get_handler(statement)
        if handler is None:
            raise ValueError(
                f"No handler registered for statement type: "
                f"{type(statement).__name__}"
            )

        return handler.execute(statement, context)


class CompositeHandler(StatementHandler):
    """A handler that delegates to multiple sub-handlers.

    Useful for grouping related statement types under a single handler.
    """

    def __init__(self, handlers: list[StatementHandler]):
        """Initialize the composite handler.

        Args:
            handlers: List of sub-handlers
        """
        self._handlers = handlers

    def can_handle(self, statement: CodeStatement) -> bool:
        """Check if any sub-handler can handle the statement.

        Args:
            statement: The statement to check

        Returns:
            True if any sub-handler can handle it
        """
        return any(h.can_handle(statement) for h in self._handlers)

    def execute(
        self,
        statement: CodeStatement,
        context: "ExecutionContext",  # noqa: F821
    ) -> Optional[GulfOfMexicoValue]:
        """Execute using the first matching sub-handler.

        Args:
            statement: The statement to execute
            context: The execution context

        Returns:
            Result from sub-handler execution

        Raises:
            ValueError: If no sub-handler can handle the statement
        """
        for handler in self._handlers:
            if handler.can_handle(statement):
                return handler.execute(statement, context)

        raise ValueError(f"No sub-handler for {type(statement).__name__}")

    @property
    def statement_type(self) -> Type[CodeStatement]:
        """Return the base CodeStatement type.

        Returns:
            CodeStatement base class
        """
        return CodeStatement
