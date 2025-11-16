"""⚠️ EXPERIMENTAL - Example plugin that adds a custom statement type.

WARNING: This is a proof-of-concept only. The plugin system is NOT supported
in the production interpreter (gulfofmexico/interpreter.py).

This plugin demonstrates how custom statement types COULD work with the
experimental plugin system, but it is NOT functional in production.

To add a new statement type to the production interpreter, you must:
1. Define the statement class in processor/syntax_tree.py
2. Add parsing logic in processor/syntax_tree.py
3. Add execution logic via pattern matching in interpreter.py
"""

from typing import Optional, Type
from gulfofmexico.plugin_system import Plugin
from gulfofmexico.handlers import StatementHandler
from gulfofmexico.context import ExecutionContext
from gulfofmexico.processor.syntax_tree import CodeStatement
from gulfofmexico.builtin import GulfOfMexicoValue, GulfOfMexicoNumber


# Define a custom statement type (would normally be in syntax_tree.py)
class PrintDebugStatement(CodeStatement):
    """Custom statement for debug printing."""

    def __init__(self, message_token, expression):
        self.message_token = message_token
        self.expression = expression


class PrintDebugHandler(StatementHandler):
    """Handler for custom PrintDebug statement.

    This demonstrates a custom statement that prints debug information
    along with the evaluated expression.
    """

    def can_handle(self, statement: CodeStatement) -> bool:
        return isinstance(statement, PrintDebugStatement)

    def execute(
        self,
        statement: CodeStatement,
        context: ExecutionContext,
    ) -> Optional[GulfOfMexicoValue]:
        from gulfofmexico.interpreter import evaluate_expression

        assert isinstance(statement, PrintDebugStatement)

        # Evaluate the expression
        result = evaluate_expression(
            statement.expression,
            context.namespaces,
            context.async_statements,
            context.when_watchers,
        )

        # Print debug message
        message = statement.message_token.value
        print(f"[DEBUG {context.current_line}] {message}: {result}")

        return None

    @property
    def statement_type(self) -> Type[CodeStatement]:
        return PrintDebugStatement


class CustomStatementPlugin(Plugin):
    """Plugin that adds a custom print_debug statement."""

    @property
    def name(self) -> str:
        return "custom-statement-plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Adds a custom print_debug statement for enhanced debugging"

    def get_handlers(self) -> list[StatementHandler]:
        """Provide the custom statement handler."""
        return [PrintDebugHandler()]

    def get_builtin_functions(self) -> dict[str, callable]:
        """No custom built-in functions."""
        return {}

    def on_load(self) -> None:
        """Called when plugin is loaded."""
        print(f"[{self.name}] Loaded version {self.version}")

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        print(f"[{self.name}] Unloaded")
