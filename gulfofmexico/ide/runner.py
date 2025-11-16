from __future__ import annotations

import io
import sys
import threading
from dataclasses import dataclass, field
from typing import Optional, Union

from gulfofmexico.builtin import KEYWORDS, Name, GulfOfMexicoValue, Variable
from gulfofmexico.processor.lexer import tokenize
from gulfofmexico.processor.syntax_tree import generate_syntax_tree
import gulfofmexico.interpreter as interpreter
from gulfofmexico.base import InterpretationError


@dataclass
class ExecutionSession:
    namespaces: list[dict[str, Union[Variable, Name]]] = field(
        default_factory=lambda: [KEYWORDS.copy()]  # type: ignore
    )
    async_statements: interpreter.AsyncStatements = field(default_factory=list)
    when_watchers: interpreter.WhenStatementWatchers = field(
        default_factory=lambda: [{}]
    )
    importable_names: dict[str, dict[str, GulfOfMexicoValue]] = field(
        default_factory=dict
    )

    def init_globals(self, filename: str, code: str) -> None:
        exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []
        interpreter.load_globals(
            filename,
            code,
            {},
            set(),
            exported_names,
            self.importable_names.get(filename, {}),
        )
        interpreter.load_global_gulfofmexico_variables(self.namespaces)
        interpreter.load_public_global_variables(self.namespaces)


class OutputCapture(io.StringIO):
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()

    def write(self, s: str) -> int:  # noqa: D401
        with self._lock:
            return super().write(s)


def run_code(
    session: ExecutionSession, code: str, filename: str = "__ide_buffer__"
) -> tuple[str, Optional[str]]:
    """Run code via production interpreter and capture stdout.

    Returns (stdout, error) where error is formatted message or None.
    """
    out = OutputCapture()
    old_stdout = sys.stdout
    try:
        sys.stdout = out
        interpreter.filename = filename
        interpreter.code = code
        tokens = tokenize(filename, code)
        statements = generate_syntax_tree(filename, tokens, code)

        exported_names: list[tuple[str, str, GulfOfMexicoValue]] = []
        # Ensure globals present
        session.init_globals(filename, code)

        _ = interpreter.interpret_code_statements_main_wrapper(
            statements,
            session.namespaces,
            session.async_statements,
            session.when_watchers,
            session.importable_names,
            exported_names,
        )
        # propagate exports
        for target_filename, name, value in exported_names:
            if target_filename not in session.importable_names:
                session.importable_names[target_filename] = {}
            session.importable_names[target_filename][name] = value
        return out.getvalue(), None
    except InterpretationError as e:
        return out.getvalue(), str(e)
    finally:
        sys.stdout = old_stdout
