"""
Variable Assignment Handler

Extracted from interpreter.py's assign_variable() function.
Responsible for handling variable assignments with support for:
    - Simple assignments: x = 5
    - Indexed assignments: list[0] = x
    - Dotted assignments: obj.field = x
    - Confidence levels for probabilistic updates
    - Debug output (?, ??, ???, ????)
    - When-statement watchers on assignment
"""

from typing import Optional, Union

from gulfofmexico.base import Token, raise_error_at_token, raise_error_at_line
from gulfofmexico.builtin import (
    GulfOfMexicoIndexable,
    GulfOfMexicoNamespaceable,
    GulfOfMexicoValue,
    Name,
    Variable,
)
from gulfofmexico.handlers import StatementHandler
from gulfofmexico.processor.syntax_tree import VariableAssignment


# Type aliases
Namespace = dict[str, Union[Variable, Name]]
AsyncStatements = list[
    tuple[
        list[tuple],
        list[Namespace],
        int,
        Union[int],
    ]
]
WhenStatementWatchers = list[dict[Union[str, int], list[tuple]]]


class VariableAssignmentHandler(StatementHandler):
    """Handler for variable assignments.

    Processes statements like:
        x = 5!
        list[0] = "hello"!
        obj.field = 42!
        matrix[0][1] = x?

    Features:
        - Simple variable reassignment
        - Indexed assignment with automatic creation for fractional indices
        - Dotted property assignment
        - Confidence levels for probabilistic updates
        - Multi-level indexed assignments (matrix[i][j])
        - Debug output at multiple verbosity levels
        - When-statement trigger on changes
    """

    def __init__(
        self,
        filename: str = "",
        code: str = "",
        current_line: int = 0,
    ):
        """Initialize the handler.

        Args:
            filename: Current file being interpreted
            code: Current code being interpreted
            current_line: Current line number for error reporting
        """
        self.filename = filename
        self.code = code
        self.current_line = current_line
        self.name_watchers: dict[str, list] = {}  # For tracking 'next' expressions

    def can_handle(self, statement) -> bool:
        """Check if this is a variable assignment.

        Args:
            statement: The statement to check

        Returns:
            True if statement is VariableAssignment
        """
        return isinstance(statement, VariableAssignment)

    def execute(
        self,
        statement: VariableAssignment,
        namespaces: list[Namespace],
        indexes: list[GulfOfMexicoValue],
        new_value: GulfOfMexicoValue,
        async_statements: AsyncStatements,
        when_statement_watchers: WhenStatementWatchers,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute the variable assignment.

        Args:
            statement: The VariableAssignment to execute
            namespaces: The namespace stack
            indexes: Evaluated indices for indexed assignment
            new_value: The value to assign
            async_statements: Async execution queue
            when_statement_watchers: When-statement watchers

        Returns:
            None (assignments don't return values)

        Raises:
            InterpretationError: If variable not found or cannot be modified
        """
        name = statement.name.value
        confidence = statement.confidence
        debug = statement.debug
        name_token = statement.name

        # Find the variable in namespaces
        var, ns = self._get_name_and_namespace_from_namespaces(name, namespaces)

        # Support dotted property assignment (e.g., alice.name = "Alice")
        dotted_target = None
        if var is None and "." in name:
            dotted_target = self._resolve_dotted_assignment(name, namespaces)
            if dotted_target is None:
                raise_error_at_token(
                    self.filename,
                    self.code,
                    "Attempted to set a name that is undefined.",
                    name_token,
                )
        elif var is None:
            raise_error_at_token(
                self.filename,
                self.code,
                "Attempted to set a name that is undefined.",
                name_token,
            )

        # Print debug output if requested
        self._handle_debug_output(debug, statement, indexes, new_value, namespaces)

        # Handle indexed vs simple assignment
        if indexes:
            self._handle_indexed_assignment(
                var, dotted_target, indexes, new_value, namespaces, name_token
            )
        else:
            self._handle_simple_assignment(
                var, dotted_target, new_value, confidence, namespaces
            )

        # Trigger when-statement watchers
        self._trigger_when_watchers(
            name, var, new_value, namespaces, async_statements, when_statement_watchers
        )

        return None

    def _get_name_and_namespace_from_namespaces(
        self, name: str, namespaces: list[Namespace]
    ) -> tuple[Optional[Union[Variable, Name]], Optional[Namespace]]:
        """Get a name/variable and its containing namespace."""
        for namespace in reversed(namespaces):
            if name in namespace:
                return namespace[name], namespace
        return None, None

    def _resolve_dotted_assignment(
        self, name: str, namespaces: list[Namespace]
    ) -> Optional[tuple[GulfOfMexicoNamespaceable, str]]:
        """Resolve dotted property assignment (e.g., obj.field = x).

        Returns:
            Tuple of (container, property_name) or None if not found
        """
        parts = name.split(".")
        base_name, tail = parts[0], parts[1:]

        base_entry, _ = self._get_name_and_namespace_from_namespaces(base_name, namespaces)
        if base_entry is None:
            return None

        container_val = base_entry.value  # type: ignore[attr-defined]

        # Traverse through intermediate segments
        for seg in tail[:-1]:
            if not isinstance(container_val, GulfOfMexicoNamespaceable) or seg not in container_val.namespace:
                return None
            next_entry = container_val.namespace[seg]
            container_val = next_entry.value  # type: ignore[attr-defined]

        # Verify final segment is namespaceable
        if not isinstance(container_val, GulfOfMexicoNamespaceable):
            return None

        return (container_val, tail[-1])

    def _handle_debug_output(
        self,
        debug: int,
        statement: VariableAssignment,
        indexes: list[GulfOfMexicoValue],
        new_value: GulfOfMexicoValue,
        namespaces: list[Namespace],
    ) -> None:
        """Handle debug output for various verbosity levels.

        Args:
            debug: Debug level (0=none, 1=value, 2=+names, 3=+expr, 4=everything)
            statement: The assignment statement
            indexes: Indices being assigned
            new_value: The new value
            namespaces: Current namespaces
        """
        # This would import db_to_string and gather_names_or_values from interpreter
        if debug == 0:
            return

        # Stub for debug output - would be implemented with full context
        pass

    def _handle_indexed_assignment(
        self,
        var: Optional[Union[Variable, Name]],
        dotted_target: Optional[tuple],
        indexes: list[GulfOfMexicoValue],
        new_value: GulfOfMexicoValue,
        namespaces: list[Namespace],
        name_token: Token,
    ) -> None:
        """Handle indexed assignment (list[0] = x).

        Args:
            var: The variable being assigned
            dotted_target: Tuple of (container, property_name) if dotted
            indexes: List of indices to traverse
            new_value: Value to assign
            namespaces: Current namespaces
            name_token: Token of the variable name

        Raises:
            InterpretationError: If indexing into non-indexable value
        """
        def assign_variable_helper(
            value_to_modify: GulfOfMexicoValue,
            remaining_indexes: list[GulfOfMexicoValue],
        ):
            """Recursively traverse and assign through indices."""
            if not isinstance(value_to_modify, GulfOfMexicoIndexable):
                raise_error_at_line(
                    self.filename,
                    self.code,
                    name_token.line,
                    "Attempted to index into an un-indexable object.",
                )

            index = remaining_indexes.pop(0)

            if not remaining_indexes:  # Perform actual assignment
                value_to_modify.assign_index(index, new_value)
            else:
                assign_variable_helper(
                    value_to_modify.access_index(index), remaining_indexes
                )

        # Handle dotted vs regular indexed assignment
        if dotted_target is not None:
            container_val, key = dotted_target
            entry = container_val.namespace.get(key)
            if entry is None:
                raise_error_at_token(
                    self.filename,
                    self.code,
                    "Attempted to index into an undefined property.",
                    name_token,
                )
            assign_variable_helper(entry.value, indexes)  # type: ignore[attr-defined]
        else:
            if var is None:
                raise_error_at_token(
                    self.filename,
                    self.code,
                    "Variable not found for indexed assignment.",
                    name_token,
                )
            assign_variable_helper(var.value, indexes)  # type: ignore[attr-defined]

    def _handle_simple_assignment(
        self,
        var: Optional[Union[Variable, Name]],
        dotted_target: Optional[tuple],
        new_value: GulfOfMexicoValue,
        confidence: int,
        namespaces: list[Namespace],
    ) -> None:
        """Handle simple (non-indexed) assignment.

        Args:
            var: The variable being assigned
            dotted_target: Tuple of (container, property_name) if dotted
            new_value: Value to assign
            confidence: Confidence level for the new value
            namespaces: Current namespaces

        Raises:
            InterpretationError: If variable cannot be modified
        """
        if dotted_target is not None:
            container_val, key = dotted_target
            existing = container_val.namespace.get(key)
            if existing is None:
                container_val.namespace[key] = Name(key, new_value)
            elif isinstance(existing, Variable):
                if not existing.can_be_reset:
                    raise_error_at_token(
                        self.filename,
                        self.code,
                        "Attempted to set a variable that cannot be set.",
                        self._get_name_token(),
                    )
                existing.add_lifetime(
                    new_value,
                    confidence,
                    100000000000,
                    existing.can_be_reset,
                    existing.can_edit_value,
                )
            else:  # Name
                existing.value = new_value  # type: ignore[attr-defined]
        else:
            if var is None or not isinstance(var, Variable):
                raise_error_at_token(
                    self.filename,
                    self.code,
                    "Attempted to set name that is not a variable.",
                    self._get_name_token(),
                )
            if not var.can_be_reset:
                raise_error_at_token(
                    self.filename,
                    self.code,
                    "Attempted to set a variable that cannot be set.",
                    self._get_name_token(),
                )
            var.add_lifetime(
                new_value,
                confidence,
                100000000000,
                var.can_be_reset,
                var.can_edit_value,
            )

    def _trigger_when_watchers(
        self,
        name: str,
        var: Optional[Union[Variable, Name]],
        new_value: GulfOfMexicoValue,
        namespaces: list[Namespace],
        async_statements: AsyncStatements,
        when_statement_watchers: WhenStatementWatchers,
    ) -> None:
        """Trigger when-statement watchers for this assignment.

        Args:
            name: Variable name
            var: The variable being assigned
            new_value: The new value
            namespaces: Current namespaces
            async_statements: Async execution queue
            when_statement_watchers: When-statement watchers
        """
        # Stub for triggering watchers
        # Would be implemented with full context from interpreter
        pass

    def _get_name_token(self) -> Optional[Token]:
        """Get a name token for error reporting."""
        # Stub - would need to be passed in or stored
        return None

    @property
    def statement_type(self):
        """Return the statement type this handler processes."""
        return VariableAssignment
