"""EXPERIMENTAL Gulf of Mexico Interpreter - Alternative Modular Architecture.

⚠️ WARNING: This package is NOT used in production! ⚠️

The actual Gulf of Mexico interpreter uses the monolithic implementation in
gulfofmexico/interpreter.py (~2,900 lines). This experimental engine package
exists as a proof-of-concept for exploring an alternative modular architecture
but is NOT integrated into the main execution path.

Production code path:
    gulfofmexico/__init__.py -> interpreter.interpret_code_statements_main_wrapper()

This experimental package provides:
- Handler-based statement execution (NOT used)
- Expression and namespace caching (NOT used)
- Plugin system prototype (NOT used)
"""

from gulfofmexico.engine.core import InterpretEngine
from gulfofmexico.engine.evaluator import ExpressionEvaluator

__all__ = ["InterpretEngine", "ExpressionEvaluator"]
