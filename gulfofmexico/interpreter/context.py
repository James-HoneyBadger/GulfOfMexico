"""
Interpreter Context - Shared Mutable State and Type Definitions

Centralizes all mutable interpreter state into a single InterpreterContext
dataclass, eliminating module-level global variables. Also defines type
aliases and constants used across interpreter sub-modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, TypeAlias, Union

from gulfofmexico.builtin import (
    GulfOfMexicoPromise,
    GulfOfMexicoValue,
    Name,
    Variable,
)
from gulfofmexico.processor.expression_tree import ExpressionTreeNode
from gulfofmexico.processor.syntax_tree import (
    AfterStatement,
    CodeStatement,
    Conditional,
    ExpressionStatement,
    ReturnStatement,
    VariableAssignment,
    VariableDeclaration,
    WhenStatement,
)

# ---------------------------------------------------------------------------
# Type Aliases
# ---------------------------------------------------------------------------

Namespace: TypeAlias = dict[str, Union[Variable, Name]]

CodeStatementWithExpression: TypeAlias = Union[
    ReturnStatement,
    Conditional,
    ExpressionStatement,
    WhenStatement,
    VariableAssignment,
    AfterStatement,
    VariableDeclaration,
]

AsyncStatements: TypeAlias = list[
    tuple[
        list[tuple[CodeStatement, ...]],
        list[Namespace],
        int,
        Union[Literal[1], Literal[-1]],
    ]
]

NameWatchers: TypeAlias = dict[
    tuple[str, int],
    tuple[
        CodeStatementWithExpression,
        set[tuple[str, int]],
        list[Namespace],
        Optional[GulfOfMexicoPromise],
    ],
]

WhenStatementWatchers: TypeAlias = list[
    dict[
        Union[str, int],
        list[
            tuple[
                ExpressionTreeNode,
                list[tuple[CodeStatement, ...]],
                list[dict[str, Variable | Name]],
            ]
        ],
    ]
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Approximate-equality ratios
NUM_EQUALITY_RATIO = 0.1
STRING_EQUALITY_RATIO = 0.7
LIST_EQUALITY_RATIO = 0.7
MAP_EQUALITY_RATIO = 0.6
OBJECT_EQUALITY_RATIO = 0.6

# Persistence paths
DB_RUNTIME_PATH = ".gulfofmexico_runtime"
INF_VAR_PATH = ".inf_vars"
INF_VAR_VALUES_PATH = ".inf_vars_values"
IMMUTABLE_CONSTANTS_PATH = ".immutable_constants"
IMMUTABLE_CONSTANTS_VALUES_PATH = ".immutable_constants_values"
DB_VAR_TO_VALUE_SEP = ";;;"


# ---------------------------------------------------------------------------
# Return Sentinel (distinguishes explicit 'return' from implicit results)
# ---------------------------------------------------------------------------

class ReturnSentinel:
    """Wraps an explicit ``return`` value so if-blocks can distinguish it from
    implicit expression results and only propagate true returns."""
    __slots__ = ("value",)

    def __init__(self, value: GulfOfMexicoValue) -> None:
        self.value = value


# ---------------------------------------------------------------------------
# Interpreter Context (replaces module-level mutable globals)
# ---------------------------------------------------------------------------

@dataclass
class InterpreterContext:
    """All mutable interpreter state, threaded through every function."""

    filename: str = ""
    code: str = ""
    current_line: int = 0
    deleted_values: set[GulfOfMexicoValue] = field(default_factory=set)
    deleted_keywords: set[str] = field(default_factory=set)
    class_instance_counts: dict[str, int] = field(default_factory=dict)
    name_watchers: NameWatchers = field(default_factory=dict)
    is_lifetime_temporal: bool = False

    def reset(self) -> None:
        """Reset mutable state between runs (REPL / multi-file)."""
        self.deleted_values = set()
        self.deleted_keywords = set()
        self.class_instance_counts = {}
        self.name_watchers = {}
        self.is_lifetime_temporal = False
