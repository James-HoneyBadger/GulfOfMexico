"""⚠️ EXPERIMENTAL - Example plugins for plugin system demonstration.

WARNING: The plugin system is NOT supported in the production interpreter.
These are proof-of-concept examples only.

This package contains example plugins demonstrating the experimental plugin system:
- example_custom_statement: Custom statement type with handler (EXPERIMENTAL)
- example_math_utils: Custom built-in functions (EXPERIMENTAL)

The production interpreter (gulfofmexico/interpreter.py) does NOT load or use plugins.
To extend the production interpreter, you must modify interpreter.py directly.
"""

__all__ = [
    "example_custom_statement",
    "example_math_utils",
]
