"""⚠️ EXPERIMENTAL - Example plugin that adds custom built-in functions.

WARNING: This is a proof-of-concept only. The plugin system is NOT supported
in the production interpreter (gulfofmexico/interpreter.py).

This plugin demonstrates how custom built-in functions COULD work with the
experimental plugin system, but it is NOT functional in production.

To add a new built-in function to the production interpreter, you must:
1. Define the function in interpreter.py (e.g., builtin_myfunction)
2. Register it in the BUILTIN_FUNCTIONS dict in interpreter.py
"""

from typing import Callable
from gulfofmexico.plugin_system import Plugin
from gulfofmexico.handlers import StatementHandler
from gulfofmexico.builtin import (
    GulfOfMexicoValue,
    GulfOfMexicoNumber,
    GulfOfMexicoString,
    GulfOfMexicoList,
)


def builtin_sum(args: list[GulfOfMexicoValue]) -> GulfOfMexicoValue:
    """Sum a list of numbers.

    Usage: sum([1, 2, 3, 4])
    Returns: 10
    """
    if len(args) != 1:
        raise ValueError("sum() takes exactly 1 argument")

    arg = args[0]
    if not isinstance(arg, GulfOfMexicoList):
        raise ValueError("sum() argument must be a list")

    total = 0
    for value in arg.values:
        if isinstance(value, GulfOfMexicoNumber):
            total += value.value
        else:
            raise ValueError("sum() requires all list elements to be numbers")

    return GulfOfMexicoNumber(total)


def builtin_join(args: list[GulfOfMexicoValue]) -> GulfOfMexicoValue:
    """Join a list of strings with a separator.

    Usage: join([\"hello\", \"world\"], \" \")
    Returns: "hello world"
    """
    if len(args) != 2:
        raise ValueError("join() takes exactly 2 arguments")

    strings_arg = args[0]
    separator_arg = args[1]

    if not isinstance(strings_arg, GulfOfMexicoList):
        raise ValueError("join() first argument must be a list")

    if not isinstance(separator_arg, GulfOfMexicoString):
        raise ValueError("join() second argument must be a string")

    separator = separator_arg.value
    parts = []

    for value in strings_arg.values:
        if isinstance(value, GulfOfMexicoString):
            parts.append(value.value)
        else:
            raise ValueError("join() requires all list elements to be strings")

    result = separator.join(parts)
    return GulfOfMexicoString(result)


def builtin_range(args: list[GulfOfMexicoValue]) -> GulfOfMexicoValue:
    """Generate a range of numbers.

    Usage: range(5) -> [0, 1, 2, 3, 4]
           range(2, 5) -> [2, 3, 4]
           range(0, 10, 2) -> [0, 2, 4, 6, 8]
    """
    if len(args) == 1:
        # range(stop)
        stop_arg = args[0]
        if not isinstance(stop_arg, GulfOfMexicoNumber):
            raise ValueError("range() argument must be a number")

        numbers = [GulfOfMexicoNumber(i) for i in range(int(stop_arg.value))]
        return GulfOfMexicoList(numbers)

    elif len(args) == 2:
        # range(start, stop)
        start_arg, stop_arg = args
        if not isinstance(start_arg, GulfOfMexicoNumber):
            raise ValueError("range() start must be a number")
        if not isinstance(stop_arg, GulfOfMexicoNumber):
            raise ValueError("range() stop must be a number")

        start = int(start_arg.value)
        stop = int(stop_arg.value)
        numbers = [GulfOfMexicoNumber(i) for i in range(start, stop)]
        return GulfOfMexicoList(numbers)

    elif len(args) == 3:
        # range(start, stop, step)
        start_arg, stop_arg, step_arg = args
        if not isinstance(start_arg, GulfOfMexicoNumber):
            raise ValueError("range() start must be a number")
        if not isinstance(stop_arg, GulfOfMexicoNumber):
            raise ValueError("range() stop must be a number")
        if not isinstance(step_arg, GulfOfMexicoNumber):
            raise ValueError("range() step must be a number")

        start = int(start_arg.value)
        stop = int(stop_arg.value)
        step = int(step_arg.value)
        numbers = [GulfOfMexicoNumber(i) for i in range(start, stop, step)]
        return GulfOfMexicoList(numbers)

    else:
        raise ValueError("range() takes 1 to 3 arguments")


class MathUtilsPlugin(Plugin):
    """Plugin that adds useful mathematical and list utility functions."""

    @property
    def name(self) -> str:
        return "math-utils-plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Adds math and list utility functions: sum, join, range"

    def get_handlers(self) -> list[StatementHandler]:
        """No custom statement handlers."""
        return []

    def get_builtin_functions(self) -> dict[str, Callable]:
        """Provide custom built-in functions."""
        return {
            "sum": builtin_sum,
            "join": builtin_join,
            "range": builtin_range,
        }

    def on_load(self) -> None:
        """Called when plugin is loaded."""
        print(f"[{self.name}] Loaded version {self.version}")
        print(f"[{self.name}] Available functions: sum(), join(), range()")

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        print(f"[{self.name}] Unloaded")
