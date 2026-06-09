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
from gulfofmexico.base import InterpretationError, NonFormattedError
from gulfofmexico.repl import main as repl_main


def _report_error(exc: BaseException) -> None:
    """Print a user-facing error message for a failed run.

    InterpretationError already carries a formatted (and colored) message, so it
    is printed as-is. Other known error types are given a concise description.
    """
    if isinstance(exc, InterpretationError):
        # Already formatted with source context and ANSI colors.
        print(str(exc), file=sys.stderr)
    elif isinstance(exc, NonFormattedError):
        print(f"\033[31mError: {exc}\033[39m", file=sys.stderr)
    elif isinstance(exc, FileNotFoundError):
        print(f"\033[31mError: file not found: {exc.filename}\033[39m", file=sys.stderr)
    elif isinstance(exc, KeyboardInterrupt):
        print("\nInterrupted.", file=sys.stderr)
    else:
        print(f"\033[31mError during execution: {exc}\033[39m", file=sys.stderr)


def _run_inline(code: str, show_tb: bool) -> int:
    """Execute inline Gulf of Mexico code via production interpreter.

    Args:
        code: Source code string to execute
        show_tb: Whether to show Python traceback on errors

    Returns:
        Exit code (0 for success, 1 for error)
    """
    from typing import Union  # pylint: disable=import-outside-toplevel

    from gulfofmexico.interpreter import (  # pylint: disable=import-outside-toplevel
        InterpreterContext,
        interpret_code_statements_main_wrapper,
    )
    from gulfofmexico.interpreter.persistence import (  # pylint: disable=import-outside-toplevel
        load_global_gulfofmexico_variables,
        load_globals,
        load_public_global_variables,
    )
    from gulfofmexico.builtin import (  # pylint: disable=import-outside-toplevel
        KEYWORDS,
        GulfOfMexicoValue,
        Name,
        Variable,
    )
    from gulfofmexico.processor.lexer import tokenize  # pylint: disable=import-outside-toplevel
    from gulfofmexico.processor.syntax_tree import (
        generate_syntax_tree,  # pylint: disable=import-outside-toplevel
    )

    try:
        filename = "__inline__"
        ctx = InterpreterContext(filename=filename, code=code)

        tokens = tokenize(filename, code)
        statements = generate_syntax_tree(filename, tokens, code)

        namespaces: list[dict[str, Union[Variable, Name]]] = [
            KEYWORDS.copy()  # type: ignore
        ]
        exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []
        importable_names: dict[str, dict[str, GulfOfMexicoValue]] = {}

        load_globals(
            filename,
            code,
            {},
            set(),
            exported_names,
            importable_names.get(filename, {}),
        )
        load_global_gulfofmexico_variables(namespaces)
        load_public_global_variables(namespaces)

        interpret_code_statements_main_wrapper(
            statements,
            namespaces,
            [],
            [{}],
            importable_names,
            exported_names,
            ctx,
        )
        return 0
    except Exception as exc:  # pylint: disable=broad-exception-caught
        if show_tb:
            raise
        _report_error(exc)
        return 1


def _main(argv: Optional[list[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="gom",
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Gulf of Mexico language interpreter.",
        epilog=(
            "modes:\n"
            "  gom                      start the interactive REPL\n"
            "  gom script.gom           run a source file\n"
            "  gom -c \"print(1)!\"       run inline code and exit\n"
            "  gom -s script.gom        run a file, showing a full Python traceback on error\n"
            "  gom-ide                  launch the graphical IDE (requires the 'ide' extra)\n\n"
            "environment variables:\n"
            "  GULFOFMEXICO_DEBUG=1     show internal debug messages (same as --debug)\n"
            "  GULFOFMEXICO_VERBOSE=1   show verbose completion messages (same as --verbose)\n\n"
            "examples:\n"
            "  gom examples/01_hello_world.gom\n"
            "  gom -c 'const const name = \"world\"! print(name)!'\n"
        ),
    )
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
        except Exception:  # pylint: disable=broad-exception-caught
            if ns.show_traceback:
                raise
            return 1

    # File mode
    if ns.file:
        try:
            run_file(ns.file)
            return 0
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if ns.show_traceback:
                raise
            _report_error(exc)
            return 1

    # Default: REPL
    try:
        return repl_main([])
    except Exception:  # pylint: disable=broad-exception-caught
        if ns.show_traceback:
            raise
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())


def main():
    """Entry point for console scripts."""
    raise SystemExit(_main())
