"""
Gulf of Mexico Command-Line Interface

Entry point for running Gulf of Mexico from the command line.

Usage Modes:
    1. REPL (interactive):
       $ gom

    2. Execute file:
       $ gom script.gom

    3. Inline code:
       $ gom -c "print(42)!"

    4. Standard input:
       $ gom - < script.gom

    5. Check a program without running it:
       $ gom --check script.gom

    6. Canonicalise a file's layout (print, or rewrite with -w):
       $ gom --fmt script.gom
       $ gom --fmt -w script.gom

    7. Show the version:
       $ gom --version

    8. Debug mode (show Python traceback):
       $ gom -s script.gom

    9. Debug output (show internal debug messages):
       $ gom --debug script.gom

    10. Verbose output (show completion messages):
       $ gom --verbose script.gom

Exit codes:
    0  success
    1  the program raised an error
    2  bad command-line usage

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
from pathlib import Path
from typing import Optional

from gulfofmexico import run_file
from gulfofmexico.base import InterpretationError, NonFormattedError
from gulfofmexico.repl import main as repl_main
from gulfofmexico.ui import VERSION, print_error, print_info, print_success


def _report_error(exc: BaseException) -> None:
    """Report a failed run on stderr, with an actionable hint where possible."""
    message = str(exc)
    if isinstance(exc, InterpretationError):
        # Already rendered with source context and colours by gulfofmexico.ui.
        print(message, file=sys.stderr)
    elif isinstance(exc, NonFormattedError):
        print_error(str(exc), hint="re-run with -s to see the full Python traceback")
    elif isinstance(exc, FileNotFoundError):
        target = exc.filename or "the file"
        print_error(
            f"cannot open {target}",
            hint="check the path, or list the bundled programs with 'gom --help'",
        )
    elif isinstance(exc, IsADirectoryError):
        print_error(f"{exc.filename} is a directory", hint="pass a .gom source file instead")
    elif isinstance(exc, KeyboardInterrupt):
        print("Interrupted.", file=sys.stderr)
    elif isinstance(exc, RecursionError):
        print_error(
            "maximum recursion depth exceeded",
            hint=(
                "GOM has no loops, so this is usually runaway recursion; "
                "add a base case, or raise GOM_RECURSION_LIMIT"
            ),
        )
    else:
        print_error(f"{message or type(exc).__name__}",
                    hint="re-run with -s to see the full Python traceback")
    sys.stderr.flush()


def _validate_source_path(path: str) -> None:
    """Fail fast with a helpful message when *path* cannot be executed."""
    candidate = Path(path).expanduser()
    if candidate.is_dir():
        raise IsADirectoryError(21, "Is a directory", path)
    if not candidate.exists():
        raise FileNotFoundError(2, "No such file or directory", path)
    if candidate.suffix == "":
        print_info(
            f"'{path}' has no .gom extension; running it anyway",
            stream=sys.stderr,
        )


def _read_stdin_source() -> str:
    """Read a program from standard input (``gom -``)."""
    stream = sys.stdin
    if stream is None or stream.closed:  # pragma: no cover - no stdin available
        return ""
    return stream.read()


def _run_inline(
    code: str,
    show_tb: bool,
    vars_json: str | None = None,
    filename: str = "__inline__",
) -> int:
    """Execute inline Gulf of Mexico code via production interpreter.

    Args:
        code: Source code string to execute
        show_tb: Whether to show Python traceback on errors
        vars_json: Optional path for a JSON snapshot of the final variables
        filename: Source name used in diagnostics (``<stdin>`` for piped input)

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
    from gulfofmexico.prelude import load_prelude  # pylint: disable=import-outside-toplevel
    from gulfofmexico.processor.lexer import tokenize  # pylint: disable=import-outside-toplevel
    from gulfofmexico.processor.syntax_tree import (
        generate_syntax_tree,  # pylint: disable=import-outside-toplevel
    )

    try:
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
        load_prelude(namespaces, ctx)
        if vars_json:
            baseline_names = {name for namespace in namespaces for name in namespace}

        interpret_code_statements_main_wrapper(
            statements,
            namespaces,
            [],
            [{}],
            importable_names,
            exported_names,
            ctx,
        )
        if vars_json:
            import json  # pylint: disable=import-outside-toplevel

            from gulfofmexico import _snapshot_variables  # pylint: disable=import-outside-toplevel

            with open(vars_json, "w", encoding="utf-8") as handle:
                json.dump(_snapshot_variables(namespaces, baseline_names), handle)
        return 0
    except Exception as exc:  # pylint: disable=broad-exception-caught
        if show_tb:
            raise
        _report_error(exc)
        return 1


