"""
Gulf of Mexico Command-Line Interface

Entry point for running Gulf of Mexico from the command line.

Usage Modes:
    1. REPL (interactive):
       $ python -m gulfofmexico

    2. Execute file:
       $ python -m gulfofmexico script.gom

    3. Inline code:
       $ python -m gulfofmexico -c "const x 123! print(x)!"

    4. Debug mode (show Python traceback):
       $ python -m gulfofmexico -s script.gom

    5. Debug output (show internal debug messages):
       $ python -m gulfofmexico --debug script.gom

    6. Verbose output (show completion messages):
       $ python -m gulfofmexico --verbose script.gom

All modes use the production interpreter in gulfofmexico/interpreter.py.
The experimental gulfofmexico/engine/ is never used.

Execution Path:
    - File mode: run_file() from gulfofmexico/__init__.py
    - Inline mode: _run_inline() direct interpreter invocation
    - REPL mode: repl_main() from gulfofmexico/repl.py
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from gulfofmexico import run_file
from gulfofmexico.repl import main as repl_main


def _run_inline(code: str, show_tb: bool) -> int:
    """Execute inline Gulf of Mexico code via production interpreter.

    Args:
        code: Source code string to execute
        show_tb: Whether to show Python traceback on errors

    Returns:
        Exit code (0 for success, 1 for error)
    """
    import gulfofmexico.interpreter as interpreter
    from gulfofmexico.processor.lexer import tokenize
    from gulfofmexico.processor.syntax_tree import generate_syntax_tree
    from gulfofmexico.builtin import KEYWORDS, Name, GulfOfMexicoValue, Variable
    from typing import Union

    try:
        filename = "__inline__"
        interpreter.filename = filename
        interpreter.code = code

        tokens = tokenize(filename, code)
        statements = generate_syntax_tree(filename, tokens, code)

        namespaces: list[dict[str, Union[Variable, Name]]] = [
            KEYWORDS.copy()  # type: ignore
        ]
        exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []
        importable_names: dict[str, dict[str, GulfOfMexicoValue]] = {}

        interpreter.load_globals(
            filename,
            code,
            {},
            set(),
            exported_names,
            importable_names.get(filename, {}),
        )
        interpreter.load_global_gulfofmexico_variables(namespaces)
        interpreter.load_public_global_variables(namespaces)

        interpreter.interpret_code_statements_main_wrapper(
            statements,
            namespaces,
            [],
            [{}],
            importable_names,
            exported_names,
        )
        return 0
    except Exception:
        if show_tb:
            raise
        print("Error during execution.", file=sys.stderr)
        return 1


def _main(argv: Optional[list[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(prog="gulfofmexico", add_help=True)
    parser.add_argument("file", nargs="?", help="Gulf of Mexico source file (.gom)")
    parser.add_argument(
        "-s",
        "--show-traceback",
        action="store_true",
        help="show full Python traceback on errors",
    )
    parser.add_argument("-c", dest="inline_code", help="run inline code and exit")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="show internal debug messages (same as GULFOFMEXICO_DEBUG=1)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="show verbose completion messages (same as GULFOFMEXICO_VERBOSE=1)",
    )
    ns = parser.parse_args(args)

    # Set environment variables based on flags
    if ns.debug:
        os.environ["GULFOFMEXICO_DEBUG"] = "1"
    if ns.verbose:
        os.environ["GULFOFMEXICO_VERBOSE"] = "1"

    # Inline code mode
    if ns.inline_code is not None:
        try:
            return _run_inline(ns.inline_code, ns.show_traceback)
        except Exception:
            if ns.show_traceback:
                raise
            return 1

    # File mode
    if ns.file:
        try:
            run_file(ns.file)
            return 0
        except Exception:
            if ns.show_traceback:
                raise
            return 1

    # Default: REPL
    try:
        return repl_main([])
    except Exception:
        if ns.show_traceback:
            raise
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())


def main():
    """Entry point for console scripts."""
    raise SystemExit(_main())
