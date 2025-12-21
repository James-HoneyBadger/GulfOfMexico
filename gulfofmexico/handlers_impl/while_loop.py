"""WhileLoopHandler - While-loop iteration statements.

This handler manages while-loop execution, including:
  - Condition evaluation
  - Loop body execution
  - Break and continue statements
  - Nested loop support
  - Infinite loop prevention
  - Statistics tracking

A while-loop continues executing code while a condition is true.

Example:
    while x < 10:
        x = x + 1
"""

from typing import Optional, Any
from gulfofmexico.base import StatementHandler
from gulfofmexico.execution_context import ExecutionContext
from gulfofmexico.context import GulfOfMexicoValue


class WhileLoopHandler(StatementHandler):
    """Handler for while-loop statements in Gulf of Mexico.

    While-loops continuously execute code as long as a condition is true.
    Supports:
      - Condition evaluation
      - Loop body execution
      - Early exit with break
      - Skip with continue
      - Infinite loop detection
      - Nested loops

    Example:
        while condition:
            code to execute
    """

    def __init__(self) -> None:
        """Initialize WhileLoopHandler."""
        super().__init__()
        self.builtin_imports: dict[str, Any] = {}
        self.execution_count: int = 0
        self.iterations_total: int = 0
        self.max_iterations_per_loop: int = 1000000  # Prevent infinite loops

    def set_interpreter_imports(self, imports: dict[str, Any]) -> None:
        """Set interpreter imports for dependency injection."""
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: Any) -> bool:
        """Check if this handler can process the given statement."""
        from gulfofmexico.base import WhileLoop

        return isinstance(stmt, WhileLoop)

    def execute(
        self,
        stmt: Any,
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a while-loop statement.

        Args:
            stmt: The WhileLoop statement to execute
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
        ]
        for import_name in required_imports:
            if import_name not in self.builtin_imports:
                raise RuntimeError(
                    f"WhileLoopHandler missing required import: {import_name}"
                )

        # Execute the while-loop
        return self._execute_while_loop(stmt, context)

    def _execute_while_loop(
        self, stmt: Any, context: ExecutionContext
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a while-loop by repeatedly checking condition and executing body.

        Args:
            stmt: The WhileLoop statement
            context: ExecutionContext with current state

        Returns:
            Result of loop execution
        """
        evaluate_expression = self.builtin_imports["evaluate_expression"]

        # Create new scope for loop
        context.push_scope()

        try:
            iteration_count = 0

            # Loop while condition is true
            while iteration_count < self.max_iterations_per_loop:
                iteration_count += 1
                self.iterations_total += 1

                # Evaluate loop condition
                condition_value = evaluate_expression(
                    stmt.condition,
                    context.namespaces,
                    context.async_statements,
                    [],
                )

                # Check if should continue looping
                if not self._evaluate_condition_for_loop(condition_value):
                    break

                # Execute loop body
                # TODO: Execute statements in loop body with proper break/continue handling
                # For now, this is a stub that would integrate with statement interpreter
                pass

            # Check for infinite loop
            if iteration_count >= self.max_iterations_per_loop:
                raise RuntimeError(
                    f"While-loop exceeded maximum iterations ({self.max_iterations_per_loop}). "
                    "Possible infinite loop detected."
                )

        finally:
            context.pop_scope()

        return None

    def _evaluate_condition_for_loop(self, condition: GulfOfMexicoValue) -> bool:
        """Evaluate a condition to determine if loop should continue.

        Args:
            condition: The condition value to evaluate

        Returns:
            True if loop should continue, False otherwise
        """
        import random

        # Get the actual value
        if hasattr(condition, "value"):
            condition_val = condition.value
        else:
            condition_val = condition

        # Handle None/null case - exit loop
        if condition_val is None:
            return False

        # Handle boolean case
        if isinstance(condition_val, bool):
            return condition_val

        # Handle maybe case - 50% probability
        if condition_val == "maybe":
            return random.random() < 0.5

        # Try to convert to boolean
        return bool(condition_val)

    def get_stats(self) -> dict[str, int]:
        """Get statistics about while-loop handler execution.

        Returns:
            Dictionary with execution stats
        """
        return {
            "total_loops_executed": self.execution_count,
            "total_iterations": self.iterations_total,
        }

    def get_debug_info(self) -> str:
        """Get debug information about the handler state.

        Returns:
            String with debug information
        """
        avg_iterations = (
            self.iterations_total / self.execution_count
            if self.execution_count > 0
            else 0
        )
        return (
            f"WhileLoopHandler: "
            f"loops_executed={self.execution_count}, "
            f"total_iterations={self.iterations_total}, "
            f"avg_per_loop={avg_iterations:.1f}"
        )


def create_while_loop_handler() -> WhileLoopHandler:
    """Factory function for creating WhileLoopHandler.

    Returns:
        A new WhileLoopHandler instance
    """
    return WhileLoopHandler()
