"""
EXPERIMENTAL Interpreter Engine - Handler-Based Architecture

⚠️ WARNING: This module is NOT used in production! ⚠️

The production Gulf of Mexico interpreter uses the monolithic implementation
in gulfofmexico/interpreter.py (~2,900 lines). This experimental engine exists
as a proof-of-concept for alternative architecture but is NOT integrated.

Architecture:
    - InterpretEngine: Main engine class (unused in production)
    - HandlerRegistry: Statement handler lookup system
    - ExpressionEvaluator: Expression evaluation with optional caching
    - NamespaceManager: Namespace and variable management

Purpose:
    This demonstrates how the interpreter COULD work with:
    - Modular handler pattern instead of monolithic pattern matching
    - Expression caching for repeated evaluations
    - Plugin system for extensibility
    - Cleaner separation of concerns

Reality:
    All production code execution flows through interpreter.py's
    interpret_code_statements() function with direct pattern matching.
    This experimental code exists for future refactoring exploration.
"""

from typing import Optional
from gulfofmexico.handlers import HandlerRegistry
from gulfofmexico.context import ExecutionContext, InterpreterConfig
from gulfofmexico.processor.syntax_tree import CodeStatement
from gulfofmexico.builtin import GulfOfMexicoValue
from gulfofmexico.engine.evaluator import ExpressionEvaluator


class InterpretEngine:
    """EXPERIMENTAL interpreter engine using handler-based architecture.

    ⚠️ WARNING: This class is NOT used in production! ⚠️

    The actual Gulf of Mexico interpreter uses pattern matching in
    interpreter.py. This experimental class demonstrates how execution
    could work with a handler registry pattern for potential future use.
    """

    def __init__(self, config: Optional[InterpreterConfig] = None):
        """Initialize the interpreter engine.

        Args:
            config: Configuration options (uses defaults if None)
        """
        self.config = config or InterpreterConfig()
        self.registry = HandlerRegistry()
        self.evaluator = ExpressionEvaluator(
            enable_cache=self.config.enable_expression_cache
        )

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register all default statement handlers."""
        from gulfofmexico.engine.handlers.variables import (
            VariableDeclarationHandler,
            VariableAssignmentHandler,
        )
        from gulfofmexico.engine.handlers.control_flow import (
            ConditionalHandler,
            WhenStatementHandler,
            AfterStatementHandler,
        )
        from gulfofmexico.engine.handlers.functions import (
            FunctionDefinitionHandler,
            ClassDeclarationHandler,
        )
        from gulfofmexico.engine.handlers.special import (
            DeleteStatementHandler,
            ReverseStatementHandler,
            ImportStatementHandler,
            ExportStatementHandler,
            ReturnStatementHandler,
            ExpressionStatementHandler,
        )

        # Register variable handlers
        self.registry.register(VariableDeclarationHandler())
        self.registry.register(VariableAssignmentHandler())

        # Register control flow handlers
        self.registry.register(ConditionalHandler())
        self.registry.register(WhenStatementHandler())
        self.registry.register(AfterStatementHandler())

        # Register function/class handlers
        self.registry.register(FunctionDefinitionHandler())
        self.registry.register(ClassDeclarationHandler())

        # Register special statement handlers
        self.registry.register(DeleteStatementHandler())
        self.registry.register(ReverseStatementHandler())
        self.registry.register(ImportStatementHandler())
        self.registry.register(ExportStatementHandler())
        self.registry.register(ReturnStatementHandler())
        self.registry.register(ExpressionStatementHandler())

    def execute_statements(
        self,
        statements: list[tuple[CodeStatement, ...]],
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a list of code statements.

        Args:
            statements: List of statement tuples to execute
            context: Execution context

        Returns:
            Optional return value from last statement
        """
        # Import here to avoid circular dependency
        from gulfofmexico.interpreter import determine_statement_type

        result = None

        for statement_tuple in statements:
            # Determine actual statement type
            statement = determine_statement_type(statement_tuple, context.namespaces)

            if statement is None:
                continue

            # Update current line for error reporting
            if hasattr(statement, "name") and hasattr(statement.name, "line"):
                context.update_line(statement.name.line)
            elif hasattr(statement, "keyword") and hasattr(statement.keyword, "line"):
                context.update_line(statement.keyword.line)

            # Try to execute using handler
            try:
                result = self.registry.execute_statement(statement, context)

                # If statement returned a value, propagate it
                if result is not None:
                    return result

            except ValueError:
                # No handler registered - fall back to legacy interpreter
                # This allows gradual migration
                result = self._execute_legacy(statement, context)

                if result is not None:
                    return result

        return result

    def _execute_legacy(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute statement using legacy interpreter.

        This is a compatibility shim during migration. As handlers are
        implemented, this will handle fewer statement types.

        Args:
            statement: Statement to execute
            context: Execution context

        Returns:
            Optional return value
        """
        # Import here to avoid circular dependency
        from gulfofmexico.interpreter import (
            interpret_code_statements,
        )

        # Use original interpreter for non-migrated statements
        # This maintains backward compatibility during migration
        return interpret_code_statements(
            [(statement,)],
            context.namespaces,
            context.async_statements,
            context.when_watchers,
            context.importable_names,
            context.exported_names,
        )

    def get_stats(self) -> dict:
        """Get performance statistics.

        Returns:
            Dictionary with performance stats
        """
        return {
            "expression_cache": self.evaluator.get_stats(),
            "registered_handlers": len(self.registry._handlers),
        }
