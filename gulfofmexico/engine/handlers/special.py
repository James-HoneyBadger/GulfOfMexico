"""EXPERIMENTAL special statement handlers.

⚠️ WARNING: These handlers are NOT used in production! ⚠️

The actual Gulf of Mexico interpreter uses pattern matching in interpreter.py
to handle these special statements. These handlers exist as a proof-of-concept
for an alternative modular architecture.
"""

from typing import Optional, Type
from gulfofmexico.handlers import StatementHandler
from gulfofmexico.processor.syntax_tree import (
    CodeStatement,
    DeleteStatement,
    ReverseStatement,
    ImportStatement,
    ExportStatement,
    ReturnStatement,
    ExpressionStatement,
)
from gulfofmexico.context import ExecutionContext
from gulfofmexico.builtin import (
    GulfOfMexicoValue,
    GulfOfMexicoList,
    GulfOfMexicoString,
    Variable,
    Name,
)
from gulfofmexico.base import raise_error_at_token


class DeleteStatementHandler(StatementHandler):
    """Handler for delete statements."""

    def can_handle(self, statement: CodeStatement) -> bool:
        return isinstance(statement, DeleteStatement)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        from gulfofmexico.interpreter import get_name_and_namespace_from_namespaces

        assert isinstance(statement, DeleteStatement)

        # Mark value as deleted
        var, ns = get_name_and_namespace_from_namespaces(
            statement.name.value, context.namespaces
        )

        if var and isinstance(var, Variable):
            context.mark_deleted(var.value)
            if ns:
                del ns[statement.name.value]

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        return DeleteStatement


class ReverseStatementHandler(StatementHandler):
    """Handler for reverse statements."""

    def can_handle(self, statement: CodeStatement) -> bool:
        return isinstance(statement, ReverseStatement)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        from gulfofmexico.interpreter import get_name_and_namespace_from_namespaces

        assert isinstance(statement, ReverseStatement)

        var, ns = get_name_and_namespace_from_namespaces(
            statement.name.value, context.namespaces
        )

        if var is None:
            raise_error_at_token(
                context.filename,
                context.code,
                f"Cannot reverse undefined name: {statement.name.value}",
                statement.name,
            )

        value = var.value if isinstance(var, Name) else var.value

        if isinstance(value, GulfOfMexicoList):
            # Reverse list in-place
            value.values.reverse()
            value.create_namespace()
        elif isinstance(value, GulfOfMexicoString):
            # Reverse string - create new reversed string
            reversed_str = value.value[::-1]
            new_value = GulfOfMexicoString(reversed_str)
            if isinstance(var, Variable):
                from gulfofmexico.constants import MAX_CONFIDENCE

                var.add_lifetime(
                    new_value,
                    0,
                    MAX_CONFIDENCE,
                    var.can_be_reset,
                    var.can_edit_value,
                )
            elif isinstance(var, Name):
                var.value = new_value
        else:
            raise_error_at_token(
                context.filename,
                context.code,
                f"Cannot reverse type {type(value).__name__}. "
                f"Only lists and strings can be reversed.",
                statement.name,
            )

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        return ReverseStatement


class ImportStatementHandler(StatementHandler):
    """Handler for import statements."""

    def can_handle(self, statement: CodeStatement) -> bool:
        return isinstance(statement, ImportStatement)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        assert isinstance(statement, ImportStatement)

        for name_token in statement.names:
            name = name_token.value
            found = False
            for file_dict in context.importable_names.values():
                if name in file_dict:
                    context.namespaces[-1][name] = Name(name, file_dict[name])
                    found = True
                    break
            if not found:
                raise_error_at_token(
                    context.filename,
                    context.code,
                    f"Cannot find imported name: {name}",
                    name_token,
                )

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        return ImportStatement


class ExportStatementHandler(StatementHandler):
    """Handler for export statements."""

    def can_handle(self, statement: CodeStatement) -> bool:
        return isinstance(statement, ExportStatement)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        from gulfofmexico.interpreter import get_name_from_namespaces

        assert isinstance(statement, ExportStatement)

        for name_token in statement.names:
            name = name_token.value
            v = get_name_from_namespaces(name, context.namespaces)
            if v is None:
                raise_error_at_token(
                    context.filename,
                    context.code,
                    f"Cannot export undefined name: {name}",
                    name_token,
                )
            value = v.value if isinstance(v, Name) else v.value
            target = statement.target_file.value
            context.exported_names.append((target, name, value))

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        return ExportStatement


class ReturnStatementHandler(StatementHandler):
    """Handler for return statements."""

    def can_handle(self, statement: CodeStatement) -> bool:
        return isinstance(statement, ReturnStatement)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        from gulfofmexico.interpreter import (
            evaluate_expression,
            print_expression_debug,
        )

        assert isinstance(statement, ReturnStatement)

        result = evaluate_expression(
            statement.expression,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        print_expression_debug(
            statement.debug,
            statement.expression,
            result,
            context.namespaces,
        )

        return result

    @property
    def statement_type(self) -> Type[CodeStatement]:
        return ReturnStatement


class ExpressionStatementHandler(StatementHandler):
    """Handler for expression statements."""

    def can_handle(self, statement: CodeStatement) -> bool:
        return isinstance(statement, ExpressionStatement)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        from gulfofmexico.interpreter import (
            evaluate_expression,
            print_expression_debug,
        )

        assert isinstance(statement, ExpressionStatement)

        result = evaluate_expression(
            statement.expression,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        print_expression_debug(
            statement.debug,
            statement.expression,
            result,
            context.namespaces,
        )

        return result

    @property
    def statement_type(self) -> Type[CodeStatement]:
        return ExpressionStatement
