"""
Gulf of Mexico Interpreter Package

Re-exports the public API to maintain backward compatibility with code
that does ``import gulfofmexico.interpreter as interpreter`` and then
accesses ``interpreter.filename``, ``interpreter.interpret_code_statements_main_wrapper``,
etc.

Modules:
    context      – InterpreterContext dataclass, type aliases, constants
    helpers      – Small utility functions (expression building, name mangling)
    operators    – Tiered equality, comparison, arithmetic
    namespaces   – Scope lookup and literal-value resolution
    persistence  – File I/O for variable storage
    expressions  – Expression evaluation engine
    variables    – Variable declaration and assignment
    watchers     – When-statements, next/previous tracking, name watching
    dispatch     – Statement-type determination
    execution    – Main interpretation loop
"""

from __future__ import annotations

# --- Context (shared state + type aliases) ---
from .context import (
    AsyncStatements,
    CodeStatementWithExpression,
    InterpreterContext,
    NameWatchers,
    Namespace,
    WhenStatementWatchers,
)

# --- Persistence ---
from .persistence import (
    load_global_gulfofmexico_variables,
    load_globals,
    load_public_global_variables,
)

# --- Execution ---
from .execution import (
    execute_conditional,
    interpret_code_statements,
    interpret_code_statements_main_wrapper,
)

# --- Backward-compatible module-level mutable state ---
# Consumers (repl.py, __init__.py, __main__.py) set ``interpreter.filename``
# and ``interpreter.code`` directly.  We provide a module-level default
# InterpreterContext and expose its attributes for this purpose.
_default_ctx = InterpreterContext()

filename: str = _default_ctx.filename
code: str = _default_ctx.code

__all__ = [
    # Types
    "AsyncStatements",
    "CodeStatementWithExpression",
    "InterpreterContext",
    "NameWatchers",
    "Namespace",
    "WhenStatementWatchers",
    # Persistence
    "load_global_gulfofmexico_variables",
    "load_globals",
    "load_public_global_variables",
    # Execution
    "execute_conditional",
    "interpret_code_statements",
    "interpret_code_statements_main_wrapper",
    # Backward compat state
    "filename",
    "code",
]
