"""
Gulf of Mexico Package - Main Entry Point

Provides the run_file() function that serves as the primary entry point for
executing Gulf of Mexico source files.

Execution Flow:
    1. Read source file and split by ===== file markers
    2. Tokenize code with gulfofmexico.processor.lexer
    3. Generate syntax tree with gulfofmexico.processor.syntax_tree
    4. Initialize namespaces with keywords and global variables
    5. Execute via interpreter.interpret_code_statements_main_wrapper()
    6. Handle exports between file sections
    7. Wait for async/when statements to complete

Multi-File Support:
    Files can be split into sections using ===== markers:
        ===== section_name =====
    Each section acts as a separate importable file for export/import statements.

Global Variables:
    - Local immutable constants (const const const)
    - Global variables from .gulfofmexico_runtime
    - Public globals from GitHub repository (if available)
"""

import time
from time import sleep
from typing import Optional, Union

from gulfofmexico.base import InterpretationError, configure_recursion_limit
from gulfofmexico.builtin import KEYWORDS, GulfOfMexicoValue, Name, Variable
from gulfofmexico.interpreter import (
    InterpreterContext,
    interpret_code_statements_main_wrapper,
)
from gulfofmexico.interpreter.persistence import (
    load_global_gulfofmexico_variables,
    load_globals,
    load_public_global_variables,
)
from gulfofmexico.prelude import load_prelude
from gulfofmexico.processor.lexer import tokenize
from gulfofmexico.processor.syntax_tree import generate_syntax_tree
from gulfofmexico.sections import split_sections
from gulfofmexico.ui import VERSION as __version__

__all__ = [
    "__version__",
    "run_file",
]

__REPL_FILENAME = "__repl__"
configure_recursion_limit()


def _snapshot_variables(
    namespaces: list[dict[str, Union[Variable, Name]]],
    baseline: set[str],
) -> list[dict[str, str]]:
    """Return a JSON-safe snapshot of the variables the program defined.

    *baseline* holds the names that already existed (keywords, built-ins and
    loaded globals) before the program ran, so the snapshot only reports what
    the program itself introduced.
    """
    from gulfofmexico.builtin import (  # pylint: disable=import-outside-toplevel
        BuiltinFunction,
        GulfOfMexicoKeyword,
        GulfOfMexicoSpecialBlankValue,
        db_to_string,
    )

    rows: dict[str, dict[str, str]] = {}
    for namespace in namespaces:
        for name, entry in namespace.items():
            if not name or name in baseline or name in KEYWORDS:
                continue
            if name.startswith("__"):
                continue
            if isinstance(entry, Variable):
                if not entry.lifetimes:
                    continue
                value = entry.lifetimes[0].value
            elif isinstance(entry, Name):
                value = entry.value
            else:
                continue
            if isinstance(
                value,
                (GulfOfMexicoKeyword, BuiltinFunction, GulfOfMexicoSpecialBlankValue),
            ):
                continue
            try:
                rendered = db_to_string(value).value
            except Exception:  # pragma: no cover - exotic values
                rendered = "..."
            if len(rendered) > 120:
                rendered = rendered[:117] + "..."
            rows[name] = {
                "name": name,
                "type": type(value).__name__.replace("GulfOfMexico", ""),
                "value": rendered,
            }
    return [rows[key] for key in sorted(rows)]


def run_file(main_filename: str, *, vars_json_path: Optional[str] = None) -> None:
    """Execute a Gulf of Mexico source file.

    Reads the file, splits by ===== markers, tokenizes, parses, and executes
    each section. Handles export/import between sections. Waits for async
    operations and when-statements after completion.

    Args:
        main_filename: Path to .gom source file
        vars_json_path: Optional path; when given, a JSON snapshot of the
            final variable scope is written there (used by the IDE inspector).
    """

    _started_at = time.perf_counter()
    with open(main_filename, "r", encoding="utf-8") as f:
        code = f.read()
    files = split_sections(code)

    # execute code for each file
    importable_names: dict[str, dict[str, GulfOfMexicoValue]] = {}
    final_namespaces: list[dict[str, Union[Variable, Name]]] = []
    final_baseline: set[str] = set()
    for filename, code in files:
        filename = filename or "__unnamed_file__"

        ctx = InterpreterContext(filename=filename, code=code)
        tokens = tokenize(filename, code)
        statements = generate_syntax_tree(filename, tokens, code)

        # load variables and run the code
        namespaces: list[dict[str, Union[Variable, Name]]] = [
            KEYWORDS.copy()  # type: ignore
        ]
        exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []
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
        baseline_names = {
            name for namespace in namespaces for name in namespace
        }
        try:
            interpret_code_statements_main_wrapper(
                statements, namespaces, [], [{}], importable_names, exported_names, ctx,
            )
        except (InterpretationError, BrokenPipeError):
            # Language-level errors are fully explained already; re-raise
            # without dumping the buffered print trail to stderr.
            raise
        except Exception:  # pylint: disable=broad-exception-caught
            # Flush any buffered debug logs so debugging information is available
            # when an internal error occurs. Re-raise after flushing to preserve
            # the original traceback behavior.
            try:
                import gulfofmexico.builtin as _builtin  # pylint: disable=import-outside-toplevel

                _builtin.flush_debug_logs()
            except Exception:
                pass
            raise

        # Remember the scope of the last executed section for --vars-json.
        final_namespaces = namespaces
        final_baseline = baseline_names

        # take exported names and put them where they belong
        for target_filename, name, value in exported_names:
            if target_filename not in importable_names:
                importable_names[target_filename] = {}
            importable_names[target_filename][name] = value

            # Also index exports by the source section name so
            # `import X from source!` can resolve deterministically.
            if filename not in importable_names:
                importable_names[filename] = {}
            importable_names[filename][name] = value

    if vars_json_path:
        import json  # pylint: disable=import-outside-toplevel

        try:
            with open(vars_json_path, "w", encoding="utf-8") as fh:
                json.dump(_snapshot_variables(final_namespaces, final_baseline), fh)
        except OSError:
            pass  # the snapshot is a convenience; never fail a run for it

    # Optional wait loop for interactive scenarios; disabled by default
    # to allow non-interactive executions (tests, scripts) to complete.
    import os  # pylint: disable=import-outside-toplevel

    verbose = os.environ.get("GULFOFMEXICO_VERBOSE")
    wait_enabled = os.environ.get("GULFOFMEXICO_WAIT")

    if verbose:
        elapsed = time.perf_counter() - _started_at
        detail = f" in {elapsed * 1000:.0f} ms" if elapsed >= 0 else ""
        if wait_enabled:
            print(
                f"Code has finished executing{detail}. "
                "Waiting for when/after statements - press Ctrl+C to stop.",
                flush=True,
            )
        else:
            print(f"Code has finished executing{detail}.", flush=True)

    if wait_enabled:
        try:
            while True:
                sleep(1)  # just waiting for any clicks, when statements, etc
        except KeyboardInterrupt:
            exit()  # quit silently
