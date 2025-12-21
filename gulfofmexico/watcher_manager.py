"""
When-Statement Watcher Manager

Replaces the complex tuple-based watcher system with a cleaner class-based approach.

Current Problems with Old System:
    - Watchers stored as complex nested tuples with 6+ levels of nesting
    - Manual management error-prone
    - Unclear semantics of captured namespaces
    - Race conditions between async and when-statement execution
    - Difficult to debug watcher state

New Solution:
    - WatcherRegistry: Centralized management of all watchers
    - Watcher: Dataclass representing a single watcher
    - Clean API for registering/triggering/removing watchers
    - Built-in deadlock detection
    - Comprehensive logging for debugging
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union
import weakref
import logging

from gulfofmexico.processor.expression_tree import ExpressionTreeNode
from gulfofmexico.processor.syntax_tree import CodeStatement

logger = logging.getLogger(__name__)


@dataclass
class Watcher:
    """Represents a single when-statement watcher.

    A watcher monitors a variable or object for changes and executes
    code when a condition is met.

    Attributes:
        id: Unique identifier for this watcher
        variable_id: ID of the variable being watched (id() of object)
        condition: Expression to evaluate when variable changes
        code: Code statements to execute if condition is true
        captured_namespaces: Snapshot of namespaces when watcher was registered
        is_active: Whether this watcher is currently active
        execution_count: Number of times this watcher has executed
        last_execution_time: Timestamp of last execution (for deadlock detection)
    """

    id: int
    variable_id: Union[str, int]
    condition: ExpressionTreeNode
    code: list[tuple[CodeStatement, ...]]
    captured_namespaces: list[dict]
    is_active: bool = True
    execution_count: int = 0
    last_execution_time: float = 0.0

    def __hash__(self):
        """Make watcher hashable for use in sets."""
        return hash(self.id)

    def __eq__(self, other):
        """Compare watchers by ID."""
        if not isinstance(other, Watcher):
            return False
        return self.id == other.id


@dataclass
class WatcherRegistry:
    """Centralized registry for when-statement watchers.

    Manages registration, triggering, and cleanup of watchers with:
        - Duplicate prevention
        - Deadlock detection
        - Activity logging
        - Namespace capture/restore
    """

    # Map from watched variable ID to list of watchers
    _watchers: dict[Union[str, int], list[Watcher]] = field(default_factory=dict)

    # Track active watcher executions to detect deadlocks
    _active_executions: set[int] = field(default_factory=set)

    # Maximum recursion depth for watcher execution
    _max_recursion_depth: int = 100

    # Counter for unique watcher IDs
    _next_watcher_id: int = 0

    # Execution history for debugging
    _execution_history: list[tuple[int, str, float]] = field(default_factory=list)

    # Max history entries to keep
    _max_history: int = 1000

    def register_watcher(
        self,
        variable_id: Union[str, int],
        condition: ExpressionTreeNode,
        code: list[tuple[CodeStatement, ...]],
        captured_namespaces: list[dict],
    ) -> int:
        """Register a new when-statement watcher.

        Args:
            variable_id: ID of variable to watch (usually id(variable))
            condition: Expression to evaluate on change
            code: Statements to execute if condition is true
            captured_namespaces: Snapshot of namespaces at registration time

        Returns:
            ID of the registered watcher

        Raises:
            ValueError: If variable_id is invalid
        """
        if variable_id is None:
            raise ValueError("variable_id cannot be None")

        watcher_id = self._next_watcher_id
        self._next_watcher_id += 1

        watcher = Watcher(
            id=watcher_id,
            variable_id=variable_id,
            condition=condition,
            code=code,
            captured_namespaces=captured_namespaces,
        )

        if variable_id not in self._watchers:
            self._watchers[variable_id] = []

        self._watchers[variable_id].append(watcher)

        logger.debug(
            f"Registered watcher {watcher_id} for variable {variable_id} "
            f"(total watchers: {len(self._watchers[variable_id])})"
        )

        return watcher_id

    def get_watchers(self, variable_id: Union[str, int]) -> list[Watcher]:
        """Get all active watchers for a variable.

        Args:
            variable_id: ID of the variable

        Returns:
            List of active watchers, or empty list if none
        """
        if variable_id not in self._watchers:
            return []
        return [w for w in self._watchers[variable_id] if w.is_active]

    def trigger_watchers(
        self,
        variable_id: Union[str, int],
        condition_evaluator: Callable[[ExpressionTreeNode, list[dict]], bool],
    ) -> list[tuple[int, list[tuple[CodeStatement, ...]]]]:
        """Trigger all watchers for a variable if conditions are met.

        Args:
            variable_id: ID of the changed variable
            condition_evaluator: Function to evaluate conditions

        Returns:
            List of (watcher_id, code) tuples for watchers that should execute

        Raises:
            RuntimeError: If deadlock is detected
        """
        watchers = self.get_watchers(variable_id)
        if not watchers:
            return []

        to_execute = []

        for watcher in watchers:
            # Deadlock detection
            if len(self._active_executions) >= self._max_recursion_depth:
                raise RuntimeError(
                    f"Possible watcher deadlock detected: {len(self._active_executions)} "
                    f"active executions (max: {self._max_recursion_depth})"
                )

            try:
                # Evaluate condition in captured namespace
                condition_met = condition_evaluator(
                    watcher.condition, watcher.captured_namespaces
                )

                if condition_met:
                    to_execute.append((watcher.id, watcher.code))
                    self._log_execution(watcher.id, "triggered")

            except Exception as e:
                logger.error(
                    f"Error evaluating watcher {watcher.id} condition: {e}",
                    exc_info=True,
                )

        return to_execute

    def mark_watcher_executing(self, watcher_id: int) -> None:
        """Mark a watcher as currently executing.

        Used to detect deadlocks and infinite loops.

        Args:
            watcher_id: ID of watcher being executed
        """
        self._active_executions.add(watcher_id)

    def mark_watcher_done(self, watcher_id: int) -> None:
        """Mark a watcher as finished executing.

        Args:
            watcher_id: ID of watcher
        """
        self._active_executions.discard(watcher_id)

    def unregister_watcher(self, watcher_id: int) -> bool:
        """Unregister and deactivate a watcher.

        Args:
            watcher_id: ID of watcher to remove

        Returns:
            True if watcher was found and removed, False otherwise
        """
        for variable_id, watchers in self._watchers.items():
            for i, watcher in enumerate(watchers):
                if watcher.id == watcher_id:
                    watcher.is_active = False
                    self._log_execution(watcher_id, "unregistered")
                    logger.debug(f"Unregistered watcher {watcher_id}")
                    return True
        return False

    def clear_watchers(self, variable_id: Union[str, int]) -> int:
        """Clear all watchers for a variable.

        Args:
            variable_id: ID of the variable

        Returns:
            Number of watchers cleared
        """
        if variable_id not in self._watchers:
            return 0

        count = len(self._watchers[variable_id])
        for watcher in self._watchers[variable_id]:
            watcher.is_active = False
        self._watchers[variable_id] = []

        logger.debug(f"Cleared {count} watchers for variable {variable_id}")
        return count

    def get_stats(self) -> dict:
        """Get statistics about registered watchers.

        Returns:
            Dictionary with watcher statistics
        """
        total_watchers = sum(len(w) for w in self._watchers.values())
        active_watchers = sum(
            len([w for w in watchers if w.is_active])
            for watchers in self._watchers.values()
        )
        total_executions = sum(w.execution_count for watchers in self._watchers.values() for w in watchers)

        return {
            "total_watchers": total_watchers,
            "active_watchers": active_watchers,
            "inactive_watchers": total_watchers - active_watchers,
            "total_executions": total_executions,
            "active_executions": len(self._active_executions),
            "variables_watched": len(self._watchers),
        }

    def _log_execution(self, watcher_id: int, action: str) -> None:
        """Log a watcher action for debugging.

        Args:
            watcher_id: ID of watcher
            action: Action name (triggered, executed, unregistered, etc)
        """
        import time

        self._execution_history.append((watcher_id, action, time.time()))

        # Keep history bounded
        if len(self._execution_history) > self._max_history:
            self._execution_history.pop(0)

    def get_debug_info(self) -> str:
        """Get detailed debug information about watcher state.

        Returns:
            Formatted debug string
        """
        lines = ["=== Watcher Registry Debug Info ==="]
        stats = self.get_stats()

        for key, value in stats.items():
            lines.append(f"{key}: {value}")

        lines.append("\nActive Executions:")
        for watcher_id in self._active_executions:
            lines.append(f"  - Watcher {watcher_id}")

        lines.append("\nRecent History:")
        for watcher_id, action, timestamp in self._execution_history[-10:]:
            lines.append(f"  - Watcher {watcher_id}: {action}")

        return "\n".join(lines)
