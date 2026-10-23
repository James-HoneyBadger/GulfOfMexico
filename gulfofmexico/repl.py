"""
Interactive REPL for the Gulf of Mexico language (production interpreter).

Features:
- Real execution path: tokenize → generate_syntax_tree →
    interpret_code_statements_main_wrapper
- Persistent state across inputs (namespaces, watchers, globals)
- Multi-line input with automatic continuation until code parses
- Commands: :help, :quit, :reset, :load <file>, :vars, :history,
    :save <file> [all|last|<n>], :open <file>, :run <n>, :clip [last|<n>]

This REPL uses the production interpreter in gulfofmexico/interpreter.py.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Optional, Union

import gulfofmexico.builtin as builtin
from gulfofmexico.interpreter import (
    InterpreterContext,
    interpret_code_statements_main_wrapper,
)
from gulfofmexico.interpreter.context import AsyncStatements, WhenStatementWatchers
from gulfofmexico.interpreter.persistence import (
    load_global_gulfofmexico_variables,
    load_globals,
    load_public_global_variables,
)
from gulfofmexico.base import InterpretationError, configure_recursion_limit
from gulfofmexico.builtin import (
    KEYWORDS,
    GulfOfMexicoUndefined,
    GulfOfMexicoValue,
    Name,
    Variable,
)
from gulfofmexico.prelude import load_prelude
from gulfofmexico.processor.lexer import tokenize
from gulfofmexico.processor.syntax_tree import generate_syntax_tree
from gulfofmexico.ui import (
    VERSION,
    color_enabled,
    heading,
    paint,
    print_error,
    print_info,
    print_success,
    rule,
    table,
)

_PRIMARY_TEXT = "gom> "
_CONT_TEXT = " ...> "

_PROMPT_COLORS = {"cyan": 36, "grey": 90}


def _styled_prompt(text: str, color: str) -> str:
    """Wrap *text* in colour, marking escapes as non-printing for readline."""
    if not color_enabled(sys.stdout):
        return text
    code = _PROMPT_COLORS[color]
    return "\x01\033[" + str(code) + "m\x02" + text + "\x01\033[0m\x02"


def primary_prompt() -> str:
    return _styled_prompt(_PRIMARY_TEXT, "cyan")


def continuation_prompt() -> str:
    return _styled_prompt(_CONT_TEXT, "grey")


REPL_FILENAME = "__repl__"
HISTORY_FILE = os.path.expanduser("~/.gom_history")
HISTORY_MAX_LINES = 1000


def _strip_strings_and_comments(code: str) -> str:
    """Return ``code`` with string literals and comments blanked out.

    Used by the REPL's multi-line completeness heuristic so that braces and
    statement terminators appearing inside strings or comments are not counted.
    Quote/comment characters are replaced with spaces to preserve offsets.
    """
    out: list[str] = []
    i = 0
    n = len(code)
    quote: Optional[str] = None
    while i < n:
        ch = code[i]
        if quote is not None:
            # Inside a string literal: blank everything until the closing quote.
            if ch == quote:
                quote = None
            out.append(" " if ch != "\n" else "\n")
            i += 1
            continue
        # Line comment //...
        if ch == "/" and i + 1 < n and code[i + 1] == "/":
            while i < n and code[i] != "\n":
                out.append(" ")
                i += 1
            continue
        # Block comment /* ... */
        if ch == "/" and i + 1 < n and code[i + 1] == "*":
            while i < n and not (code[i] == "*" and i + 1 < n and code[i + 1] == "/"):
                out.append(" " if code[i] != "\n" else "\n")
                i += 1
            # Consume the closing */ if present.
            if i < n:
                out.append(" ")
                i += 1
            if i < n:
                out.append(" ")
                i += 1
            continue
        if ch in ("\"", "'"):
            quote = ch
            out.append(" ")
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


class GomRepl:
    """Stateful REPL runner bound to the production interpreter."""

    def __init__(self) -> None:
        # Shared state across inputs
        self.namespaces: list[dict[str, Union[Variable, Name]]] = [
            KEYWORDS.copy()  # type: ignore
        ]
        self.async_statements: AsyncStatements = []
        self.when_statement_watchers: WhenStatementWatchers = [{}]
        self.importable_names: dict[str, dict[str, GulfOfMexicoValue]] = {}
        self.history: list[str] = []
        self.prefill_lines: list[str] = []

        # readline integration (populated by _setup_readline)
        self._readline = None
        self._completion_matches: list[str] = []

        # Interpreter context for the REPL session
        self.ctx = InterpreterContext(filename=REPL_FILENAME, code="")

        configure_recursion_limit()

        # Load global, public, and runtime globals into namespaces
        exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []
        load_globals(
            REPL_FILENAME,
            "",
            {},
            set(),
            exported_names,
            self.importable_names.get(REPL_FILENAME, {}),
        )
        load_global_gulfofmexico_variables(self.namespaces)
        load_public_global_variables(self.namespaces)
        load_prelude(self.namespaces, self.ctx)

    def banner(self) -> str:
        """The REPL greeting: product banner plus a short cheat sheet."""
        width = 72
        lines = [
            "",
            paint("Gulf of Mexico", "bold", "bright_cyan"),
            paint(f"v{VERSION}  ·  interactive session", "dim"),
            rule(width, "─"),
            paint("  -1-based indexing   three-valued booleans   no loops", "dim"),
            paint("  End statements with !   Use ; for NOT   Type ? to inspect", "dim"),
            rule(width, "─"),
            table(
                [
                    (":help", "show all commands"),
                    (":vars", "inspect current variables"),
                    (":load <file>", "run a .gom file"),
                    (":reset", "clear all state"),
                    (":quit", "leave the session"),
                ],
                indent=2,
            ),
            "",
        ]
        return "\n".join(lines)

    def _setup_readline(self) -> None:
        """Enable line editing, persistent history, and tab completion.

        Uses the standard-library ``readline`` module when available. Failures
        are non-fatal: the REPL still works without line editing.
        """
        try:
            import readline  # pylint: disable=import-outside-toplevel
        except ImportError:  # pragma: no cover - platform without readline
            self._readline = None
            return
        self._readline = readline
        # Load persisted history if present.
        try:
            readline.read_history_file(HISTORY_FILE)
        except (OSError, FileNotFoundError):
            pass
        readline.set_history_length(HISTORY_MAX_LINES)
        # Wire up tab completion.
        readline.set_completer(self._complete)
        readline.set_completer_delims(" \t\n(){}[]!?,:;")
        # 'libedit' (macOS default) needs different binding syntax.
        if "libedit" in getattr(readline, "__doc__", ""):
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

    def _save_history(self) -> None:
        """Persist readline history to disk (best-effort)."""
        rl = getattr(self, "_readline", None)
        if rl is None:
            return
        try:
            rl.write_history_file(HISTORY_FILE)
        except OSError:  # pragma: no cover - disk failure
            pass

    def _completion_candidates(self) -> list[str]:
        """Build the list of completable identifiers (keywords + in-scope names)."""
        names: set[str] = set()
        for key in KEYWORDS:
            if isinstance(key, str):
                names.add(key)
        for namespace in self.namespaces:
            for key in namespace:
                if isinstance(key, str):
                    names.add(key)
        # Meta-commands are handy to complete at the start of a line too.
        names.update(
            {":help", ":quit", ":reset", ":load", ":vars", ":history", ":save", ":open", ":run", ":clip"}
        )
        return sorted(names)

    def _complete(self, text: str, state: int) -> Optional[str]:
        """readline completer: return the ``state``-th match for ``text``."""
        if state == 0:
            if text:
                self._completion_matches = [
                    name for name in self._completion_candidates() if name.startswith(text)
                ]
            else:
                self._completion_matches = self._completion_candidates()
        try:
            return self._completion_matches[state]
        except (IndexError, AttributeError):
            return None

    def _read_multiline(self) -> Optional[str]:
        """
        Read one logical code block, allowing multi-line input until it parses.
        Returns None on EOF (Ctrl-D).
        """
        lines: list[str] = []
        prompt = primary_prompt()
        # If we have a prefilled buffer (from :open), seed it into the editor
        if self.prefill_lines:
            # Show a small notice and the prefilled content
            print(f"<prefilled {len(self.prefill_lines)} line(s)>")
            for line_text in self.prefill_lines:
                print(line_text)
            lines = self.prefill_lines.copy()
            self.prefill_lines.clear()
            prompt = continuation_prompt()
        while True:
            try:
                line = input(prompt)
            except EOFError:
                return None
            except KeyboardInterrupt:
                # Ctrl+C abandons the current block but keeps the session.
                print()
                if lines:
                    print_info("input cleared - press Ctrl+D to exit")
                    lines = []
                    prompt = primary_prompt()
                else:
                    print_info("press Ctrl+D or :quit to exit")
                continue
            # Meta-commands handled only when first and as a single block
            if not lines and line.strip().startswith(":"):
                return line.strip()

            lines.append(line)
            candidate = "\n".join(lines)

            # Try parsing to determine completeness
            try:
                tokens = tokenize(REPL_FILENAME, candidate)
                _ = generate_syntax_tree(
                    REPL_FILENAME,
                    tokens,
                    candidate,
                )
                # If parse succeeds, return buffer
                return candidate
            except InterpretationError as e:
                # Heuristic: if likely incomplete input, continue.
                # Strip string/comment content first so braces or terminators
                # inside literals don't confuse the completeness check.
                stripped = _strip_strings_and_comments(candidate)
                open_braces = stripped.count("{") - stripped.count("}")
                ends_with_open = stripped.rstrip().endswith(("{", ",", ":"))
                missing_punct = not stripped.rstrip().endswith(("!", "?", "}", ")", "]"))
                if open_braces > 0 or ends_with_open or missing_punct:
                    prompt = continuation_prompt()
                    continue
                # Otherwise, show the diagnostic and reset the buffer
                print(e, file=sys.stderr)
                return ""

    def _cmd_help(self) -> None:
        width = 72
        print()
        print(heading("Commands", width=width))
        print(
            table(
                [
                    (":help", "Show this help"),
                    (":quit, :q", "Exit the REPL"),
                    (":reset", "Reset all REPL state"),
                    (":vars", "List current variables"),
                    (":load <file>", "Load and execute a .gom file"),
                    (":open <file>", "Stage a file as the next input"),
                    (":history [n]", "List history, or show block n"),
                    (":run [n|last]", "Re-execute a history block"),
                    (":save <file> [all|last|<n>]", "Save history to a file"),
                    (":clip [last|<n>]", "Copy a block to the clipboard"),
                ],
                indent=2,
            )
        )
        print()
        print(heading("Writing code", width=width))
        print(
            table(
                [
                    ("print \"hi\"!", "Print (parentheses optional)"),
                    ("const x = 1!", "Declare; use var to allow reassignment"),
                    ("if cond { ... }", "Blocks indent by exactly 3 spaces"),
                    ("function f(a) => a + 1!", "Functions return an expression"),
                    ("2 * 1+3", "Tighter spacing binds first (prints 8)"),
                    ("?", "Inspect the value of a statement"),
                ],
                indent=2,
            )
        )
        print()

    def _cmd_reset(self) -> None:
        self.namespaces = [KEYWORDS.copy()]  # type: ignore
        self.async_statements = []
        self.when_statement_watchers = [{}]
        self.importable_names.clear()
        print_info("state reset - all variables and watchers cleared")

    def _cmd_vars(self) -> None:
        top = self.namespaces[-1] if self.namespaces else {}
        vars_only = {k: v for k, v in top.items() if isinstance(v, Variable)}
        if not vars_only:
            print_info("no variables defined yet")
            return
        rows = []
        for name, var in vars_only.items():
            value = var.value
            rendered = builtin.db_to_string(value).value
            if len(rendered) > 48:
                rendered = rendered[:45] + "..."
            rows.append((name, type(value).__name__.removeprefix("GulfOfMexico"), rendered))
        print()
        print(table(rows, header=("name", "type", "value"), indent=2))
        print()

    def _cmd_load(self, path: str) -> None:
        file = Path(path).expanduser()
        if not file.exists():
            print_error(f"no such file: {file}")
            return
        try:
            code = file.read_text(encoding="utf-8")
        except OSError as e:
            print_error(f"cannot read {file}: {e}")
            return
        # Support multi-file sections using ===== markers (same as run_file)
        code_lines = code.splitlines(keepends=True)
        files: list[tuple[Optional[str], str]] = []
        matches = [re.match(r"=====.*", line) for line in code_lines]
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

            ctx = InterpreterContext(filename=fname, code=section_code)

            try:
                tokens = tokenize(fname, section_code)
                statements = generate_syntax_tree(fname, tokens, section_code)
                interpret_code_statements_main_wrapper(
                    statements,
                    self.namespaces,
                    self.async_statements,
                    self.when_statement_watchers,
                    self.importable_names,
                    exported_names,
                    ctx,
                )
            except InterpretationError as e:
                print(e, file=sys.stderr)
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
            print_success(f"loaded {file} ({len(files)} section(s))")

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
                print_info("usage: :load <file>")
                return True
            self._cmd_load(" ".join(parts[1:]))
            return True
        if op == ":history":
            if not self.history:
                print_info("history is empty")
                return True
            # :history [n] → show full block n or list if no n
            if len(parts) >= 2:
                try:
                    idx = int(parts[1])
                    if idx <= 0 or idx > len(self.history):
                        print_error(f"no history entry {idx}")
                        return True
                    print(self.history[idx - 1])
                except ValueError:
                    print_info("usage: :history [n]")
                return True
            for i, block in enumerate(self.history, start=1):
                first = block.splitlines()[0] if block.strip() else ""
                preview = (first[:60] + "…") if len(first) > 60 else first
                print(f"{i:>3}: {preview}")
            return True
        if op == ":save":
            # :save <file> [all|last|<n>]
            if len(parts) < 2:
                print_info("usage: :save <file> [all|last|<n>]")
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
                print_success(f"saved to {target}")
            except ValueError:
                print("Usage: :save <file> [all|last|<n>]")
            except OSError as e:
                print_error(f"cannot save {target}: {e}")
            return True
        if op == ":open":
            if len(parts) < 2:
                print_info("usage: :open <file>")
                return True
            file = Path(" ".join(parts[1:])).expanduser()
            if not file.exists():
                print_error(f"no such file: {file}")
                return True
            try:
                content = file.read_text(encoding="utf-8")
            except OSError as e:
                print_error(f"cannot read {file}: {e}")
                return True
            # Stage for next input; do not execute now
            self.prefill_lines = content.splitlines()
            print_info(f"staged {len(self.prefill_lines)} line(s) as the next input")
            return True
        if op == ":run":
            try:
                if len(parts) < 2:
                    if not self.history:
                        print_info("history is empty")
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
                print_info("usage: :run [n|last]")
            return True
        if op == ":clip":
            # :clip [last|<n>] → copy block to clipboard if possible
            if not self.history:
                print_info("history is empty")
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
                print_info("usage: :clip [last|<n>]")
                return True
            if self._copy_to_clipboard(content):
                print_success("copied to clipboard")
            else:
                msg = "clipboard unavailable - copy the block below manually:\n"
                print(msg + content)
            return True
        print_error(f"unknown command: {op}", hint="type :help for the command list")
        return True

    def _execute(self, code: str, *, filename: Optional[str] = None) -> None:
        if code.strip() == "":
            return
        fname = filename or REPL_FILENAME
        exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []

        ctx = InterpreterContext(filename=fname, code=code)

        tokens = tokenize(fname, code)
        statements = generate_syntax_tree(fname, tokens, code)

        # Execute
        try:
            result = interpret_code_statements_main_wrapper(
                statements,
                self.namespaces,
                self.async_statements,
                self.when_statement_watchers,
                self.importable_names,
                exported_names,
                ctx,
            )
        except InterpretationError as e:
            # The diagnostic explains the problem; keep stderr free of the
            # buffered print trail.
            print(e, file=sys.stderr)
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
            print(builtin.db_to_string(result).value)

        # Record successful block in history
        self.history.append(code)

    def loop(self) -> None:
        print(self.banner())
        self._setup_readline()
        try:
            while True:
                block = self._read_multiline()
                if block is None:
                    # EOF (Ctrl+D)
                    print(paint("bye.", "dim"))
                    return
                if block.startswith(":"):
                    if not self._dispatch_command(block):
                        print(paint("bye.", "dim"))
                        return
                    continue
                self._execute(block)
        finally:
            self._save_history()

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
