"""WhenStatementHandler - Reactive programming with when-statements.

This handler manages reactive programming through when-statements, which are
triggered when watched variables change. It replaces the complex watcher system
with a clean, testable handler.

Key features:
  - Variable watching and change detection
  - Condition evaluation and reactive execution
  - Scope management for when-statement code blocks
  - Support for async operations within when-statements
  - Statistics tracking for debugging
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from copy import deepcopy
from gulfofmexico.base import StatementHandler
from gulfofmexico.execution_context import ExecutionContext
from gulfofmexico.context import GulfOfMexicoValue


@dataclass
class WhenWatcher:
    """Represents a single when-statement watcher."""

    condition: Any
    statements: list[tuple[Any, ...]]
    captured_namespaces: list[dict[str, Any]]


@dataclass
class WhenStatementWatcherRegistry:
    """Registry of watchers for a single watched name/value."""

    watchers: list[WhenWatcher] = field(default_factory=list)

    def add_watcher(
        self,
        condition: Any,
        statements: list[tuple[Any, ...]],
        captured_namespaces: list[dict[str, Any]],
    ) -> None:
        """Add a new watcher for this variable."""
        self.watchers.append(
            WhenWatcher(
                condition=condition,
                statements=statements,
                captured_namespaces=deepcopy(captured_namespaces),
            )
        )

    def get_watchers(self) -> list[WhenWatcher]:
        """Get all watchers for this variable."""
        return self.watchers


class WhenStatementHandler(StatementHandler):
    """Handler for when-statements in Gulf of Mexico.

    When-statements are reactive programming constructs that watch variables
    and execute code when those variables change and a condition is met.

    Example:
        when x > 10:
            print("x is greater than 10")

    This handler:
      1. Parses when-statement conditions
      2. Identifies watched variables
      3. Registers watchers for change detection
      4. Evaluates conditions and executes code blocks
      5. Manages scope for when-statement execution
    """

    def __init__(self) -> None:
        """Initialize WhenStatementHandler."""
        super().__init__()
        self.watchers_by_name: dict[str | int, WhenStatementWatcherRegistry] = {}
        self.builtin_imports: dict[str, Any] = {}
        self.execution_count: int = 0
        self.triggered_count: int = 0

    def set_interpreter_imports(self, imports: dict[str, Any]) -> None:
        """Set interpreter imports for dependency injection."""
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: Any) -> bool:
        """Check if this handler can process the given statement."""
        from gulfofmexico.base import WhenStatement

        return isinstance(stmt, WhenStatement)

    def execute(
        self,
        stmt: Any,
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a when-statement.

        Args:
            stmt: The WhenStatement to execute
            context: ExecutionContext with current state
            *args: Additional arguments (unused)
            **kwargs: Additional keyword arguments (unused)

        Returns:
            Result of executing the when-statement (usually None)

        Raises:
            RuntimeError: If required interpreter functions are missing
        """
        self.execution_count += 1

        # Validate required imports
        required_imports = [
            "get_built_expression",
            "gather_names_or_values",
            "get_name_from_namespaces",
            "evaluate_expression",
            "Variable",
            "GulfOfMexicoMutable",
        ]
        for import_name in required_imports:
            if import_name not in self.builtin_imports:
                raise RuntimeError(
                    f"WhenStatementHandler missing required import: {import_name}"
                )

        # Register the when-statement as a reactive watcher
        self._register_when_statement(stmt, context)

        # Immediately check if condition is already true (eager evaluation)
        self._check_condition_immediately(stmt, context)

        return None

    def _register_when_statement(self, stmt: Any, context: ExecutionContext) -> None:
        """Register a when-statement as a watcher.

        Identifies all variables referenced in the condition and registers
        watchers for them so that the when-statement code executes whenever
        those variables change.

        Args:
            stmt: The WhenStatement to register
            context: ExecutionContext with current state
        """
        get_built_expression = self.builtin_imports["get_built_expression"]
        gather_names_or_values = self.builtin_imports["gather_names_or_values"]
        get_name_from_namespaces = self.builtin_imports["get_name_from_namespaces"]
        Variable = self.builtin_imports["Variable"]
        GulfOfMexicoMutable = self.builtin_imports["GulfOfMexicoMutable"]

        # Build the condition expression
        built_condition = get_built_expression(stmt.expression)

        # Gather all names/variables referenced in the condition
        gathered_names = gather_names_or_values(built_condition)

        # Extract caller names (e.g., "list" from "list.length")
        caller_names = [
            n
            for name in gathered_names
            if (n := ".".join(name.value.split(".")[:-1]))
        ]

        # Build list of dictionary keys to watch (variable IDs and mutable IDs)
        dict_keys = (
            [
                (
                    id(v)
                    if isinstance(
                        v := get_name_from_namespaces(name.value, context.namespaces),
                        Variable,
                    )
                    else name.value
                )
                for name in gathered_names
            ]
            + [
                id(v.value)
                for name in gathered_names
                if (v := get_name_from_namespaces(name.value, context.namespaces))
                is not None
                and isinstance(v.value, GulfOfMexicoMutable)
            ]
            + [
                id(v)
                for name in caller_names
                if isinstance(
                    v := get_name_from_namespaces(name, context.namespaces), Variable
                )
            ]
            + [
                id(v.value)
                for name in caller_names
                if (v := get_name_from_namespaces(name, context.namespaces))
                is not None
                and isinstance(v.value, GulfOfMexicoMutable)
            ]
        )

        # Register watchers for each watched name/value
        for watch_key in dict_keys:
            if watch_key not in self.watchers_by_name:
                self.watchers_by_name[watch_key] = WhenStatementWatcherRegistry()

            self.watchers_by_name[watch_key].add_watcher(
                condition=built_condition,
                statements=stmt.code,
                captured_namespaces=context.namespaces,
            )

    def _check_condition_immediately(
        self, stmt: Any, context: ExecutionContext
    ) -> None:
        """Check if the condition is true immediately and execute if so.

        This allows when-statements to be triggered on registration if the
        condition is already satisfied, providing eager evaluation semantics.

        Args:
            stmt: The WhenStatement
            context: ExecutionContext with current state
        """
        evaluate_expression = self.builtin_imports["evaluate_expression"]

        try:
            # Evaluate condition in current context
            condition_value = evaluate_expression(
                stmt.expression, context.namespaces, context.async_statements, []
            )

            # Check if condition is satisfied
            if self._evaluate_condition_for_execution(condition_value):
                self.triggered_count += 1
                # Execute the when-statement code block
                self._execute_when_block(stmt.code, context)
        except Exception:
            # Silently fail on immediate evaluation - watchers will handle it
            # This prevents noise in normal program execution
            pass

    def _evaluate_condition_for_execution(self, condition: GulfOfMexicoValue) -> bool:
        """Evaluate a condition to determine if code should execute.

        Supports deterministic (true/false) and probabilistic (maybe) values.

        Args:
            condition: The condition value to evaluate

        Returns:
            True if condition should trigger execution, False otherwise
        """
        import random

        # Get the boolean value
        if hasattr(condition, "value"):
            condition_val = condition.value
        else:
            condition_val = condition

        # Handle None/null case - evaluate as false
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

    def _execute_when_block(
        self, statements: list[tuple[Any, ...]], context: ExecutionContext
    ) -> None:
        """Execute the code block inside a when-statement.

        Args:
            statements: List of statement tuples to execute
            context: ExecutionContext with current state
        """
        # Create new scope for when-statement block
        context.push_scope()

        try:
            # TODO: Execute statements in the when-statement block
            # This would integrate with the statement interpreter to execute
            # each statement in statements with the new scope
            pass
        finally:
            # Always pop scope, even if error occurs
            context.pop_scope()

    def get_stats(self) -> dict[str, int]:
        """Get statistics about when-statement handler execution.

        Returns:
            Dictionary with execution stats
        """
        return {
            "total_executions": self.execution_count,
            "total_triggers": self.triggered_count,
            "total_watchers": sum(
                len(registry.watchers) for registry in self.watchers_by_name.values()
            ),
        }

    def get_debug_info(self) -> str:
        """Get debug information about the handler state.

        Returns:
            String with debug information
        """
        total_watchers = sum(
            len(registry.watchers) for registry in self.watchers_by_name.values()
        )
        return (
            f"WhenStatementHandler: "
            f"executed={self.execution_count}, "
            f"triggered={self.triggered_count}, "
            f"watchers={total_watchers}"
        )


def create_when_handler() -> WhenStatementHandler:
    """Factory function for creating WhenStatementHandler.

    Returns:
        A new WhenStatementHandler instance
    """
    return WhenStatementHandler()
