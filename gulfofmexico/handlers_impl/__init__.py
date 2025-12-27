"""
Concrete Statement Handler Implementations

This module contains the production-ready handler implementations that replace
the monolithic pattern matching in interpreter.py.

Each handler is responsible for executing a specific type of CodeStatement.

Handlers:
    - VariableDeclarationHandler: Handles variable declarations (const/var)
    - VariableAssignmentHandler: Handles variable assignments
    - ExpressionStatementHandler: Handles expression evaluation
    - ReturnStatementHandler: Handles return statements
    - ConditionalHandler: Handles if statements
    - WhenStatementHandler: Handles when statements (reactive)
    - AfterStatementHandler: Handles after statements (event listeners)
    - FunctionDefinitionHandler: Handles function definitions
    - ClassDeclarationHandler: Handles class definitions
    - DeleteStatementHandler: Handles variable deletion
    - ImportStatementHandler: Handles imports
    - ExportStatementHandler: Handles exports

Status: Production handlers being activated
"""

__all__ = []

# Handlers are imported on-demand in interpreter_phase5.py
# This keeps the module lightweight and avoids circular imports