def _tool_targets(ns) -> list[tuple[str, str, Optional[Path]]] | None:
    """Resolve the sources ``--check``/``--fmt`` should work on.

    A target is ``(display_name, source_text, path_or_None)``. Returns ``None``
    after reporting a usage problem.
    """
    if ns.inline_code is not None:
        return [("<inline>", ns.inline_code, None)]
    paths = [ns.file, *ns.more_files] if ns.file else []
    if paths == ["-"]:
        return [("<stdin>", _read_stdin_source(), None)]
    if "-" in paths:
        print_error("'-' cannot be combined with file names", hint="pipe one program at a time")
        return None
    if paths:
        targets: list[tuple[str, str, Optional[Path]]] = []
        for name in paths:
            _validate_source_path(name)
            path = Path(name)
            targets.append((name, path.read_text(encoding="utf-8"), path))
        return targets
    print_error(
        "nothing to work on",
        hint="pass a FILE, '-' to read standard input, or -c 'code'",
    )
    return None


def _run_tool(ns) -> int:
    """Handle ``--check`` and ``--fmt`` (and their combination) for one source."""
    from gulfofmexico.tools import check_source, format_source  # pylint: disable=import-outside-toplevel

    targets = _tool_targets(ns)
    if targets is None:
        return 2

    status = 0
    for name, code, path in targets:
        formatted = format_source(name, code) if ns.fmt else None

        if formatted is not None:
            if ns.write:
                if path is None:
                    print_error(
                        "--write needs a file",
                        hint="standard input and -c cannot be rewritten in place",
                    )
                    status = 2
                    continue
                if formatted == code:
                    print_info(f"{name}: already formatted")
                else:
                    path.write_text(formatted, encoding="utf-8")
                    print_success(f"{name}: reformatted")
            elif ns.check:
                # Both flags: a CI-friendly "is this file canonical?" gate.
                if formatted != code:
                    print_error(
                        f"{name}: not formatted",
                        hint=f"run 'gom --fmt -w {name}' to rewrite it",
                    )
                    status = 1
                elif not ns.quiet:
                    print_info(f"{name}: formatted")
            else:
                sys.stdout.write(formatted)

        if ns.check:
            source = formatted if formatted is not None else code
            try:
                count = check_source(name, source)
            except InterpretationError as exc:
                print(str(exc), file=sys.stderr)
                status = 1
                continue
            if not ns.quiet:
                plural = "" if count == 1 else "s"
                print_success(f"{name}: ok ({count} statement{plural})")

    return status


