"""
Interpreter Persistence - File I/O for Variable Storage

Handles loading and saving Gulf of Mexico variables to/from the file system.
Supports infinite-lifetime variables and immutable constants (const const const).
"""

from __future__ import annotations

import pickle
import random
from pathlib import Path

from gulfofmexico.builtin import (
    GulfOfMexicoValue,
    Variable,
    VariableLifetime,
)

from .context import (
    DB_RUNTIME_PATH,
    DB_VAR_TO_VALUE_SEP,
    IMMUTABLE_CONSTANTS_PATH,
    IMMUTABLE_CONSTANTS_VALUES_PATH,
    INF_VAR_PATH,
    INF_VAR_VALUES_PATH,
    Namespace,
)


# ---------------------------------------------------------------------------
# Global (infinite-lifetime) variables
# ---------------------------------------------------------------------------

def load_global_gulfofmexico_variables(namespaces: list[Namespace]) -> None:
    """Load infinite-lifetime variables from ``~/.gulfofmexico_runtime``."""
    dir_path = Path().home() / DB_RUNTIME_PATH
    inf_values_path = dir_path / INF_VAR_VALUES_PATH
    inf_var_list = dir_path / INF_VAR_PATH

    if not dir_path.is_dir() or not inf_values_path.is_dir() or not inf_var_list.is_file():
        return

    with open(inf_var_list, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if not line.strip():
                continue

            name, identity, can_be_reset_str, can_edit_value_str, confidence = line.split(DB_VAR_TO_VALUE_SEP)
            can_be_reset = can_be_reset_str == "True" if can_be_reset_str in ("True", "False") else True
            can_edit_value = can_edit_value_str == "True" if can_edit_value_str in ("True", "False") else True

            with open(dir_path / INF_VAR_VALUES_PATH / identity, "rb") as data_f:
                value = pickle.load(data_f)  # noqa: S301

            namespaces[-1][name] = Variable(
                name,
                [VariableLifetime(value, 100_000_000_000, int(confidence), can_be_reset, can_edit_value)],
                [],
            )


# ---------------------------------------------------------------------------
# Immutable constants (const const const)
# ---------------------------------------------------------------------------

def load_local_immutable_constants(namespaces: list[Namespace]) -> None:
    """Load locally stored immutable constants (const const const variables)."""
    dir_path = Path().home() / DB_RUNTIME_PATH
    immutable_values_path = dir_path / IMMUTABLE_CONSTANTS_VALUES_PATH
    immutable_list = dir_path / IMMUTABLE_CONSTANTS_PATH

    if not dir_path.is_dir() or not immutable_values_path.is_dir() or not immutable_list.is_file():
        return

    with open(immutable_list, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if not line.strip():
                continue
            try:
                name, identity, confidence = line.split(DB_VAR_TO_VALUE_SEP)
                with open(dir_path / IMMUTABLE_CONSTANTS_VALUES_PATH / identity, "rb") as data_f:
                    value = pickle.load(data_f)  # noqa: S301
                namespaces[-1][name] = Variable(
                    name,
                    [VariableLifetime(value, 100_000_000_000, int(confidence), False, False)],
                    [],
                )
            except (ValueError, FileNotFoundError, pickle.UnpicklingError):
                continue


def save_local_immutable_constant(name: str, value: GulfOfMexicoValue, confidence: int) -> None:
    """Persist an immutable constant to disk."""
    dir_path = Path().home() / DB_RUNTIME_PATH
    immutable_values_path = dir_path / IMMUTABLE_CONSTANTS_VALUES_PATH

    if not dir_path.is_dir():
        dir_path.mkdir()
    if not immutable_values_path.is_dir():
        immutable_values_path.mkdir()

    generated_addr = random.randint(1, 100_000_000_000)

    with open(dir_path / IMMUTABLE_CONSTANTS_PATH, "a", encoding="utf-8") as f:
        SEP = DB_VAR_TO_VALUE_SEP
        f.write(f"{name}{SEP}{generated_addr}{SEP}{confidence}\n")

    with open(dir_path / IMMUTABLE_CONSTANTS_VALUES_PATH / str(generated_addr), "wb") as f:
        pickle.dump(value, f)


def load_public_global_variables(namespaces: list[Namespace]) -> None:
    """Load all public global variables (currently delegates to immutable constants)."""
    load_local_immutable_constants(namespaces)


def load_globals(
    _filename: str,
    _code: str,
    _arg3: object,
    _arg4: object,
    _exported_names: list[tuple[str, str, GulfOfMexicoValue]],
    _importable_names: dict[str, GulfOfMexicoValue],
    namespaces: list[Namespace] | None = None,
) -> None:
    """Load global variables — called before interpretation begins.

    Delegates to ``load_global_gulfofmexico_variables`` and
    ``load_public_global_variables`` when *namespaces* is provided.
    """
    if namespaces is not None:
        load_global_gulfofmexico_variables(namespaces)
        load_public_global_variables(namespaces)
