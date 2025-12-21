"""FunctionDefinitionHandler - Function definition and declaration.

This handler manages function definition and creation, including:
  - Function creation and storage
  - Parameter management
  - Return type handling
  - Async function support
  - Closure and scope management
  - Statistics tracking

Functions are first-class objects in Gulf of Mexico.

Example:
    func greet(name):
        return "Hello, " + name
"""

from typing import Optional, Any
from gulfofmexico.base import StatementHandler
from gulfofmexico.execution_context import ExecutionContext
from gulfofmexico.context import GulfOfMexicoValue


class FunctionDefinitionHandler(StatementHandler):
    """Handler for function definition statements in Gulf of Mexico.

    Functions are first-class objects that encapsulate code and parameters.
    This handler:
      - Creates function objects from definitions
      - Stores functions in namespace
      - Manages parameter lists
      - Supports async functions
      - Handles closures and scope
      - Tracks function statistics

    Example:
        func my_function(x, y):
            return x + y
    """

    def __init__(self) -> None:
        """Initialize FunctionDefinitionHandler."""
        super().__init__()
        self.builtin_imports: dict[str, Any] = {}
        self.execution_count: int = 0
        self.functions_defined: int = 0

    def set_interpreter_imports(self, imports: dict[str, Any]) -> None:
        """Set interpreter imports for dependency injection."""
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: Any) -> bool:
        """Check if this handler can process the given statement."""
        from gulfofmexico.base import FunctionDefinition

        return isinstance(stmt, FunctionDefinition)

    def execute(
        self,
        stmt: Any,
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a function definition statement.

        Args:
            stmt: The FunctionDefinition statement to execute
            context: ExecutionContext with current state
            *args: Additional arguments (unused)
            **kwargs: Additional keyword arguments (unused)

        Returns:
            None (functions don't return values on definition)

        Raises:
            RuntimeError: If required interpreter functions are missing
        """
        self.execution_count += 1

        # Validate required imports
        required_imports = [
            "GulfOfMexicoFunction",
            "Variable",
            "VariableLifetime",
            "Name",
        ]
        for import_name in required_imports:
            if import_name not in self.builtin_imports:
                raise RuntimeError(
                    f"FunctionDefinitionHandler missing required import: {import_name}"
                )

        # Create and register the function
        return self._define_function(stmt, context)

    def _define_function(
        self, stmt: Any, context: ExecutionContext
    ) -> Optional[GulfOfMexicoValue]:
        """Define a function and store it in the namespace.

        Args:
            stmt: The FunctionDefinition statement
            context: ExecutionContext with current state

        Returns:
            None (definition doesn't return values)
        """
        GulfOfMexicoFunction = self.builtin_imports["GulfOfMexicoFunction"]
        Variable = self.builtin_imports["Variable"]
        VariableLifetime = self.builtin_imports["VariableLifetime"]
        Name = self.builtin_imports["Name"]

        # Extract function parameters
        parameter_names = [arg.value for arg in stmt.args]

        # Create function object
        func_obj = GulfOfMexicoFunction(
            parameters=parameter_names,
            body=stmt.code,
            is_async=stmt.is_async,
        )

        # Store function in current namespace as a Variable
        func_var = Variable(
            name=stmt.name.value,
            lifetimes=[
                VariableLifetime(
                    value=func_obj,
                    lifetime=100000000000,  # Very long lifetime
                    index=0,
                    is_mutable=True,
                    exports=True,
                )
            ],
            deletions=[],
        )

        context.namespaces[-1][stmt.name.value] = func_var
        self.functions_defined += 1

        return None

    def get_stats(self) -> dict[str, int]:
        """Get statistics about function definition handler execution.

        Returns:
            Dictionary with execution stats
        """
        return {
            "total_executions": self.execution_count,
            "functions_defined": self.functions_defined,
        }

    def get_debug_info(self) -> str:
        """Get debug information about the handler state.

        Returns:
            String with debug information
        """
        return (
            f"FunctionDefinitionHandler: "
            f"executed={self.execution_count}, "
            f"functions_defined={self.functions_defined}"
        )


def create_function_definition_handler() -> FunctionDefinitionHandler:
    """Factory function for creating FunctionDefinitionHandler.

    Returns:
        A new FunctionDefinitionHandler instance
    """
    return FunctionDefinitionHandler()
