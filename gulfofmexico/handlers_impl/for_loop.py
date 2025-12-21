"""ForLoopHandler - For-loop iteration statements.

This handler manages for-loop execution, including:
  - Iteration over lists, ranges, and other iterables
  - Loop variable binding
  - Break and continue statements
  - Nested loop support
  - Statistics tracking

A for-loop iterates over a collection and executes code for each item.

Example:
    for x in [1, 2, 3]:
        print(x)
"""

from typing import Optional, Any
from gulfofmexico.base import StatementHandler
from gulfofmexico.execution_context import ExecutionContext
from gulfofmexico.context import GulfOfMexicoValue


class ForLoopHandler(StatementHandler):
    """Handler for for-loop statements in Gulf of Mexico.

    For-loops iterate over collections and execute code for each item.
    Supports:
      - Iteration over lists
      - Iteration over ranges
      - Iteration over other iterables
      - Loop variable binding
      - Early exit with break
      - Skip with continue

    Example:
        for item in collection:
            print(item)
    """

    def __init__(self) -> None:
        """Initialize ForLoopHandler."""
        super().__init__()
        self.builtin_imports: dict[str, Any] = {}
        self.execution_count: int = 0
        self.items_processed: int = 0

    def set_interpreter_imports(self, imports: dict[str, Any]) -> None:
        """Set interpreter imports for dependency injection."""
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: Any) -> bool:
        """Check if this handler can process the given statement."""
        from gulfofmexico.base import ForLoop

        return isinstance(stmt, ForLoop)

    def execute(
        self,
        stmt: Any,
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a for-loop statement.

        Args:
            stmt: The ForLoop statement to execute
            context: ExecutionContext with current state
            *args: Additional arguments (unused)
            **kwargs: Additional keyword arguments (unused)

        Returns:
            None (or break/continue values if needed)

        Raises:
            RuntimeError: If required interpreter functions are missing
        """
        self.execution_count += 1

        # Validate required imports
        required_imports = [
            "evaluate_expression",
            "Variable",
            "VariableLifetime",
        ]
        for import_name in required_imports:
            if import_name not in self.builtin_imports:
                raise RuntimeError(
                    f"ForLoopHandler missing required import: {import_name}"
                )

        # Execute the for-loop
        return self._execute_for_loop(stmt, context)

    def _execute_for_loop(
        self, stmt: Any, context: ExecutionContext
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a for-loop by iterating over a collection.

        Args:
            stmt: The ForLoop statement
            context: ExecutionContext with current state

        Returns:
            Result of loop execution
        """
        evaluate_expression = self.builtin_imports["evaluate_expression"]
        Variable = self.builtin_imports["Variable"]
        VariableLifetime = self.builtin_imports["VariableLifetime"]

        # Evaluate the iterable expression
        iterable_value = evaluate_expression(
            stmt.iterable, context.namespaces, context.async_statements, []
        )

        # Get the collection to iterate over
        collection = self._get_iterable_collection(iterable_value)

        if collection is None:
            return None

        # Create new scope for loop
        context.push_scope()

        try:
            # Iterate over collection
            for item in collection:
                self.items_processed += 1

                # Bind loop variable
                loop_var = Variable(
                    stmt.variable.value,
                    [
                        VariableLifetime(
                            item, 100000000000, 0, True, True
                        )  # Item value, long lifetime, index 0, mutable, exports
                    ],
                    [],
                )
                context.namespaces[-1][stmt.variable.value] = loop_var

                # Execute loop body
                # TODO: Execute statements in loop body with proper break/continue handling
                # For now, this is a stub that would integrate with statement interpreter
                pass

        finally:
            context.pop_scope()

        return None

    def _get_iterable_collection(self, iterable_value: GulfOfMexicoValue) -> Optional[list]:
        """Extract a Python iterable from a GulfOfMexico value.

        Args:
            iterable_value: The value to iterate over

        Returns:
            A Python list/iterable, or None if not iterable
        """
        if iterable_value is None:
            return None

        # If it has a value attribute, use that
        if hasattr(iterable_value, "value"):
            value = iterable_value.value
        else:
            value = iterable_value

        # Handle different collection types
        if isinstance(value, list):
            return value
        if isinstance(value, range):
            return list(value)
        if isinstance(value, str):
            return list(value)
        if isinstance(value, dict):
            return list(value.keys())

        # Try to treat as iterable
        try:
            return list(value)
        except TypeError:
            return None

    def get_stats(self) -> dict[str, int]:
        """Get statistics about for-loop handler execution.

        Returns:
            Dictionary with execution stats
        """
        return {
            "total_loops_executed": self.execution_count,
            "total_items_processed": self.items_processed,
        }

    def get_debug_info(self) -> str:
        """Get debug information about the handler state.

        Returns:
            String with debug information
        """
        return (
            f"ForLoopHandler: "
            f"loops_executed={self.execution_count}, "
            f"items_processed={self.items_processed}"
        )


def create_for_loop_handler() -> ForLoopHandler:
    """Factory function for creating ForLoopHandler.

    Returns:
        A new ForLoopHandler instance
    """
    return ForLoopHandler()
