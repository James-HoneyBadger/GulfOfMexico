"""
Interactive REPL for the Gulf of Mexico language (production interpreter).

Features:
- Real execution path: tokenize → generate_syntax_tree →
    interpret_code_statements_main_wrapper
- Persistent state across inputs (namespaces, watchers, globals)
- Multi-line input with automatic continuation until code parses
- Commands: :help, :quit, :reset, :load <file>, :vars, :history,
    :save <file> [all|last|<n>], :open <file>, :run <n>, :clip [last|<n>]

This REPL intentionally avoids the experimental engine; it uses the
monolithic production interpreter in gulfofmexico/interpreter.py.
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional, Union
import re

from gulfofmexico.builtin import (
    KEYWORDS,
    Name,
    GulfOfMexicoValue,
    Variable,
    GulfOfMexicoUndefined,
)
import gulfofmexico.builtin as builtin
from gulfofmexico.processor.lexer import tokenize
from gulfofmexico.processor.syntax_tree import generate_syntax_tree
from gulfofmexico.base import InterpretationError
import gulfofmexico.interpreter as interpreter


PRIMARY_PROMPT = "gom> "
CONT_PROMPT = " ...> "
REPL_FILENAME = "__repl__"


class GomRepl:
    """Stateful REPL runner bound to the production interpreter."""

    def __init__(self) -> None:
        # Shared state across inputs
        # Namespaces: first element is a copy of keyword namespace
        self.namespaces: list[dict[str, Union[Variable, Name]]] = [
            KEYWORDS.copy()  # type: ignore
        ]
        # When/after support with proper types from interpreter
        self.async_statements: interpreter.AsyncStatements = []
        self.when_statement_watchers: interpreter.WhenStatementWatchers = [{}]
        # Export/import map across pseudo-files
        self.importable_names: dict[str, dict[str, GulfOfMexicoValue]] = {}
        # History of successfully executed code blocks
        self.history: list[str] = []
        # Optional prefilled buffer to seed the next input block
        self.prefill_lines: list[str] = []

        # Basic interpreter environment setup
        sys.setrecursionlimit(100000)

        # Load global, public, and runtime globals into namespaces
        # We use an empty code block for initialization
        interpreter.filename = REPL_FILENAME
        interpreter.code = ""
        exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []
        interpreter.load_globals(
            interpreter.filename,
            interpreter.code,
            {},
            set(),
            exported_names,
            self.importable_names.get(interpreter.filename, {}),
        )
        interpreter.load_global_gulfofmexico_variables(self.namespaces)
        interpreter.load_public_global_variables(self.namespaces)

    def banner(self) -> str:
        return (
            "Gulf of Mexico REPL (production interpreter)\n"
            "Type :help for commands, :quit to exit."
        )

    def _read_multiline(self) -> Optional[str]:
        """
        Read one logical code block, allowing multi-line input until it parses.
        Returns None on EOF (Ctrl-D).
        """
        lines: list[str] = []
        prompt = PRIMARY_PROMPT
        # If we have a prefilled buffer (from :open), seed it into the editor
        if self.prefill_lines:
            # Show a small notice and the prefilled content
            print(f"<prefilled {len(self.prefill_lines)} line(s)>")
            for line_text in self.prefill_lines:
                print(line_text)
            lines = self.prefill_lines.copy()
            self.prefill_lines.clear()
            prompt = CONT_PROMPT
        while True:
            try:
                line = input(prompt)
            except EOFError:
                return None
            # Meta-commands handled only when first and as a single block
            if not lines and line.strip().startswith(":"):
                return line.strip()

            lines.append(line)
            candidate = "\n".join(lines)

            # Try parsing to determine completeness
            try:
                interpreter.filename = REPL_FILENAME
                interpreter.code = candidate
                tokens = tokenize(interpreter.filename, candidate)
                _ = generate_syntax_tree(
                    interpreter.filename,
                    tokens,
                    candidate,
                )
                # If parse succeeds, return buffer
                return candidate
            except InterpretationError as e:
                # Heuristic: if likely incomplete input, continue
                # Check for common trailing characters or unmatched braces
                open_braces = candidate.count("{") - candidate.count("}")
                ends_with_open = candidate.rstrip().endswith(("{", ",", ":"))
                missing_punct = not candidate.rstrip().endswith(
                    ("!", "?", "}", ")", "]")
                )
                if open_braces > 0 or ends_with_open or missing_punct:
                    prompt = CONT_PROMPT
                    continue
                # Otherwise, show error and reset buffer
                print(f"\x1b[31m{e}\x1b[0m")
                return ""

    def _cmd_help(self) -> None:
        print(
            "\n".join(
                [
                    ":help              Show this help",
                    ":quit | :q         Exit the REPL",
                    ":reset             Reset all REPL state",
                    ":load <file>       Load and execute a .gom file",
                    ":vars              List current variables",
                    ":history [n]       Show history (list or full block n)",
                    ":save <file> [all|last|<n>]  Save history (default: all)",
                    ":open <file>       Prefill next input with file contents",
                    ":run [n|last]      Re-execute a history block",
                    "                   (no arg = last)",
                    ":clip [last|<n>]   Copy block to clipboard if available",
                ]
            )
        )

    def _cmd_reset(self) -> None:
        self.namespaces = [KEYWORDS.copy()]  # type: ignore
        self.async_statements = []
        self.when_statement_watchers = [{}]
        self.importable_names.clear()
        print("State reset.")

    def _cmd_vars(self) -> None:
        top = self.namespaces[-1] if self.namespaces else {}
        vars_only = {k: v for k, v in top.items() if isinstance(v, Variable)}
        if not vars_only:
            print("<no variables>")
            return
        for k, v in vars_only.items():
            # Variable may wrap a value; best-effort display
            current = v.value.value if hasattr(v.value, "value") else v.value
            print(f"{k} = {current}")

    def _cmd_load(self, path: str) -> None:
        file = Path(path).expanduser()
        if not file.exists():
            print(f"No such file: {file}")
            return
        try:
            code = file.read_text(encoding="utf-8")
        except OSError as e:
            print(f"Failed to read {file}: {e}")
            return
        # Support multi-file sections using ===== markers (same as run_file)
        code_lines = code.splitlines(keepends=True)
        files: list[tuple[Optional[str], str]] = []
        matches = [re.match(r"=====.*", l) for l in code_lines]
        if any(matches):
            for i, match in reversed([*enumerate(matches)]):
                if match is None:
                    continue
                name = match.group().strip("=").strip() or None
                files.insert(0, (name, "".join(code_lines[i + 1 :])))
                del code_lines[i:]
            files.insert(0, (None, "".join(code_lines[0:])))
        else:
            files = [(None, "".join(code_lines))]

        # Execute each section in current REPL state, preserving namespaces
        # and handling import/export map across sections.
        any_error = False
        for section_name, section_code in files:
            fname = section_name or "__unnamed_file__"
            exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []

            # Prepare interpreter module state for this section
            interpreter.filename = fname
            interpreter.code = section_code

            try:
                tokens = tokenize(fname, section_code)
                statements = generate_syntax_tree(fname, tokens, section_code)
                interpreter.interpret_code_statements_main_wrapper(
                    statements,
                    self.namespaces,
                    self.async_statements,
                    self.when_statement_watchers,
                    self.importable_names,
                    exported_names,
                )
            except InterpretationError as e:
                print(f"\x1b[31m{e}\x1b[0m")
                any_error = True
                break

            # Apply exports to importable map
            for target_filename, name, value in exported_names:
                if target_filename not in self.importable_names:
                    self.importable_names[target_filename] = {}
                self.importable_names[target_filename][name] = value

        # Record load command in history (avoid dumping entire file into history)
        self.history.append(f":load {str(file)}")
        if not any_error:
            # Optionally provide a small ack
            pass

    def _dispatch_command(self, cmd: str) -> bool:
        """
        Handle meta-commands. Return True to continue, False to quit.
        """
        parts = cmd.split()
        if not parts:
            return True
        op = parts[0]
        if op in (":quit", ":q"):
            return False
        if op == ":help":
            self._cmd_help()
            return True
        if op == ":reset":
            self._cmd_reset()
            return True
        if op == ":vars":
            self._cmd_vars()
            return True
        if op == ":load":
            if len(parts) < 2:
                print("Usage: :load <file>")
                return True
            self._cmd_load(" ".join(parts[1:]))
            return True
        if op == ":history":
            if not self.history:
                print("<empty history>")
                return True
            # :history [n] → show full block n or list if no n
            if len(parts) >= 2:
                try:
                    idx = int(parts[1])
                    if idx <= 0 or idx > len(self.history):
                        print(f"No history entry {idx}.")
                        return True
                    print(self.history[idx - 1])
                except ValueError:
                    print("Usage: :history [n]")
                return True
            for i, block in enumerate(self.history, start=1):
                first = block.splitlines()[0] if block.strip() else ""
                preview = (first[:60] + "…") if len(first) > 60 else first
                print(f"{i:>3}: {preview}")
            return True
        if op == ":save":
            # :save <file> [all|last|<n>]
            if len(parts) < 2:
                print("Usage: :save <file> [all|last|<n>]")
                return True
            target = parts[1]
            mode = parts[2] if len(parts) >= 3 else "all"
            try:
                if mode == "all":
                    content = "\n\n".join(self.history)
                elif mode == "last":
                    content = self.history[-1] if self.history else ""
                else:
                    # numeric index
                    idx = int(mode)
                    if idx <= 0 or idx > len(self.history):
                        print(f"No history entry {idx}.")
                        return True
                    content = self.history[idx - 1]
                Path(target).expanduser().write_text(content, encoding="utf-8")
                print(f"Saved to {target}")
            except ValueError:
                print("Usage: :save <file> [all|last|<n>]")
            except OSError as e:
                print(f"Failed to save to {target}: {e}")
            return True
        if op == ":open":
            if len(parts) < 2:
                print("Usage: :open <file>")
                return True
            file = Path(" ".join(parts[1:])).expanduser()
            if not file.exists():
                print(f"No such file: {file}")
                return True
            try:
                content = file.read_text(encoding="utf-8")
            except OSError as e:
                print(f"Failed to read {file}: {e}")
                return True
            # Stage for next input; do not execute now
            self.prefill_lines = content.splitlines()
            print(f"Staged {len(self.prefill_lines)} line(s) for next input.")
            return True
        if op == ":run":
            try:
                if len(parts) < 2:
                    if not self.history:
                        print("<empty history>")
                        return True
                    idx = len(self.history)
                elif parts[1] == "last":
                    idx = len(self.history)
                else:
                    idx = int(parts[1])
                if idx <= 0 or idx > len(self.history):
                    print(f"No history entry {idx}.")
                    return True
                code = self.history[idx - 1]
                self._execute(code, filename=REPL_FILENAME)
            except ValueError:
                print("Usage: :run [n|last]")
            return True
        if op == ":clip":
            # :clip [last|<n>] → copy block to clipboard if possible
            if not self.history:
                print("<empty history>")
                return True
            mode = parts[1] if len(parts) >= 2 else "last"
            try:
                if mode == "last":
                    content = self.history[-1]
                else:
                    n = int(mode)
                    if n <= 0 or n > len(self.history):
                        print(f"No history entry {n}.")
                        return True
                    content = self.history[n - 1]
            except ValueError:
                print("Usage: :clip [last|<n>]")
                return True
            if self._copy_to_clipboard(content):
                print("Copied to clipboard.")
            else:
                msg = (
                    "Clipboard not available. Printed block below; "
                    + "copy manually:\n"
                )
                print(msg + content)
            return True
        print(f"Unknown command: {op}. Try :help")
        return True

    def _execute(self, code: str, *, filename: Optional[str] = None) -> None:
        if code.strip() == "":
            return
        fname = filename or REPL_FILENAME
        exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []

        # Prepare interpreter module state
        interpreter.filename = fname
        interpreter.code = code

        tokens = tokenize(fname, code)
        statements = generate_syntax_tree(fname, tokens, code)

        # Execute
        try:
            result = interpreter.interpret_code_statements_main_wrapper(
                statements,
                self.namespaces,  # preserve across inputs
                self.async_statements,
                self.when_statement_watchers,
                self.importable_names,
                exported_names,
            )
        except InterpretationError as e:
            # Flush any buffered debug logs to assist troubleshooting
            try:
                builtin.flush_debug_logs()
            except Exception:
                pass
            print(f"\x1b[31m{e}\x1b[0m")
            return
        except Exception:
            # Unexpected exception: flush debug logs and re-raise to show
            # the full traceback for debugging purposes.
            try:
                builtin.flush_debug_logs()
            except Exception:
                pass
            raise

        # Handle exported names
        for target_filename, name, value in exported_names:
            if target_filename not in self.importable_names:
                self.importable_names[target_filename] = {}
            self.importable_names[target_filename][name] = value

        # Only print meaningful results (suppress implicit 'undefined')
        if result is not None and not isinstance(result, GulfOfMexicoUndefined):
            # Best-effort print of result
            print(result)

        # Record successful block in history
        self.history.append(code)

    def loop(self) -> None:
        print(self.banner())
        while True:
            block = self._read_multiline()
            if block is None:
                # EOF
                print()
                return
            if block.startswith(":"):
                if not self._dispatch_command(block):
                    return
                continue
            self._execute(block)

    @staticmethod
    def _copy_to_clipboard(text: str) -> bool:
        """Best-effort clipboard copy. Returns True on success."""
        # Try pyperclip first
        try:
            import pyperclip  # type: ignore

            pyperclip.copy(text)
            return True
        except (ImportError, RuntimeError):  # pragma: no cover - optional dep
            pass
        # Try tkinter fallback
        try:
            import tkinter as tk  # type: ignore

            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            # Ensure clipboard persists after window closes
            root.update()
            root.destroy()
            return True
        except (ImportError, RuntimeError):  # pragma: no cover
            return False


def main(argv: list[str] | None = None) -> int:
    _ = argv or sys.argv[1:]
    repl = GomRepl()
    repl.loop()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
