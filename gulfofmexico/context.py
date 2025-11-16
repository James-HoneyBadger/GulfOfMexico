"""Execution context for the Gulf of Mexico interpreter.

This module provides ExecutionContext and InterpreterConfig classes that can be
used by both the production interpreter and experimental engine package.

Note: ExecutionContext is currently only used by the experimental engine in
gulfofmexico/engine/. The production interpreter in interpreter.py uses
module-level global variables instead.
"""

from dataclasses import dataclass, field
from typing import Optional
from gulfofmexico.builtin import GulfOfMexicoValue


# Type aliases for complex types
Namespace = dict[str, "Variable | Name"]  # noqa: F821
AsyncStatements = list[tuple[list, list[Namespace], int, int]]
WhenStatementWatchers = list[dict]


@dataclass
class ExecutionContext:
    """Encapsulates interpreter execution state.

    This class can be used to pass state through function calls instead of
    using global variables. Currently only used by the experimental engine
    in gulfofmexico/engine/. The production interpreter uses module-level
    globals in interpreter.py instead.

    Attributes:
        filename: Current file being executed
        code: Source code being executed
        namespaces: Stack of variable namespaces
        async_statements: Queue of async statement executions
        when_watchers: Watchers for reactive 'when' statements
        importable_names: Names exported from other files
        exported_names: Names exported from current file
        current_line: Current line number for error reporting
        deleted_values: Set of deleted value objects
    """

    filename: str
    code: str
    namespaces: list[Namespace]
    async_statements: AsyncStatements
    when_watchers: WhenStatementWatchers
    importable_names: dict[str, dict[str, GulfOfMexicoValue]]
    exported_names: list[tuple[str, str, GulfOfMexicoValue]]

    # Execution state
    current_line: int = 0
    deleted_values: set[GulfOfMexicoValue] = field(default_factory=set)

    # Performance caching (future enhancement)
    expression_cache: dict[int, GulfOfMexicoValue] = field(default_factory=dict)
    namespace_cache: dict[str, tuple[int, "Variable"]] = field(  # noqa: F821
        default_factory=dict
    )

    def clear_caches(self) -> None:
        """Clear all performance caches."""
        self.expression_cache.clear()
        self.namespace_cache.clear()

    def invalidate_namespace_cache(self, name: str) -> None:
        """Invalidate cache entry for a specific variable name.

        Args:
            name: Variable name to invalidate
        """
        self.namespace_cache.pop(name, None)

    def update_line(self, line: int) -> None:
        """Update current line number for error reporting.

        Args:
            line: New line number
        """
        self.current_line = line

    def mark_deleted(self, value: GulfOfMexicoValue) -> None:
        """Mark a value as deleted.

        Args:
            value: Value to mark as deleted
        """
        self.deleted_values.add(value)

    def is_deleted(self, value: GulfOfMexicoValue) -> bool:
        """Check if a value has been deleted.

        Args:
            value: Value to check

        Returns:
            True if value has been deleted
        """
        return value in self.deleted_values


@dataclass
class InterpreterConfig:
    """Configuration options for the interpreter.

    Attributes:
        enable_expression_cache: Enable caching of pure expressions
        enable_namespace_cache: Enable caching of namespace lookups
        max_recursion_depth: Maximum recursion depth
        enable_github_globals: Enable GitHub global variable storage
        debug_mode: Enable debug output
    """

    enable_expression_cache: bool = True
    enable_namespace_cache: bool = True
    max_recursion_depth: int = 100000
    enable_github_globals: bool = True
    debug_mode: bool = False
