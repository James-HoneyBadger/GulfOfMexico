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

import re
import sys
from time import sleep
from typing import Optional, Union

from gulfofmexico.builtin import KEYWORDS, Name, GulfOfMexicoValue, Variable
from gulfofmexico.processor.lexer import tokenize
from gulfofmexico.processor.syntax_tree import generate_syntax_tree
from gulfofmexico.interpreter import (
    interpret_code_statements_main_wrapper,
    load_global_gulfofmexico_variables,
    load_globals,
    load_public_global_variables,
)

__all__ = ["run_file"]

__REPL_FILENAME = "__repl__"
sys.setrecursionlimit(100000)


def run_file(main_filename: str) -> None:
    """Execute a Gulf of Mexico source file.

    Reads the file, splits by ===== markers, tokenizes, parses, and executes
    each section. Handles export/import between sections. Waits for async
    operations and when-statements after completion.

    Args:
        main_filename: Path to .gom source file
    """

    with open(main_filename, "r", encoding="utf-8") as f:
        code_lines = (
            f.readlines()
        )  # split up into separate 'files' by finding which lines start with
    # multiple equal signs
    files: list[tuple[Optional[str], str]] = []
    if any(matches := [re.match(r"=====.*", line) for line in code_lines]):
        for i, match in reversed([*enumerate(matches)]):
            if match is None:
                continue
            name = match.group().strip("=").strip() or None
            files.insert(0, (name, "".join(code_lines[i + 1 :])))
            del code_lines[i:]
        files.insert(0, (None, "".join(code_lines[0:])))
    else:
        files = [(None, "".join(code_lines))]

    # execute code for each file
    importable_names: dict[str, dict[str, GulfOfMexicoValue]] = {}
    for filename, code in files:
        filename = filename or "__unnamed_file__"
        # Set global variables for interpreter
        import gulfofmexico.interpreter as interpreter

        interpreter.filename = filename
        interpreter.code = code
        tokens = tokenize(filename, code)
        statements = generate_syntax_tree(filename, tokens, code)

        # load variables and run the code
        # Use Name objects directly for keywords
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
        try:
            interpret_code_statements_main_wrapper(
                statements, namespaces, [], [{}], importable_names, exported_names
            )
        except Exception:
            # Flush any buffered debug logs so debugging information is available
            # when a program errors out. Re-raise after flushing to preserve
            # the original traceback behavior.
            try:
                import gulfofmexico.builtin as _builtin

                _builtin.flush_debug_logs()
            except Exception:
                pass
            raise

        # take exported names and put them where they belong
        for target_filename, name, value in exported_names:
            if target_filename not in importable_names:
                importable_names[target_filename] = {}
            importable_names[target_filename][name] = value

    # Only show completion message if there are async/when statements that might be pending
    # Check if we have any when-statements or after-statements to wait for
    import os

    if os.environ.get("GULFOFMEXICO_VERBOSE"):
        print(
            "\033[33mCode has finished executing. Press ^C once or twice "
            "to stop waiting for when-statements and "
            "after-statements.\033[039m",
            flush=True,
        )
    try:
        while True:
            sleep(1)  # just waiting for any clicks, when statements, etc
    except KeyboardInterrupt:
        exit()  # quit silently
