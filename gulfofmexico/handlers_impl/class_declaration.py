"""ClassDeclarationHandler - Class declaration and object creation.

This handler manages class definition and creation, including:
  - Class object creation
  - Member initialization
  - Method binding
  - Inheritance support (future)
  - Scope management for class body
  - Statistics tracking

Classes are templates for creating objects with shared behavior.

Example:
    class Person:
        func __init__(name):
            this.name = name
"""

from typing import Optional, Any
from gulfofmexico.base import StatementHandler
from gulfofmexico.execution_context import ExecutionContext
from gulfofmexico.context import GulfOfMexicoValue


class ClassDeclarationHandler(StatementHandler):
    """Handler for class declaration statements in Gulf of Mexico.

    Classes define templates for creating objects with methods and properties.
    This handler:
      - Creates class objects from declarations
      - Initializes class namespace
      - Binds methods to the class
      - Manages class-level members
      - Stores class in namespace
      - Tracks class statistics

    Example:
        class MyClass:
            x = 10
            func method():
                return x
    """

    def __init__(self) -> None:
        """Initialize ClassDeclarationHandler."""
        super().__init__()
        self.builtin_imports: dict[str, Any] = {}
        self.execution_count: int = 0
        self.classes_defined: int = 0

    def set_interpreter_imports(self, imports: dict[str, Any]) -> None:
        """Set interpreter imports for dependency injection."""
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: Any) -> bool:
        """Check if this handler can process the given statement."""
        from gulfofmexico.base import ClassDeclaration

        return isinstance(stmt, ClassDeclaration)

    def execute(
        self,
        stmt: Any,
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a class declaration statement.

        Args:
            stmt: The ClassDeclaration statement to execute
            context: ExecutionContext with current state
            *args: Additional arguments (unused)
            **kwargs: Additional keyword arguments (unused)

        Returns:
            None (class declarations don't return values)

        Raises:
            RuntimeError: If required interpreter functions are missing
        """
        self.execution_count += 1

        # Validate required imports
        required_imports = [
            "GulfOfMexicoObject",
            "Name",
        ]
        for import_name in required_imports:
            if import_name not in self.builtin_imports:
                raise RuntimeError(
                    f"ClassDeclarationHandler missing required import: {import_name}"
                )

        # Create and register the class
        return self._declare_class(stmt, context)

    def _declare_class(
        self, stmt: Any, context: ExecutionContext
    ) -> Optional[GulfOfMexicoValue]:
        """Declare a class and store it in the namespace.

        Args:
            stmt: The ClassDeclaration statement
            context: ExecutionContext with current state

        Returns:
            None (declaration doesn't return values)
        """
        GulfOfMexicoObject = self.builtin_imports["GulfOfMexicoObject"]
        Name = self.builtin_imports["Name"]

        # Create empty class object
        class_obj = GulfOfMexicoObject(name=stmt.name.value, namespace={})

        # Create a namespace for the class body execution
        class_namespace = {stmt.name.value: Name(stmt.name.value, class_obj)}

        # Execute class body in isolated scope
        # TODO: Integrate with statement interpreter to execute class body
        # For now, this is a stub that would:
        # 1. Execute all statements in stmt.code
        # 2. Capture all defined members
        # 3. Populate class_obj.namespace with the members

        # Populate class members from the class namespace
        # (excluding the class self-reference)
        for key, value in class_namespace.items():
            if key != stmt.name.value:
                class_obj.namespace[key] = value

        # Store the class object in current namespace
        context.namespaces[-1][stmt.name.value] = Name(stmt.name.value, class_obj)
        self.classes_defined += 1

        return None

    def get_stats(self) -> dict[str, int]:
        """Get statistics about class declaration handler execution.

        Returns:
            Dictionary with execution stats
        """
        return {
            "total_executions": self.execution_count,
            "classes_defined": self.classes_defined,
        }

    def get_debug_info(self) -> str:
        """Get debug information about the handler state.

        Returns:
            String with debug information
        """
        return (
            f"ClassDeclarationHandler: "
            f"executed={self.execution_count}, "
            f"classes_defined={self.classes_defined}"
        )


def create_class_declaration_handler() -> ClassDeclarationHandler:
    """Factory function for creating ClassDeclarationHandler.

    Returns:
        A new ClassDeclarationHandler instance
    """
    return ClassDeclarationHandler()