class _HelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Keep option help on one line and align it to a comfortable column."""

    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=26, width=90)


def _build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser with grouped, scannable help output."""
    parser = argparse.ArgumentParser(
        prog="gom",
        usage="gom [options] [FILE]",
        add_help=True,
        formatter_class=_HelpFormatter,
        description=(
            "Gulf of Mexico - an esoteric language where arrays start at -1.\n"
            "Run a program, evaluate an expression, or drop into the REPL."
        ),
        epilog=(
            "modes:\n"
            "  gom                        start the interactive REPL\n"
            "  gom program.gom            run a source file\n"
            "  gom -c \"print(42)!\"        run inline code and exit\n"
            "  gom - < program.gom        run a program read from standard input\n"
            "  gom --check program.gom    parse and validate without running\n"
            "  gom --fmt program.gom      print the program in canonical layout (-w rewrites)\n"
            "  gom -s program.gom         run a file, printing a Python traceback on error\n"
            "  gom-ide                    launch the graphical IDE (requires the 'ide' extra)\n"
            "\n"
            "environment:\n"
            "  GULFOFMEXICO_DEBUG=1       internal debug messages (same as --debug)\n"
            "  GULFOFMEXICO_VERBOSE=1     completion messages (same as --verbose)\n"
            "  GULFOFMEXICO_WAIT=1        wait for when/after statements after the program ends\n"
            "  GOM_DISABLE_TARIFF=1       disable the random import tariff\n"
            "  GOM_NO_PRELUDE=1           do not auto-load the standard helper library\n"
            "  GOM_HOME=DIR               parent of the runtime state directory (default: home)\n"
            "  GOM_RECURSION_LIMIT=N      maximum interpreter recursion depth\n"
            "  NO_COLOR=1                 disable colour (same as --no-color)\n"
            "\n"
            "examples:\n"
            "  gom examples/01_hello_world.gom\n"
            "  gom -c 'const const name = \"world\"! print(name)!'\n"
            "  gom --check --fmt examples/01_hello_world.gom\n"
            "  gom --version\n"
        ),
    )
    parser.add_argument(
        "file",
        nargs="?",
        metavar="FILE",
        help="Gulf of Mexico source file to execute (.gom)",
    )
    parser.add_argument(
        "more_files",
        nargs="*",
        metavar="FILE",
        help=argparse.SUPPRESS,  # additional files for --check / --fmt
    )

    run = parser.add_argument_group("running code")
    run.add_argument(
        "-c",
        dest="inline_code",
        metavar="CODE",
        help="run inline code and exit",
    )
    run.add_argument(
        "-s",
        "--show-traceback",
        action="store_true",
        help="show a Python traceback when the program fails",
    )

    tools = parser.add_argument_group("tools")
    tools.add_argument(
        "--check",
        action="store_true",
        help="parse and validate the program without running it",
    )
    tools.add_argument(
        "--fmt",
        action="store_true",
        help="print the program in canonical layout (never reflows a line)",
    )
    tools.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="with --fmt, rewrite the file in place",
    )

    output = parser.add_argument_group("output")
    output.add_argument(
        "--debug",
        action="store_true",
        help="show internal debug messages",
    )
    output.add_argument(
        "--verbose",
        action="store_true",
        help="show a completion message with elapsed time",
    )
    output.add_argument(
        "--no-color",
        action="store_true",
        help="disable ANSI colour (also honours NO_COLOR)",
    )
    output.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress non-essential informational messages",
    )
    output.add_argument(
        "--vars-json",
        metavar="PATH",
        help="write a JSON snapshot of the final variables (used by the IDE)",
    )
    output.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"gom {VERSION}",
        help="print the interpreter version and exit",
    )
    return parser


def _main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point that also handles interpreter-level signals."""
    try:
        return _run_main(argv)
    except BrokenPipeError:
        # The reader went away (``gom program.gom | head``). Close stdout
        # quietly so Python does not report a flush error on exit.
        _close_stdout_quietly()
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


def _close_stdout_quietly() -> None:
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
    except OSError:  # pragma: no cover - stdout already closed
        pass


def _run_main(argv: Optional[list[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    parser = _build_parser()
    ns = parser.parse_args(args)

    if ns.no_color:
        os.environ["NO_COLOR"] = "1"
    if ns.debug:
        os.environ["GULFOFMEXICO_DEBUG"] = "1"
    if ns.verbose:
        os.environ["GULFOFMEXICO_VERBOSE"] = "1"
    if ns.quiet:
        os.environ.pop("GULFOFMEXICO_VERBOSE", None)

    if ns.write and not ns.fmt:
        print_error("--write needs --fmt", hint="use 'gom --fmt -w FILE' to rewrite in place")
        return 2

    if ns.more_files and not (ns.check or ns.fmt):
        print_error(
            "only --check and --fmt accept multiple files",
            hint="pass a single program to run it",
        )
        return 2

    # Static tools: check / format, on a file, inline code, or stdin
    if ns.check or ns.fmt:
        try:
            return _run_tool(ns)
        except BrokenPipeError:
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if ns.show_traceback:
                raise
            _report_error(exc)
            return 1

    # Inline code mode
    if ns.inline_code is not None:
        try:
            return _run_inline(ns.inline_code, ns.show_traceback, ns.vars_json)
        except BrokenPipeError:
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if ns.show_traceback:
                raise
            _report_error(exc)
            return 1

    # Standard input mode
    if ns.file == "-":
        try:
            return _run_inline(
                _read_stdin_source(),
                ns.show_traceback,
                ns.vars_json,
                filename="<stdin>",
            )
        except BrokenPipeError:
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if ns.show_traceback:
                raise
            _report_error(exc)
            return 1

    # File mode
    if ns.file:
        try:
            _validate_source_path(ns.file)
            run_file(ns.file, vars_json_path=ns.vars_json)
            return 0
        except BrokenPipeError:
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if ns.show_traceback:
                raise
            _report_error(exc)
            return 1

    # Default: REPL
    try:
        return repl_main([])
    except Exception as exc:  # pylint: disable=broad-exception-caught
        if ns.show_traceback:
            raise
        _report_error(exc)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())


def main():
    """Entry point for console scripts."""
    raise SystemExit(_main())
