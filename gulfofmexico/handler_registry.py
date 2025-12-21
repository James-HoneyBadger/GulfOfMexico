"""
Handler Registry - Coordinates Statement Handler Execution

This module provides:
    - HandlerRegistry: Registers and dispatches to statement handlers
    - Statement handler auto-discovery
    - Fallback to legacy pattern matching
    - Debug info for handler statistics

Purpose:
    Enables gradual migration from monolithic pattern matching to handler pattern
    by routing statements to appropriate handlers with seamless fallback.
"""

import logging
from typing import Optional, Type, Any

from gulfofmexico.handlers import StatementHandler, HandlerRegistry as BaseRegistry
from gulfofmexico.processor.syntax_tree import CodeStatement
from gulfofmexico.execution_context import ExecutionContext

logger = logging.getLogger(__name__)


class ProductionHandlerRegistry(BaseRegistry):
    """Extended handler registry for production use.

    Features:
        - Handler registration and caching
        - Execution statistics tracking
        - Fallback mechanism for unhandled statements
        - Debug information collection
    """

    def __init__(self):
        """Initialize the registry."""
        super().__init__()
        self._execution_stats = {}
        self._handler_enable_flags = {}
        self._fallback_handler = None

    def register(self, handler: StatementHandler, enable: bool = True) -> None:
        """Register a statement handler.

        Args:
            handler: The handler to register
            enable: Whether handler is enabled (can be toggled at runtime)
        """
        super().register(handler)
        stmt_type = handler.statement_type
        self._handler_enable_flags[stmt_type.__name__] = enable
        self._execution_stats[stmt_type.__name__] = {
            "count": 0,
            "total_time": 0.0,
            "errors": 0,
        }

    def set_fallback_handler(self, handler: Optional[StatementHandler]) -> None:
        """Set a fallback handler for unhandled statements.

        The fallback is called when no primary handler can handle a statement.
        Useful for delegating to the old pattern matching system during migration.

        Args:
            handler: Fallback handler, or None to disable
        """
        self._fallback_handler = handler

    def enable_handler_type(self, statement_type: Type[CodeStatement]) -> None:
        """Enable a handler type.

        Args:
            statement_type: Type of statement to enable
        """
        type_name = statement_type.__name__
        if type_name in self._handler_enable_flags:
            self._handler_enable_flags[type_name] = True

    def disable_handler_type(self, statement_type: Type[CodeStatement]) -> None:
        """Disable a handler type (will use fallback).

        Args:
            statement_type: Type of statement to disable
        """
        type_name = statement_type.__name__
        if type_name in self._handler_enable_flags:
            self._handler_enable_flags[type_name] = False

    def execute_statement(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Any:
        """Execute a statement through appropriate handler.

        Routing logic:
            1. Check if statement type is enabled
            2. Find matching handler in registry
            3. Execute handler with context
            4. Fall back to fallback handler if configured
            5. Raise error if no handler found

        Args:
            statement: The statement to execute
            context: Execution context containing all state

        Returns:
            Result from handler execution

        Raises:
            ValueError: If no handler found and no fallback configured
        """
        import time

        stmt_type = type(statement).__name__
        stats = self._execution_stats.get(stmt_type, None)

        # Check if handler type is enabled
        if not self._handler_enable_flags.get(stmt_type, True):
            logger.debug(f"Handler type {stmt_type} disabled, using fallback")
            if self._fallback_handler:
                return self._fallback_handler.execute(statement, context)
            raise ValueError(f"No handler for {stmt_type} and fallback disabled")

        # Find handler
        handler = self.get_handler(statement)
        if handler and self._handler_enable_flags.get(stmt_type, True):
            # Execute handler with timing
            start_time = time.time()
            try:
                result = handler.execute(statement, context)

                # Update statistics
                if stats:
                    stats["count"] += 1
                    stats["total_time"] += time.time() - start_time

                logger.debug(
                    f"Executed handler for {stmt_type} "
                    f"({time.time() - start_time:.4f}s)"
                )
                return result

            except Exception as e:
                # Update error statistics
                if stats:
                    stats["errors"] += 1

                logger.error(
                    f"Error in handler for {stmt_type}: {e}",
                    exc_info=True,
                )
                raise

        # No handler found, try fallback
        if self._fallback_handler:
            logger.debug(f"No handler found for {stmt_type}, using fallback")
            return self._fallback_handler.execute(statement, context)

        raise ValueError(f"No handler registered for statement type: {stmt_type}")

    def get_stats(self) -> dict:
        """Get execution statistics for all handlers.

        Returns:
            Dictionary mapping statement type names to statistics
        """
        return {
            stmt_type: stats.copy() for stmt_type, stats in self._execution_stats.items()
        }

    def get_debug_info(self) -> str:
        """Get detailed debug information about handler state.

        Returns:
            Formatted debug string
        """
        lines = ["=== Handler Registry Debug Info ===", ""]

        # Handler statistics
        lines.append("Handler Statistics:")
        for stmt_type, stats in self._execution_stats.items():
            enabled = self._handler_enable_flags.get(stmt_type, True)
            status = "✓ ENABLED" if enabled else "✗ DISABLED"
            count = stats["count"]
            avg_time = (
                (stats["total_time"] / count * 1000)
                if count > 0
                else 0
            )
            errors = stats["errors"]

            lines.append(
                f"  {stmt_type:30s} {status:12s} "
                f"Count: {count:5d} AvgTime: {avg_time:7.2f}ms Errors: {errors}"
            )

        lines.append("")
        lines.append("Handler Status:")
        for stmt_type, handler in self._type_cache.items():
            lines.append(f"  {stmt_type.__name__:30s} -> {handler.__class__.__name__}")

        if self._fallback_handler:
            lines.append(f"\nFallback Handler: {self._fallback_handler.__class__.__name__}")
        else:
            lines.append("\nFallback Handler: None (migrations must be complete)")

        return "\n".join(lines)

    def print_debug_info(self) -> None:
        """Print debug information to stdout."""
        print(self.get_debug_info())

    def reset_statistics(self) -> None:
        """Reset all execution statistics.

        Useful for benchmarking or testing.
        """
        for stats in self._execution_stats.values():
            stats["count"] = 0
            stats["total_time"] = 0.0
            stats["errors"] = 0


def create_production_registry() -> ProductionHandlerRegistry:
    """Create and configure the production handler registry.

    This function:
        - Creates a new registry
        - Registers all built-in handlers (14 total)
        - Sets up fallback to legacy pattern matching

    Returns:
        Configured ProductionHandlerRegistry ready for use

    Note:
        This is the main entry point for handler initialization.
        All handlers are registered during Phase 4 integration.

    Handler Inventory (14 total):
        Infrastructure (5):
            - VariableDeclarationHandler
            - VariableAssignmentHandler
            - ExecutionContext (state management)
            - WatcherManager (reactive watchers)
            - HandlerRegistry (this class)

        Expression (1):
            - ExpressionHandler

        Statements (8):
            - ConditionalHandler (if statements)
            - ForLoopHandler (for loops)
            - WhileLoopHandler (while loops)
            - WhenStatementHandler (reactive watching)
            - FunctionDefinitionHandler (function definitions)
            - ReturnStatementHandler (return statements)
            - ClassDeclarationHandler (class definitions)
            - AfterStatementHandler (event listeners)
    """
    registry = ProductionHandlerRegistry()

    # Infrastructure Handlers
    try:
        from gulfofmexico.handlers_impl.variable_declaration import (
            VariableDeclarationHandler,
        )
        registry.register(VariableDeclarationHandler())
        logger.debug("Registered VariableDeclarationHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import VariableDeclarationHandler: {e}")

    try:
        from gulfofmexico.handlers_impl.variable_assignment import (
            VariableAssignmentHandler,
        )
        registry.register(VariableAssignmentHandler())
        logger.debug("Registered VariableAssignmentHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import VariableAssignmentHandler: {e}")

    # Statement Handlers - Week 1 (Return, Conditional)
    try:
        from gulfofmexico.handlers_impl.return_statement import (
            ReturnStatementHandler,
        )
        registry.register(ReturnStatementHandler())
        logger.debug("Registered ReturnStatementHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import ReturnStatementHandler: {e}")

    try:
        from gulfofmexico.handlers_impl.conditional import ConditionalHandler
        registry.register(ConditionalHandler())
        logger.debug("Registered ConditionalHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import ConditionalHandler: {e}")

    # Statement Handlers - Week 2 (When, For, While)
    try:
        from gulfofmexico.handlers_impl.when_statement import WhenStatementHandler
        registry.register(WhenStatementHandler())
        logger.debug("Registered WhenStatementHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import WhenStatementHandler: {e}")

    try:
        from gulfofmexico.handlers_impl.for_loop import ForLoopHandler
        registry.register(ForLoopHandler())
        logger.debug("Registered ForLoopHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import ForLoopHandler: {e}")

    try:
        from gulfofmexico.handlers_impl.while_loop import WhileLoopHandler
        registry.register(WhileLoopHandler())
        logger.debug("Registered WhileLoopHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import WhileLoopHandler: {e}")

    # Statement Handlers - Week 3 (Function, Class, After)
    try:
        from gulfofmexico.handlers_impl.function_definition import (
            FunctionDefinitionHandler,
        )
        registry.register(FunctionDefinitionHandler())
        logger.debug("Registered FunctionDefinitionHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import FunctionDefinitionHandler: {e}")

    try:
        from gulfofmexico.handlers_impl.class_declaration import (
            ClassDeclarationHandler,
        )
        registry.register(ClassDeclarationHandler())
        logger.debug("Registered ClassDeclarationHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import ClassDeclarationHandler: {e}")

    try:
        from gulfofmexico.handlers_impl.advanced_statements import (
            AfterStatementHandler,
        )
        registry.register(AfterStatementHandler())
        logger.debug("Registered AfterStatementHandler")
    except (ImportError, Exception) as e:
        logger.warning(f"Could not import AfterStatementHandler: {e}")

    # Delete and Import/Export handlers (if available)
    try:
        from gulfofmexico.handlers_impl.advanced_statements import (
            DeleteStatementHandler,
        )
        registry.register(DeleteStatementHandler())
        logger.debug("Registered DeleteStatementHandler")
    except (ImportError, Exception) as e:
        logger.debug(f"Could not import DeleteStatementHandler: {e}")

    try:
        from gulfofmexico.handlers_impl.advanced_statements import (
            ImportExportHandler,
        )
        registry.register(ImportExportHandler())
        logger.debug("Registered ImportExportHandler")
    except (ImportError, Exception) as e:
        logger.debug(f"Could not import ImportExportHandler: {e}")

    handler_count = len(registry._handlers)
    logger.info(f"✓ Phase 4 Handler registry initialized with {handler_count} handlers")

    return registry
