"""
Variable Declaration Handler

Extracted from interpreter.py's declare_new_variable() function.
Responsible for handling variable declarations with support for:
    - const/var modifiers
    - Probabilistic values with confidence levels
    - Temporal and line-based lifetimes
    - Type annotations
    - Global immutable constants (const const const)
    - When-statement watchers
"""

from typing import Optional, Union

from gulfofmexico.base import Token, debug_print, raise_error_at_token
from gulfofmexico.builtin import (
    GulfOfMexicoBoolean,
    GulfOfMexicoMutable,
    GulfOfMexicoUndefined,
    GulfOfMexicoValue,
    Name,
    Variable,
    VariableLifetime,
)
from gulfofmexico.handlers import StatementHandler
from gulfofmexico.processor.syntax_tree import VariableDeclaration


# Type aliases
Namespace = dict[str, Union[Variable, Name]]
AsyncStatements = list[
    tuple[
        list[tuple],  # statements
        list[Namespace],  # namespaces
        int,  # index
        Union[int],  # direction
    ]
]
WhenStatementWatchers = list[dict[Union[str, int], list[tuple]]]


class VariableDeclarationHandler(StatementHandler):
    """Handler for variable declarations.

    Processes statements like:
        const x = 5!
        var y <10> = maybe!
        const const const z = important!

    Features:
        - Probabilistic values (confidence levels 0-100)
        - Temporal lifetimes: <seconds>
        - Line-based lifetimes: <lines>
        - Type annotations
        - Global constants that persist across sessions
    """

    def __init__(
        self,
        filename: str = "",
        code: str = "",
    ):
        """Initialize the handler.

        Args:
            filename: Current file being interpreted
            code: Current code being interpreted
        """
        self.filename = filename
        self.code = code

    def can_handle(self, statement) -> bool:
        """Check if this is a variable declaration.

        Args:
            statement: The statement to check

        Returns:
            True if statement is VariableDeclaration
        """
        return isinstance(statement, VariableDeclaration)

    def execute(
        self,
        statement: VariableDeclaration,
        namespaces: list[Namespace],
        value: GulfOfMexicoValue,
        async_statements: AsyncStatements,
        when_statement_watchers: WhenStatementWatchers,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute the variable declaration.

        Args:
            statement: The VariableDeclaration to execute
            namespaces: The namespace stack
            value: The value to assign
            async_statements: Async execution queue
            when_statement_watchers: When-statement watchers

        Returns:
            None (declarations don't return values)

        Raises:
            InterpretationError: If type annotation fails or invalid lifetime
        """
        name = statement.name.value
        confidence = statement.confidence
        lifetime = statement.lifetime

        # Determine variable properties based on modifiers
        can_be_reset = "var" in [mod.value for mod in statement.modifiers]
        can_edit_value = "const" not in [mod.value for mod in statement.modifiers]

        # Parse lifetime if provided
        duration = 100000000000  # default infinite
        is_temporal = False
        temporal_duration = 0.0

        if lifetime:
            try:
                if lifetime.startswith("<") and lifetime.endswith(">"):
                    # Temporal lifetime like <5.0>
                    temporal_duration = float(lifetime[1:-1])
                    duration = 100000000000  # still infinite lines
                    is_temporal = True
                else:
                    # Line-based lifetime
                    duration = int(lifetime)
            except ValueError:
                raise_error_at_token(
                    self.filename,
                    self.code,
                    f"Invalid lifetime specification: {lifetime}",
                    statement.name,
                )

        # Create the variable
        var = Variable(name, [], [])
        var.add_lifetime(
            value,
            confidence,
            duration,
            can_be_reset,
            can_edit_value,
            is_temporal=is_temporal,
            temporal_duration=temporal_duration,
        )

        # Add to namespace
        namespaces[-1][name] = var

        # Check type annotation if provided
        if statement.type_annotation:
            self._check_type_annotation(value, statement.type_annotation)

        # Check if this is a global immutable constant (const const const)
        is_triple_const = (
            len(statement.modifiers) == 3
            and all(mod.value == "const" for mod in statement.modifiers)
        )

        if is_triple_const:
            # Save as immutable global constant
            self._save_local_immutable_constant(name, value, confidence)

            # Try to create GitHub issue for global sharing
            try:
                self._open_global_variable_issue(name, value, confidence)
            except Exception:
                # GitHub storage failed, but local storage succeeded
                pass

        # Trigger when statement watchers for this new variable
        when_watchers = self._get_code_from_when_statement_watchers(
            id(var), when_statement_watchers
        )
        for when_watcher in when_watchers:
            condition, inside_statements = when_watcher[:2]
            condition_val = self._evaluate_expression(
                condition, namespaces, async_statements, when_statement_watchers
            )
            if isinstance(value, GulfOfMexicoMutable):
                if id(value) not in when_statement_watchers[-1]:
                    when_statement_watchers[-1][id(value)] = []
                when_statement_watchers[-1][id(value)].append(when_watcher)
            self._execute_conditional(
                condition_val,
                inside_statements,
                namespaces,
                when_statement_watchers,
            )

        return None

    def _check_type_annotation(
        self, value: GulfOfMexicoValue, type_tokens: list[Token]
    ) -> None:
        """Check if a value matches the expected type annotation.

        Args:
            value: The value to check
            type_tokens: Tokens representing the type annotation

        Raises:
            InterpretationError: If type doesn't match
        """
        if not type_tokens:
            return

        type_name_tokens = [t for t in type_tokens if hasattr(t, "type")]
        if not type_name_tokens:
            return

        type_name = "".join(t.value for t in type_name_tokens)

        # Map type names to checks
        type_checks = {
            "Int": self._check_is_number,
            "String": self._check_is_string,
            "Char[]": self._check_is_string,
            "Int9": self._check_is_number,
            "Int99": self._check_is_number,
        }

        if checker := type_checks.get(type_name):
            checker(value, type_name)

    def _check_is_number(self, value: GulfOfMexicoValue, type_name: str) -> None:
        """Check if value is a number."""
        from gulfofmexico.builtin import GulfOfMexicoNumber
        from gulfofmexico.base import InterpretationError

        if not isinstance(value, GulfOfMexicoNumber):
            raise InterpretationError(
                f"Type error: expected {type_name}, got {type(value).__name__}"
            )

    def _check_is_string(self, value: GulfOfMexicoValue, type_name: str) -> None:
        """Check if value is a string."""
        from gulfofmexico.builtin import GulfOfMexicoString
        from gulfofmexico.base import InterpretationError

        if not isinstance(value, GulfOfMexicoString):
            raise InterpretationError(
                f"Type error: expected {type_name}, got {type(value).__name__}"
            )

    def _save_local_immutable_constant(
        self, name: str, value: GulfOfMexicoValue, confidence: int
    ) -> None:
        """Save an immutable constant locally."""
        import pickle
        import random
        from pathlib import Path

        dir_path = Path().home() / ".gulfofmexico"
        immutable_values_path = dir_path / ".immutable_constants_values"

        # Create directories if they don't exist
        if not dir_path.is_dir():
            dir_path.mkdir()
        if not immutable_values_path.is_dir():
            immutable_values_path.mkdir()

        # Generate unique ID
        generated_addr = random.randint(1, 100000000000)
        sep = ";;;"

        # Save to list file
        with open(dir_path / ".immutable_constants", "a") as f:
            f.write(f"{name}{sep}{generated_addr}{sep}{confidence}\n")

        # Save value
        with open(
            dir_path / ".immutable_constants_values" / str(generated_addr), "wb"
        ) as f:
            pickle.dump(value, f)

    def _open_global_variable_issue(
        self, name: str, value: GulfOfMexicoValue, confidence: int
    ) -> None:
        """Try to open a GitHub issue to share this global variable.

        Args:
            name: Variable name
            value: Variable value
            confidence: Confidence level

        Raises:
            Exception: If GitHub API is unavailable
        """
        import json
        import os

        try:
            import github
        except ImportError:
            return

        try:
            access_token = os.environ["GITHUB_ACCESS_TOKEN"]
        except KeyError:
            return

        # Note: Serialization would happen here
        # This is a stub for the full implementation
        pass

    def _get_code_from_when_statement_watchers(
        self, name_or_id: Union[str, int], when_statement_watchers: WhenStatementWatchers
    ) -> list:
        """Get watchers for a name/id from the watchers list."""
        vals = []
        for watcher_dict in when_statement_watchers:
            if val := watcher_dict.get(name_or_id):
                vals += val
        return vals

    def _evaluate_expression(self, expr, namespaces, async_statements, when_statement_watchers):
        """Evaluate an expression (stub for now)."""
        # This would be imported from the main interpreter
        from gulfofmexico.builtin import GulfOfMexicoBoolean
        return GulfOfMexicoBoolean(True)

    def _execute_conditional(
        self, condition, inside_statements, namespaces, when_statement_watchers
    ):
        """Execute a conditional block (stub for now)."""
        pass

    @property
    def statement_type(self):
        """Return the statement type this handler processes."""
        return VariableDeclaration
