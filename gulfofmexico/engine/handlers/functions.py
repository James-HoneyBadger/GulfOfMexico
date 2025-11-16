"""EXPERIMENTAL function and class definition handlers.

⚠️ WARNING: These handlers are NOT used in production! ⚠️

The actual Gulf of Mexico interpreter uses pattern matching in interpreter.py
to handle functions and classes. These handlers exist as a proof-of-concept
for an alternative modular architecture.
"""

from typing import Optional, Type
from gulfofmexico.handlers import StatementHandler
from gulfofmexico.processor.syntax_tree import (
    CodeStatement,
    FunctionDefinition,
    ClassDeclaration,
)
from gulfofmexico.context import ExecutionContext
from gulfofmexico.builtin import (
    GulfOfMexicoValue,
    GulfOfMexicoFunction,
    GulfOfMexicoObject,
    Variable,
    VariableLifetime,
    Name,
)
from gulfofmexico.constants import MAX_CONFIDENCE


class FunctionDefinitionHandler(StatementHandler):
    """Handler for function definitions."""

    def can_handle(self, statement: CodeStatement) -> bool:
        """Check if this is a function definition.

        Args:
            statement: Statement to check

        Returns:
            True if this is a FunctionDefinition
        """
        return isinstance(statement, FunctionDefinition)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a function definition.

        Args:
            statement: The function definition statement
            context: Execution context

        Returns:
            None (definitions don't return values)
        """
        assert isinstance(statement, FunctionDefinition)

        # Create the function object
        func = GulfOfMexicoFunction(
            [arg.value for arg in statement.args],
            statement.code,
            statement.is_async,
        )

        # Add to namespace
        context.namespaces[-1][statement.name.value] = Variable(
            statement.name.value,
            [VariableLifetime(func, MAX_CONFIDENCE, 0, True, True)],
            [],
        )

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        """Return the statement type this handler processes.

        Returns:
            FunctionDefinition class
        """
        return FunctionDefinition


class ClassDeclarationHandler(StatementHandler):
    """Handler for class declarations."""

    def can_handle(self, statement: CodeStatement) -> bool:
        """Check if this is a class declaration.

        Args:
            statement: Statement to check

        Returns:
            True if this is a ClassDeclaration
        """
        return isinstance(statement, ClassDeclaration)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a class declaration.

        Args:
            statement: The class declaration statement
            context: Execution context

        Returns:
            None (declarations don't return values)
        """
        from gulfofmexico.interpreter import interpret_code_statements

        assert isinstance(statement, ClassDeclaration)

        # Create a class object
        class_obj = GulfOfMexicoObject(statement.name.value, {})

        # Execute the class body in a new scope
        class_namespace = {statement.name.value: Name(statement.name.value, class_obj)}

        interpret_code_statements(
            statement.code,
            context.namespaces + [class_namespace],
            context.async_statements,
            context.when_watchers + [{}],
            context.importable_names,
            context.exported_names,
        )

        # Add the class to the namespace
        context.namespaces[-1][statement.name.value] = Name(
            statement.name.value, class_obj
        )

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        """Return the statement type this handler processes.

        Returns:
            ClassDeclaration class
        """
        return ClassDeclaration
