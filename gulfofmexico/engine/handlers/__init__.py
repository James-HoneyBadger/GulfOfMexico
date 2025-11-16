"""EXPERIMENTAL statement handlers for the Gulf of Mexico interpreter.

⚠️ WARNING: These handlers are NOT used in production! ⚠️

The actual Gulf of Mexico interpreter uses pattern matching in interpreter.py.
These handlers exist as a proof-of-concept for an alternative modular
architecture organized by functionality:

- variables: Variable declarations and assignments
- control_flow: Conditionals, when, and after statements
- functions: Function definitions and class declarations
- special: Delete, reverse, import, export, return, and expression statements
"""

from gulfofmexico.handlers import StatementHandler
from gulfofmexico.engine.handlers.variables import (
    VariableDeclarationHandler,
    VariableAssignmentHandler,
)
from gulfofmexico.engine.handlers.control_flow import (
    ConditionalHandler,
    WhenStatementHandler,
    AfterStatementHandler,
)
from gulfofmexico.engine.handlers.functions import (
    FunctionDefinitionHandler,
    ClassDeclarationHandler,
)
from gulfofmexico.engine.handlers.special import (
    DeleteStatementHandler,
    ReverseStatementHandler,
    ImportStatementHandler,
    ExportStatementHandler,
    ReturnStatementHandler,
    ExpressionStatementHandler,
)

__all__ = [
    "StatementHandler",
    # Variable handlers
    "VariableDeclarationHandler",
    "VariableAssignmentHandler",
    # Control flow handlers
    "ConditionalHandler",
    "WhenStatementHandler",
    "AfterStatementHandler",
    # Function/class handlers
    "FunctionDefinitionHandler",
    "ClassDeclarationHandler",
    # Special statement handlers
    "DeleteStatementHandler",
    "ReverseStatementHandler",
    "ImportStatementHandler",
    "ExportStatementHandler",
    "ReturnStatementHandler",
    "ExpressionStatementHandler",
]
