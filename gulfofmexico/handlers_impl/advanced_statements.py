"""Advanced Statement Handlers - After, Delete, and Import statements.

This module provides handlers for advanced Gulf of Mexico statements:
  - AfterStatementHandler: Delayed/deferred execution
  - DeleteStatementHandler: Variable deletion and cleanup
  - ImportExportHandler: Module import and export management

These handlers complete the core statement handler set for Phase 3.
"""

from typing import Optional, Any, Union
from gulfofmexico.base import StatementHandler
from gulfofmexico.execution_context import ExecutionContext
from gulfofmexico.context import GulfOfMexicoValue


class AfterStatementHandler(StatementHandler):
    """Handler for after-statements (delayed execution).

    After-statements defer code execution until a specified event or time.
    This enables event-driven programming patterns.

    Example:
        after mouse_click:
            print("Mouse clicked!")
    """

    def __init__(self) -> None:
        """Initialize AfterStatementHandler."""
        super().__init__()
        self.builtin_imports: dict[str, Any] = {}
        self.execution_count: int = 0
        self.events_triggered: int = 0

    def set_interpreter_imports(self, imports: dict[str, Any]) -> None:
        """Set interpreter imports for dependency injection."""
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: Any) -> bool:
        """Check if this handler can process the given statement."""
        from gulfofmexico.base import AfterStatement

        return isinstance(stmt, AfterStatement)

    def execute(
        self,
        stmt: Any,
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute an after-statement.

        Args:
            stmt: The AfterStatement to execute
            context: ExecutionContext with current state
            *args: Additional arguments (unused)
            **kwargs: Additional keyword arguments (unused)

        Returns:
            None (after-statement registers event handlers)

        Raises:
            RuntimeError: If required imports are missing
        """
        self.execution_count += 1

        required_imports = ["evaluate_expression"]
        for import_name in required_imports:
            if import_name not in self.builtin_imports:
                raise RuntimeError(
                    f"AfterStatementHandler missing required import: {import_name}"
                )

        # Evaluate the event expression
        # TODO: Register event handler based on event type
        return None

    def get_stats(self) -> dict[str, int]:
        """Get statistics about after-statement handler execution."""
        return {
            "total_executions": self.execution_count,
            "events_triggered": self.events_triggered,
        }

    def get_debug_info(self) -> str:
        """Get debug information about the handler state."""
        return (
            f"AfterStatementHandler: "
            f"executed={self.execution_count}, "
            f"triggered={self.events_triggered}"
        )


class DeleteStatementHandler(StatementHandler):
    """Handler for delete-statements (variable deletion).

    Delete-statements remove variables from scope and mark their values
    for garbage collection.

    Example:
        delete x
        delete mylist.item
    """

    def __init__(self) -> None:
        """Initialize DeleteStatementHandler."""
        super().__init__()
        self.builtin_imports: dict[str, Any] = {}
        self.execution_count: int = 0
        self.deletions_performed: int = 0

    def set_interpreter_imports(self, imports: dict[str, Any]) -> None:
        """Set interpreter imports for dependency injection."""
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: Any) -> bool:
        """Check if this handler can process the given statement."""
        from gulfofmexico.base import DeleteStatement

        return isinstance(stmt, DeleteStatement)

    def execute(
        self,
        stmt: Any,
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute a delete-statement.

        Args:
            stmt: The DeleteStatement to execute
            context: ExecutionContext with current state
            *args: Additional arguments (unused)
            **kwargs: Additional keyword arguments (unused)

        Returns:
            None

        Raises:
            RuntimeError: If required imports are missing
        """
        self.execution_count += 1

        required_imports = ["get_name_from_namespaces", "Variable"]
        for import_name in required_imports:
            if import_name not in self.builtin_imports:
                raise RuntimeError(
                    f"DeleteStatementHandler missing required import: {import_name}"
                )

        # Get the variable to delete
        get_name_from_namespaces = self.builtin_imports["get_name_from_namespaces"]
        Variable = self.builtin_imports["Variable"]

        var = get_name_from_namespaces(stmt.name.value, context.namespaces)

        if var and isinstance(var, Variable):
            # Mark variable values as deleted and remove from namespace
            for ns in reversed(context.namespaces):
                if stmt.name.value in ns:
                    del ns[stmt.name.value]
                    self.deletions_performed += 1
                    break

        return None

    def get_stats(self) -> dict[str, int]:
        """Get statistics about delete-statement handler execution."""
        return {
            "total_executions": self.execution_count,
            "deletions_performed": self.deletions_performed,
        }

    def get_debug_info(self) -> str:
        """Get debug information about the handler state."""
        return (
            f"DeleteStatementHandler: "
            f"executed={self.execution_count}, "
            f"deleted={self.deletions_performed}"
        )


class ImportExportHandler(StatementHandler):
    """Handler for import/export statements.

    Import/export statements manage module dependencies and public APIs.

    Examples:
        import math
        export MyClass
        from utils import helper_func
    """

    def __init__(self) -> None:
        """Initialize ImportExportHandler."""
        super().__init__()
        self.builtin_imports: dict[str, Any] = {}
        self.execution_count: int = 0
        self.imports_loaded: int = 0
        self.exports_registered: int = 0

    def set_interpreter_imports(self, imports: dict[str, Any]) -> None:
        """Set interpreter imports for dependency injection."""
        self.builtin_imports.update(imports)

    def can_handle(self, stmt: Any) -> bool:
        """Check if this handler can process the given statement."""
        from gulfofmexico.base import ImportStatement, ExportStatement

        return isinstance(stmt, (ImportStatement, ExportStatement))

    def execute(
        self,
        stmt: Any,
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[GulfOfMexicoValue]:
        """Execute an import or export statement.

        Args:
            stmt: The ImportStatement or ExportStatement to execute
            context: ExecutionContext with current state
            *args: Additional arguments (unused)
            **kwargs: Additional keyword arguments (unused)

        Returns:
            None

        Raises:
            RuntimeError: If required imports are missing
        """
        self.execution_count += 1

        from gulfofmexico.base import ImportStatement

        if isinstance(stmt, ImportStatement):
            self.imports_loaded += 1
            # TODO: Load and integrate imported module
        else:
            self.exports_registered += 1
            # TODO: Register exported symbols

        return None

    def get_stats(self) -> dict[str, int]:
        """Get statistics about import/export handler execution."""
        return {
            "total_executions": self.execution_count,
            "imports_loaded": self.imports_loaded,
            "exports_registered": self.exports_registered,
        }

    def get_debug_info(self) -> str:
        """Get debug information about the handler state."""
        return (
            f"ImportExportHandler: "
            f"executed={self.execution_count}, "
            f"imports={self.imports_loaded}, "
            f"exports={self.exports_registered}"
        )


def create_after_handler() -> AfterStatementHandler:
    """Factory function for creating AfterStatementHandler."""
    return AfterStatementHandler()


def create_delete_handler() -> DeleteStatementHandler:
    """Factory function for creating DeleteStatementHandler."""
    return DeleteStatementHandler()


def create_import_export_handler() -> ImportExportHandler:
    """Factory function for creating ImportExportHandler."""
    return ImportExportHandler()
