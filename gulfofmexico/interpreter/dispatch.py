"""
Interpreter Dispatch - Statement Type Determination

Resolves ambiguous statement tuples (multiple parses) to a single
concrete statement type by checking keyword values in the current
namespace.
"""

from __future__ import annotations

import re
from typing import Optional

from gulfofmexico.builtin import (
    GulfOfMexicoKeyword,
)
from gulfofmexico.processor.syntax_tree import (
    ClassDeclaration,
    CodeStatement,
    CodeStatementKeywordable,
    Conditional,
    DeleteStatement,
    ExportStatement,
    ExpressionStatement,
    FunctionDefinition,
    ImportStatement,
    ReturnStatement,
    ReverseStatement,
    VariableAssignment,
    VariableDeclaration,
    WhenStatement,
    AfterStatement,
)

from .context import InterpreterContext, Namespace
from .namespaces import get_name_from_namespaces, get_value_from_namespaces


def determine_statement_type(
    possible_statements: tuple[CodeStatement, ...],
    namespaces: list[Namespace],
    ctx: InterpreterContext,
) -> Optional[CodeStatement]:
    """Pick the first valid interpretation from *possible_statements*."""
    instance_to_keywords: dict[type[CodeStatementKeywordable], set[str]] = {
        Conditional: {"if"},
        WhenStatement: {"when"},
        AfterStatement: {"after"},
        ClassDeclaration: {"class", "className"},
        DeleteStatement: {"delete"},
        ReverseStatement: {"reverse"},
        ImportStatement: {"import"},
    }

    for st in possible_statements:
        if isinstance(st, CodeStatementKeywordable):
            val = get_name_from_namespaces(st.keyword.value, namespaces)
            if (
                val is not None
                and isinstance(val.value, GulfOfMexicoKeyword)
                and val.value.value in instance_to_keywords[type(st)]
                and val.value.value not in ctx.deleted_keywords
            ):
                return st

        elif isinstance(st, ReturnStatement):
            if st.keyword is None:
                return st
            val = get_name_from_namespaces(st.keyword.value, namespaces)
            if val and isinstance(val.value, GulfOfMexicoKeyword) and val.value.value == "return":
                return st
            if st.keyword.value == "return":
                return st

        elif isinstance(st, FunctionDefinition):
            if len(st.keywords) == 1:
                val = get_name_from_namespaces(st.keywords[0].value, namespaces)
                if val and isinstance(val.value, GulfOfMexicoKeyword) and re.match(r"^f?u?n?c?t?i?o?n?$", val.value.value):
                    return st
            elif len(st.keywords) == 2:
                val = get_name_from_namespaces(st.keywords[0].value, namespaces)
                other_val = get_name_from_namespaces(st.keywords[1].value, namespaces)
                if (
                    val and other_val
                    and isinstance(val.value, GulfOfMexicoKeyword) and isinstance(other_val.value, GulfOfMexicoKeyword)
                    and re.match(r"^f?u?n?c?t?i?o?n?$", other_val.value.value)
                    and val.value.value == "async"
                ):
                    return st

        elif isinstance(st, VariableDeclaration):
            if len(st.modifiers) == 1:
                if (
                    (val := get_name_from_namespaces(st.modifiers[0].value, namespaces)) is not None
                    and isinstance(val.value, GulfOfMexicoKeyword)
                    and val.value.value in {"const", "var"}
                ):
                    return st
            elif len(st.modifiers) == 2:
                if all(
                    (val := get_name_from_namespaces(mod.value, namespaces)) is not None
                    and isinstance(val.value, GulfOfMexicoKeyword)
                    and val.value.value in {"const", "var"}
                    for mod in st.modifiers
                ):
                    return st
            elif len(st.modifiers) == 3:
                if all(
                    (val := get_name_from_namespaces(mod.value, namespaces)) is not None
                    and isinstance(val.value, GulfOfMexicoKeyword)
                    and val.value.value == "const"
                    for mod in st.modifiers
                ):
                    return st

        elif isinstance(st, ExportStatement):
            if (
                isinstance(v := get_value_from_namespaces(st.to_keyword, namespaces, ctx), GulfOfMexicoKeyword)
                and v.value == "to"
                and isinstance(v := get_value_from_namespaces(st.export_keyword, namespaces, ctx), GulfOfMexicoKeyword)
                and v.value == "export"
            ):
                return st

    # Fallback: variable assignment then expression statement
    for st in possible_statements:
        if isinstance(st, VariableAssignment):
            return st
    for st in possible_statements:
        if isinstance(st, ExpressionStatement):
            return st
    return None
