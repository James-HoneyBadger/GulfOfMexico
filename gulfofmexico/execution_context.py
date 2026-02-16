"""
ExecutionContext - Unified Context for Statement Handlers

Replaces passing 10+ parameters through handler functions by encapsulating
all execution state in a single, coherent context object.

Before (Monolithic Pattern Matching):
    interpret_code_statements(
        statements,
        namespaces,
        async_statements,
        when_statement_watchers,
        importable_names,
        exported_names,
    )

After (Handler Pattern):
    handler.execute(statement, context)
    where context contains all of the above plus utilities
"""

from dataclasses import dataclass, field
from typing import Optional, Union
# Path removed - not used in this module

from gulfofmexico.builtin import (
    GulfOfMexicoValue,
    Name,
    Variable,
)
from gulfofmexico.processor.syntax_tree import CodeStatement


# Type aliases for clarity
Namespace = dict[str, Union[Variable, Name]]
AsyncStatements = list[
    tuple[
        list[tuple[CodeStatement, ...]],
        list[Namespace],
        int,
        Union[int],
    ]
]
ExportedNames = list[tuple[str, str, GulfOfMexicoValue]]


@dataclass
class ExecutionContext:
    """Complete execution context for statement handlers.

    This class encapsulates all state needed for executing statements,
    replacing the parameter explosion in the original monolithic design.

    Attributes:
        filename: Current file being interpreted
        code: Current code string being interpreted
        current_line: Current line number for error reporting

        Execution State:
        namespaces: Stack of variable namespaces
        async_statements: Queue of pending async tasks
        when_statement_watchers: Registry of when-statement watchers
        importable_names: Available imports by module
        exported_names: Exported names for import system

        Debugging:
        deleted_values: Set of values that have been deleted
        verbose: Enable verbose output
    """

    # File context
    filename: str
    code: str
    current_line: int = 0

    # Execution state
    namespaces: list[Namespace] = field(default_factory=list)
    async_statements: AsyncStatements = field(default_factory=list)
    when_statement_watchers: list = field(default_factory=list)

    # Import/export system
    importable_names: dict[str, dict[str, GulfOfMexicoValue]] = field(
        default_factory=dict
    )
    exported_names: ExportedNames = field(default_factory=list)

    # Debugging/tracking
    deleted_values: set[GulfOfMexicoValue] = field(default_factory=set)
    verbose: bool = False
    _scope_depth: int = 0

    # Helper: name watchers for 'next' keyword
    name_watchers: dict = field(default_factory=dict)

    # Helper: active event listeners
    after_listeners: list = field(default_factory=list)

    def get_variable(self, name: str) -> Optional[Union[Variable, Name]]:
        """Get a variable from the namespace stack.

        Searches from most local (top) to global (bottom) scope.

        Args:
            name: Variable name (supports dotted access like obj.field)

        Returns:
            The Variable or Name, or None if not found

        Example:
            >>> context.get_variable('x')
            Variable('x', ...)
            >>> context.get_variable('obj.field')
            Name('field', ...)
        """
        # Fast path for simple names
        if "." not in name:
            for namespace in reversed(self.namespaces):
                if name in namespace:
                    return namespace[name]
            return None

        # Slow path for dotted names
        parts = name.split(".")
        base_entry = None

        for namespace in reversed(self.namespaces):
            if parts[0] in namespace:
                base_entry = namespace[parts[0]]
                break

        if base_entry is None:
            return None

        # Walk nested namespaces
        from gulfofmexico.builtin import GulfOfMexicoNamespaceable

        current_value = base_entry.value  # type: ignore[attr-defined]
        current_entry = base_entry

        for seg in parts[1:]:
            if not isinstance(current_value, GulfOfMexicoNamespaceable):
                return None
            if seg not in current_value.namespace:
                return None
            current_entry = current_value.namespace[seg]
            current_value = current_entry.value  # type: ignore[attr-defined]

        return current_entry

    def set_variable(
        self, name: str, value: GulfOfMexicoValue, confidence: int = 0
    ) -> None:
        """Set a variable in the current scope.

        Args:
            name: Variable name
            value: Value to set
            confidence: Confidence level (0-100)
        """
        if not self.namespaces:
            raise ValueError("Cannot set variable with empty namespace stack")

        # For existing variables, add a new lifetime
        if existing := self.get_variable(name):
            if isinstance(existing, Variable):
                existing.add_lifetime(value, confidence, 100000000000, True, True)
            elif isinstance(existing, Name):
                # Don't overwrite keyword/const Names
                from gulfofmexico.builtin import GulfOfMexicoKeyword
                if isinstance(existing.value, GulfOfMexicoKeyword):
                    raise ValueError(f"Cannot overwrite keyword '{name}'")
                # Create a proper Variable to replace the Name
                var = Variable(name, [], [])
                var.add_lifetime(value, confidence, 100000000000, True, True)
                # Find and replace in the correct namespace
                for ns in reversed(self.namespaces):
                    if name in ns:
                        ns[name] = var
                        break
        else:
            # New variable in current scope
            var = Variable(name, [], [])
            var.add_lifetime(value, confidence, 100000000000, True, True)
            self.namespaces[-1][name] = var

    def push_scope(self) -> None:
        """Push a new variable scope onto the stack.

        Used when entering blocks (functions, conditionals, loops).
        """
        self.namespaces.append({})
        self.when_statement_watchers.append({})
        self._scope_depth += 1

    def pop_scope(self) -> None:
        """Pop the current variable scope.

        Returns to the parent scope.

        Raises:
            ValueError: If trying to pop global scope
        """
        if len(self.namespaces) <= 1:
            raise ValueError("Cannot pop global scope")

        self.namespaces.pop()
        self.when_statement_watchers.pop()
        self._scope_depth -= 1

    def get_current_namespace(self) -> Namespace:
        """Get the current (most local) namespace.

        Returns:
            The topmost namespace dict
        """
        if not self.namespaces:
            raise ValueError("No namespace available")
        return self.namespaces[-1]

    def get_global_namespace(self) -> Namespace:
        """Get the global (bottom-most) namespace.

        Returns:
            The bottom-most namespace dict
        """
        if not self.namespaces:
            raise ValueError("No namespace available")
        return self.namespaces[0]

    def delete_variable(self, name: str) -> bool:
        """Delete a variable from the namespace.

        Args:
            name: Variable name

        Returns:
            True if variable was deleted, False if not found
        """
        for namespace in reversed(self.namespaces):
            if name in namespace:
                var_or_name = namespace[name]
                # Mark value as deleted if it's a variable
                if isinstance(var_or_name, Variable):
                    self.deleted_values.add(var_or_name.value)
                del namespace[name]
                return True
        return False

    def clone_for_scope(self) -> "ExecutionContext":
        """Create a context clone for a new scope.

        Useful for when-statements and other scoped executions
        that need a snapshot of the current context.

        Returns:
            New ExecutionContext with shallow-copied namespaces
        """
        from copy import copy

        ctx = copy(self)
        # Don't share mutable collections
        ctx.namespaces = [ns.copy() for ns in self.namespaces]
        ctx.async_statements = self.async_statements.copy()
        ctx.when_statement_watchers = [w.copy() for w in self.when_statement_watchers]
        ctx._scope_depth = self._scope_depth  # pylint: disable=protected-access

        return ctx

    def get_debug_info(self) -> str:
        """Get detailed debug information about the current state.

        Returns:
            Formatted debug string with context information
        """
        lines = [
            "=== ExecutionContext Debug Info ===",
            f"File: {self.filename}",
            f"Line: {self.current_line}",
            f"Scope depth: {self._scope_depth}",
            "",
            "Namespace Stack:",
        ]

        for i, ns in enumerate(self.namespaces):
            depth = i
            indent = "  " * depth
            lines.append(f"{indent}[{i}] {len(ns)} variables")
            # Show first few variables in each scope
            for name in list(ns.keys())[:3]:
                lines.append(f"{indent}  - {name}")
            if len(ns) > 3:
                lines.append(f"{indent}  ... and {len(ns) - 3} more")

        lines.extend(
            [
                "",
                "Async Tasks:",
                f"  Pending: {len(self.async_statements)}",
                "",
                "When-Statement Watchers:",
                f"  Total watchers: {sum(len(w) for w in self.when_statement_watchers)}",
                "",
                "Imports/Exports:",
                f"  Importable modules: {len(self.importable_names)}",
                f"  Exported names: {len(self.exported_names)}",
            ]
        )

        if self.deleted_values:
            lines.extend(
                ["", "Deleted Values:", f"  Count: {len(self.deleted_values)}"]
            )

        return "\n".join(lines)

    def print_debug_info(self) -> None:
        """Print debug information to stdout."""
        print(self.get_debug_info())

    @classmethod
    def create_root(cls, filename: str = "", code: str = "") -> "ExecutionContext":
        """Create a root execution context with global scope.

        Useful for initializing the interpreter.

        Args:
            filename: File being interpreted
            code: Code being interpreted

        Returns:
            New ExecutionContext with global namespace ready
        """
        ctx = cls(filename=filename, code=code)
        ctx.push_scope()  # Create global namespace
        return ctx

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"ExecutionContext(file={self.filename!r}, "
            f"line={self.current_line}, "
            f"scopes={len(self.namespaces)}, "
            f"async={len(self.async_statements)})"
        )
