"""
Return Statement Handler for Gulf of Mexico Interpreter.

Handles return statements from functions, which are the primary mechanism
for functions to yield values back to their callers.

Supports:
- Return from synchronous functions
- Return from async functions (via promises)
- Return value evaluation
- Error handling for invalid return contexts
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from gulfofmexico.base import StatementHandler
from gulfofmexico.builtin import GulfOfMexicoPromise, GulfOfMexicoValue
from gulfofmexico.context import ExecutionContext
from gulfofmexico.processor.syntax_tree import ReturnStatement, Token


logger = logging.getLogger(__name__)


class ReturnStatementHandler(StatementHandler):
    """Handler for return statements in Gulf of Mexico.
    
    Return statements serve two purposes:
    1. In synchronous functions: Return value from function via promise resolution
    2. In async functions: Scheduled as part of async execution
    
    The handler coordinates promise resolution for async functions to work
    correctly with the execution model.
    """

    def __init__(self):
        """Initialize return statement handler."""
        super().__init__()
        self.return_count = 0
        self.builtin_imports = {}  # Imported from interpreter scope

    def set_interpreter_imports(self, imports: Dict[str, Callable]) -> None:
        """Set references to interpreter functions needed for return evaluation.
        
        Required imports:
        - evaluate_expression: Evaluate the return value expression
        - raise_error_at_line: Report errors in invalid contexts
        """
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: ReturnStatement) -> bool:
        """Return statement handler handles all return statements."""
        return isinstance(stmt, ReturnStatement)

    def execute(
        self,
        stmt: ReturnStatement,
        context: ExecutionContext,
        promise: Optional[GulfOfMexicoPromise] = None,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute return statement and resolve promise.
        
        Args:
            stmt: Return statement to execute
            context: Execution context with namespaces and state
            promise: Promise to resolve with return value (for async functions)
            
        Returns:
            The return value that was resolved to the promise
            
        Raises:
            RuntimeError: If promise is None (invalid return context)
        """
        self.return_count += 1

        if context.debug_level >= 2:
            logger.info(f"[Return] Executing return statement (#{self.return_count})")

        # Evaluate the return expression
        return_value = self._evaluate_return_value(stmt, context)

        if context.debug_level >= 3:
            logger.debug(f"[Return] Return value: {return_value}")

        # Resolve the promise with the return value
        return self._resolve_promise(return_value, promise, context)

    def _evaluate_return_value(
        self,
        stmt: ReturnStatement,
        context: ExecutionContext,
    ) -> GulfOfMexicoValue:
        """Evaluate the expression being returned.
        
        Args:
            stmt: Return statement with expression
            context: Execution context
            
        Returns:
            Evaluated return value
        """
        evaluate_expr = self.builtin_imports.get("evaluate_expression")
        if not evaluate_expr:
            raise RuntimeError("Missing evaluate_expression import")

        return_value = evaluate_expr(
            stmt.expression,
            context.namespaces,
            context.async_statements,
            context.when_statement_watchers,
        )

        if context.debug_level >= 3:
            logger.debug(f"[Return] Evaluated expression to: {type(return_value).__name__}")

        return return_value

    def _resolve_promise(
        self,
        return_value: GulfOfMexicoValue,
        promise: Optional[GulfOfMexicoPromise],
        context: ExecutionContext,
    ) -> GulfOfMexicoValue:
        """Resolve the function's promise with the return value.
        
        For async functions, the promise object holds the return value that
        will be made available to the caller after the function completes.
        
        Args:
            return_value: The value to return
            promise: Promise to resolve (None for non-async context)
            context: Execution context (for error reporting)
            
        Returns:
            The return value
            
        Raises:
            RuntimeError: If promise is None (invalid return context)
        """
        if promise is None:
            raise_error = self.builtin_imports.get("raise_error_at_line")
            if raise_error:
                raise_error(
                    context.filename,
                    context.code,
                    context.current_line,
                    "Return statement used outside of function context.",
                )
            raise RuntimeError("Return statement outside function context")

        # Set promise value to the evaluated return value
        promise.value = return_value

        if context.debug_level >= 2:
            logger.info(f"[Return] Promise resolved with value: {type(return_value).__name__}")

        return return_value

    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics.
        
        Returns:
            Dictionary with:
            - total_returns: Total return statements executed
        """
        return {
            "total_returns": self.return_count,
        }

    def get_debug_info(self) -> str:
        """Get debug information about return statement handler state.
        
        Returns:
            Formatted debug information string
        """
        return (
            f"ReturnStatementHandler Debug Info:\n"
            f"  Total Return Statements: {self.return_count}\n"
        )


def create_return_handler() -> ReturnStatementHandler:
    """Factory function to create a configured return statement handler.
    
    Returns:
        Initialized ReturnStatementHandler ready for use
    """
    return ReturnStatementHandler()
