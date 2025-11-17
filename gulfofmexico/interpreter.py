"""
Gulf of Mexico Interpreter - Main Execution Engine

This is the production interpreter that executes Gulf of Mexico code (~2,900 lines).
All execution flows through this monolithic implementation.

Execution Flow:
    1. gulfofmexico/__init__.py run_file() entry point
    2. interpret_code_statements_main_wrapper() initializes context
    3. interpret_code_statements() main loop with pattern matching
    4. Individual statement handlers execute code

Core Features Implemented:
    - Probabilistic variables with confidence levels and lifetimes
    - Temporal and line-based variable lifetimes
    - -1 array indexing (Gulf of Mexico's key feature)
    - Fractional array indexing with automatic insertion
    - Approximate equality (~= with fuzzy ratios)
    - next/previous value tracking and watchers
    - async/await for concurrent execution
    - when statement reactive programming
    - const const const for immutable globals
    - Class objects with namespaces
    - String interpolation with ${}
    - Flexible quoting system

Note: gulfofmexico/engine/ contains experimental handler-based architecture
that is NOT used in production. All code execution uses this file's pattern matching.
"""

from __future__ import annotations
import os
import re
import json
import random
import pickle
import requests
from pathlib import Path
from copy import deepcopy
from difflib import SequenceMatcher
from typing import Literal, Optional, TypeAlias, Union

KEY_MOUSE_IMPORTED = True
try:
    from pynput import keyboard, mouse
except ImportError:
    KEY_MOUSE_IMPORTED = False

GITHUB_IMPORTED = True
try:
    import github
except ImportError:
    GITHUB_IMPORTED = False

from gulfofmexico.base import (
    InterpretationError,
    NonFormattedError,
    OperatorType,
    Token,
    TokenType,
    debug_print,
    debug_print_no_token,
    raise_error_at_line,
    raise_error_at_token,
)
from gulfofmexico.builtin import (
    FLOAT_TO_INT_PREC,
    BuiltinFunction,
    GulfOfMexicoBoolean,
    GulfOfMexicoFunction,
    GulfOfMexicoIndexable,
    GulfOfMexicoKeyword,
    GulfOfMexicoList,
    GulfOfMexicoMap,
    GulfOfMexicoMutable,
    GulfOfMexicoNamespaceable,
    GulfOfMexicoNumber,
    GulfOfMexicoObject,
    GulfOfMexicoPendingInit,
    GulfOfMexicoPromise,
    GulfOfMexicoSpecialBlankValue,
    GulfOfMexicoString,
    GulfOfMexicoUndefined,
    Name,
    Variable,
    GulfOfMexicoValue,
    VariableLifetime,
    db_not,
    db_to_boolean,
    db_to_number,
    db_to_string,
    is_int,
)
from gulfofmexico.serialize import serialize_obj, deserialize_obj
from gulfofmexico.processor.lexer import tokenize as db_tokenize
from gulfofmexico.processor.expression_tree import (
    ExpressionTreeNode,
    FunctionNode,
    ListNode,
    SingleOperatorNode,
    ValueNode,
    IndexNode,
    ExpressionNode,
    build_expression_tree,
    get_expr_first_token,
)
from gulfofmexico.processor.syntax_tree import (
    AfterStatement,
    AgileStatement,
    AIBuzzwordStatement,
    BlockchainStatement,
    ClassDeclaration,
    CodeStatement,
    CodeStatementKeywordable,
    Conditional,
    CorporateSpeakStatement,
    DeleteStatement,
    DevOpsStatement,
    EmotionalStatement,
    ExportStatement,
    ExpressionStatement,
    FunctionDefinition,
    GaslightingStatement,
    ImportStatement,
    ProcrastinationStatement,
    QuantumStatement,
    ReturnStatement,
    ReverseStatement,
    SecurityTheaterStatement,
    StartupStatement,
    SuperstitiousStatement,
    TimeTravelStatement,
    TryWhateverStatement,
    VariableAssignment,
    VariableDeclaration,
    WhenStatement,
)

# several "ratios" used in the approx equal function
NUM_EQUALITY_RATIO = 0.1  # a-b / b
STRING_EQUALITY_RATIO = 0.7  # min ratio to be considered equal
LIST_EQUALITY_RATIO = (
    0.7  # min ratio of all the elements of a list to be equal for the lists to be equal
)
MAP_EQUALITY_RATIO = 0.6  # lower thresh cause i feel like it
FUNCTION_EQUALITY_RATIO = 0.6  # yeah
OBJECT_EQUALITY_RATIO = 0.6

# thing used in the .gulfofmexico_runtime file
DB_RUNTIME_PATH = ".gulfofmexico_runtime"
INF_VAR_PATH = ".inf_vars"
INF_VAR_VALUES_PATH = ".inf_vars_values"
IMMUTABLE_CONSTANTS_PATH = ".immutable_constants"
IMMUTABLE_CONSTANTS_VALUES_PATH = ".immutable_constants_values"
DB_VAR_TO_VALUE_SEP = ";;;"  # i'm feeling fancy

# :D
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
        list[tuple[ExpressionTreeNode, list[tuple[CodeStatement, ...]]]],
    ]
]  # bro there are six square brackets...


def get_built_expression(
    expr: Union[list[Token], ExpressionTreeNode],
) -> ExpressionTreeNode:
    return (
        expr
        if isinstance(expr, ExpressionTreeNode)
        else build_expression_tree(filename, expr, code)
    )


def get_modified_next_name(name: str, ns: int) -> str:
    return f"{name}_{ns}__next"


def get_modified_prev_name(name: str) -> str:
    return f"{name.replace('.', '__')}__prev"


# i believe this function is exclusively called from the evaluate_expression function
def evaluate_normal_function(
    expr: FunctionNode,
    func: Union[GulfOfMexicoFunction, BuiltinFunction],
    namespaces: list[Namespace],
    args: list[GulfOfMexicoValue],
    when_statement_watchers: WhenStatementWatchers,
) -> GulfOfMexicoValue:

    # check to evaluate builtin
    if isinstance(func, BuiltinFunction):
        if func.arg_count > len(args):
            raise_error_at_token(
                filename,
                code,
                f"Expected more arguments for function call with {func.arg_count} argument{'s' if func.arg_count != 1 else ''}.",
                expr.name,
            )
        max_arg_count = func.arg_count if func.arg_count >= 0 else len(args)
        result = func.function(*args[:max_arg_count]) or GulfOfMexicoUndefined()

        # Handle pending init for constructors
        if isinstance(result, GulfOfMexicoPendingInit):
            instance = result.instance
            init_args = result.init_args

            # Get the init method from the instance namespace
            if "init" in instance.namespace:
                init_entry = instance.namespace["init"]
                init_func = (
                    init_entry.value
                    if isinstance(init_entry, Name)
                    else (
                        init_entry.lifetimes[0].value
                        if isinstance(init_entry, Variable) and init_entry.lifetimes
                        else None
                    )
                )

                if isinstance(init_func, GulfOfMexicoFunction):
                    # Check arg count
                    if len(init_func.args) > len(init_args):
                        raise_error_at_token(
                            filename,
                            code,
                            f"init method expects {len(init_func.args)} argument{'s' if len(init_func.args) != 1 else ''}, got {len(init_args)}.",
                            expr.name,
                        )

                    # Call init with instance namespace in scope
                    init_namespace: Namespace = {
                        name: Name(name, arg)
                        for name, arg in zip(init_func.args, init_args)
                    }
                    interpret_code_statements(
                        init_func.code,
                        namespaces + [instance.namespace, init_namespace],
                        [],
                        when_statement_watchers + [{}, {}],
                        {},
                        [],
                    )

            return instance

        return result

    # check length is proper, adjust namespace, and run this code
    if len(func.args) > len(args):
        raise_error_at_token(
            filename,
            code,
            f"Expected more arguments for function call with {len(func.args)} argument{'s' if len(func.args) != 1 else ''}.",
            expr.name,
        )
    new_namespace: Namespace = {
        name: Name(name, arg) for name, arg in zip(func.args, args)
    }
    return (
        interpret_code_statements(
            func.code,
            namespaces + [new_namespace],
            [],
            when_statement_watchers + [{}],
            {},
            [],
        )
        or GulfOfMexicoUndefined()
    )


def register_async_function(
    expr: FunctionNode,
    func: GulfOfMexicoFunction,
    namespaces: list[Namespace],
    args: list[GulfOfMexicoValue],
    async_statements: AsyncStatements,
) -> None:
    """Adds a job to the async statements queue, which is accessed in the interpret_code_statements function."""
    if len(func.args) > len(args):
        raise_error_at_token(
            filename,
            code,
            f"Expected more arguments for function call with {len(func.args)} argument{'s' if len(func.args) != 1 else ''}.",
            expr.name,
        )
    function_namespaces = namespaces + [
        {name: Name(name, arg) for name, arg in zip(func.args, args)}
    ]
    async_statements.append((func.code, function_namespaces, 0, 1))


def get_code_from_when_statement_watchers(
    name_or_id: Union[str, int], when_statement_watchers: WhenStatementWatchers
) -> list[tuple[ExpressionTreeNode, list[tuple[CodeStatement, ...]]]]:
    vals = []
    for watcher_dict in when_statement_watchers:
        if val := watcher_dict.get(name_or_id):
            vals += val
    return vals


def remove_from_when_statement_watchers(
    name_or_id: Union[str, int],
    watcher: tuple[ExpressionTreeNode, list[tuple[CodeStatement, ...]]],
    when_statement_watchers: WhenStatementWatchers,
) -> None:
    for watcher_dict in when_statement_watchers:
        if vals := watcher_dict.get(name_or_id):
            remove = None
            for i, v in enumerate(vals):
                if v == watcher:
                    remove = i
            if remove is not None:
                del vals[remove]


def remove_from_all_when_statement_watchers(
    name_or_id: Union[str, int], when_statement_watchers: WhenStatementWatchers
) -> None:
    for watcher_dict in when_statement_watchers:
        if name_or_id in watcher_dict:
            del watcher_dict[name_or_id]


def load_global_gulfofmexico_variables(namespaces: list[Namespace]) -> None:

    dir_path = Path().home() / DB_RUNTIME_PATH
    inf_values_path = dir_path / INF_VAR_VALUES_PATH
    inf_var_list = dir_path / INF_VAR_PATH
    if not dir_path.is_dir():
        return
    if not inf_values_path.is_dir():
        return
    if not inf_var_list.is_file():
        return

    with open(inf_var_list, "r") as f:
        for line in f.readlines():
            if not line.strip():
                continue

            name, identity, can_be_reset, can_edit_value, confidence = line.split(
                DB_VAR_TO_VALUE_SEP
            )
            can_be_reset = (
                eval(can_be_reset) if can_be_reset in ["True", "False"] else True
            )  # safe code !!!!!!!!!!!!
            can_edit_value = (
                eval(can_edit_value) if can_edit_value in ["True", "False"] else True
            )

            with open(dir_path / INF_VAR_VALUES_PATH / identity, "rb") as data_f:
                value = pickle.load(data_f)
            namespaces[-1][name] = Variable(
                name,
                [
                    VariableLifetime(
                        value,
                        100000000000,
                        int(confidence),
                        can_be_reset,
                        can_edit_value,
                    )
                ],
                [],
            )


def load_local_immutable_constants(namespaces: list[Namespace]) -> None:
    """Load locally stored immutable constants (const const const variables)."""
    dir_path = Path().home() / DB_RUNTIME_PATH
    immutable_values_path = dir_path / IMMUTABLE_CONSTANTS_VALUES_PATH
    immutable_list = dir_path / IMMUTABLE_CONSTANTS_PATH

    if not dir_path.is_dir():
        return
    if not immutable_values_path.is_dir():
        return
    if not immutable_list.is_file():
        return

    with open(immutable_list, "r") as f:
        for line in f.readlines():
            if not line.strip():
                continue

            try:
                name, identity, confidence = line.split(DB_VAR_TO_VALUE_SEP)
                with open(
                    dir_path / IMMUTABLE_CONSTANTS_VALUES_PATH / identity, "rb"
                ) as data_f:
                    value = pickle.load(data_f)
                # Immutable constants: can_be_reset=False, can_edit_value=False
                namespaces[-1][name] = Variable(
                    name,
                    [
                        VariableLifetime(
                            value,
                            100000000000,  # Effectively infinite
                            int(confidence),
                            False,  # can_be_reset
                            False,  # can_edit_value
                        )
                    ],
                    [],
                )
            except (ValueError, FileNotFoundError, pickle.UnpicklingError):
                # Skip malformed entries
                continue


def save_local_immutable_constant(
    name: str, value: GulfOfMexicoValue, confidence: int
) -> None:
    """Save an immutable constant locally."""
    dir_path = Path().home() / DB_RUNTIME_PATH
    immutable_values_path = dir_path / IMMUTABLE_CONSTANTS_VALUES_PATH

    # Create directories if they don't exist
    if not dir_path.is_dir():
        dir_path.mkdir()
    if not immutable_values_path.is_dir():
        immutable_values_path.mkdir()

    # Generate unique ID
    generated_addr = random.randint(1, 100000000000)

    # Save to list file
    with open(dir_path / IMMUTABLE_CONSTANTS_PATH, "a") as f:
        SEP = DB_VAR_TO_VALUE_SEP
        f.write(f"{name}{SEP}{generated_addr}{SEP}{confidence}\n")

    # Save value
    with open(
        dir_path / IMMUTABLE_CONSTANTS_VALUES_PATH / str(generated_addr), "wb"
    ) as f:
        pickle.dump(value, f)


def load_public_global_variables(namespaces: list[Namespace]) -> None:
    # First load locally stored immutable constants
    load_local_immutable_constants(namespaces)

    try:
        repo_url = "https://raw.githubusercontent.com/James-HoneyBadger/gulfofmexico-interpreter-globals-patched/main"
        response = requests.get(f"{repo_url}/public_globals.txt", timeout=5)
        response.raise_for_status()

        for line in response.text.split("\n"):
            if not line.strip():
                continue
            try:
                name, address, confidence = line.split(DB_VAR_TO_VALUE_SEP)
                can_be_reset = can_edit_value = False  # these were const

                serialized_value_response = requests.get(
                    f"{repo_url}/serialized_objects/{address}", timeout=5
                )
                serialized_value_response.raise_for_status()
                serialized_value = serialized_value_response.text

                value = deserialize_obj(json.loads(serialized_value))
                # Only add if not already loaded from local storage
                if name not in namespaces[-1]:
                    namespaces[-1][name] = Variable(
                        name,
                        [
                            VariableLifetime(
                                value,
                                100000000000,
                                int(confidence),
                                can_be_reset,
                                can_edit_value,
                            )
                        ],
                        [],
                    )
            except (ValueError, json.JSONDecodeError, requests.RequestException):
                # Skip malformed lines or failed requests
                continue
    except requests.RequestException:
        # If we can't load public globals, that's okay - we already loaded local ones
        pass


def open_global_variable_issue(name: str, value: GulfOfMexicoValue, confidence: int):
    if not GITHUB_IMPORTED:
        raise_error_at_line(
            filename,
            code,
            current_line,
            "Cannot create a public global variable without a the GitHub API imported.",
        )
    try:
        access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    except KeyError:
        raise_error_at_line(
            filename,
            code,
            current_line,
            "To declare public globals, you must set the GITHUB_ACCESS_TOKEN to a personal access token.",
        )

    issue_body = json.dumps(serialize_obj(value))
    with github.Github(auth=github.Auth.Token(access_token)) as g:  # type: ignore
        repo = g.get_repo("James-HoneyBadger/gulfofmexico-interpreter-globals")
        repo.create_issue(
            f"Create Public Global: {name}{DB_VAR_TO_VALUE_SEP}{confidence}", issue_body
        )


def check_type_annotation(value: GulfOfMexicoValue, type_tokens: list[Token]) -> None:
    """Check if a value matches the expected type annotation."""
    if not type_tokens:
        return  # No type annotation, nothing to check

    # Extract the type name from tokens (skip whitespace)
    type_name_tokens = [t for t in type_tokens if t.type != TokenType.WHITESPACE]
    if not type_name_tokens:
        return

    type_name = "".join(t.value for t in type_name_tokens)

    # Check type compatibility
    if type_name == "Int":
        if not isinstance(value, GulfOfMexicoNumber):
            raise InterpretationError(
                f"Type error: expected Int, got {type(value).__name__}"
            )
    elif type_name == "String":
        if not isinstance(value, GulfOfMexicoString):
            raise InterpretationError(
                f"Type error: expected String, got {type(value).__name__}"
            )
    elif type_name == "Char[]":
        if not isinstance(value, GulfOfMexicoString):
            raise InterpretationError(
                f"Type error: expected Char[], got {type(value).__name__}"
            )
    elif type_name == "Int9":
        if not isinstance(value, GulfOfMexicoNumber):
            raise InterpretationError(
                f"Type error: expected Int9, got {type(value).__name__}"
            )
        # Int9 represents binary, but for now we'll just check it's a number
    elif type_name == "Int99":
        if not isinstance(value, GulfOfMexicoNumber):
            raise InterpretationError(
                f"Type error: expected Int99, got {type(value).__name__}"
            )
        # Int99 represents some other representation, but for now we'll just check it's a number
    # Add more type checks as needed


def declare_new_variable(
    statement: VariableDeclaration,
    value: GulfOfMexicoValue,
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
) -> None:
    name = statement.name.value
    confidence = statement.confidence
    lifetime = statement.lifetime

    # Determine variable properties based on modifiers
    can_be_reset = "var" in [mod.value for mod in statement.modifiers]
    can_edit_value = "const" not in [mod.value for mod in statement.modifiers]

    # Parse lifetime if provided
    duration = 100000000000  # default infinite
    is_temporal = False
    temporal_duration = 0.0
    if lifetime:
        try:
            if lifetime.startswith("<") and lifetime.endswith(">"):
                # Temporal lifetime like <5.0>
                temporal_duration = float(lifetime[1:-1])
                duration = 100000000000  # still infinite lines
                is_temporal = True
            else:
                # Line-based lifetime
                duration = int(lifetime)
        except ValueError:
            raise_error_at_token(
                filename,
                code,
                f"Invalid lifetime specification: {lifetime}",
                statement.name,
            )

    # Create the variable
    var = Variable(name, [], [])
    var.add_lifetime(
        value,
        confidence,
        duration,
        can_be_reset,
        can_edit_value,
        is_temporal=is_temporal,
        temporal_duration=temporal_duration,
    )

    # Add to namespace
    namespaces[-1][name] = var

    # Check type annotation if provided
    if statement.type_annotation:
        check_type_annotation(value, statement.type_annotation)

    # Check if this is a global immutable constant (const const const)
    is_triple_const = len(statement.modifiers) == 3 and all(
        mod.value == "const" for mod in statement.modifiers
    )

    if is_triple_const:
        # Save as immutable global constant
        save_local_immutable_constant(name, value, confidence)

        # Try to create GitHub issue for global sharing, but don't fail if
        # it doesn't work
        try:
            open_global_variable_issue(name, value, confidence)
        except Exception:
            # GitHub storage failed, but local storage succeeded
            # This is acceptable - the variable is still immutable locally
            pass

    # Trigger when statement watchers for this new variable
    when_watchers = get_code_from_when_statement_watchers(
        id(var), when_statement_watchers
    )
    for when_watcher in when_watchers:
        condition, inside_statements = when_watcher
        condition_val = evaluate_expression(
            condition, namespaces, async_statements, when_statement_watchers
        )
        if isinstance(value, GulfOfMexicoMutable):
            if id(value) not in when_statement_watchers[-1]:
                when_statement_watchers[-1][id(value)] = []
            when_statement_watchers[-1][id(value)].append(when_watcher)
        execute_conditional(
            condition_val,
            inside_statements,
            namespaces,
            when_statement_watchers,
            {},
            [],
        )


def assign_variable(
    statement: VariableAssignment,
    indexes: list[GulfOfMexicoValue],
    new_value: GulfOfMexicoValue,
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
):
    name, confidence, debug = (
        statement.name.value,
        statement.confidence,
        statement.debug,
    )
    name_token = statement.name

    var, ns = get_name_and_namespace_from_namespaces(name, namespaces)
    # Support dotted property assignment e.g., alice.name = "Alice"!
    dotted_target = None
    if var is None and "." in name:
        parts = name.split(".")
        base_name, tail = parts[0], parts[1:]
        base_entry, _ = get_name_and_namespace_from_namespaces(base_name, namespaces)
        if base_entry is None:
            raise_error_at_token(
                filename, code, "Attempted to set a name that is undefined.", name_token
            )
        container_val = base_entry.value  # type: ignore[attr-defined]
        # Traverse through intermediate segments
        for seg in tail[:-1]:
            if (
                not isinstance(container_val, GulfOfMexicoNamespaceable)
                or seg not in container_val.namespace
            ):
                raise_error_at_token(
                    filename,
                    code,
                    "Attempted to set a name that is undefined.",
                    name_token,
                )
            next_entry = container_val.namespace[seg]
            container_val = next_entry.value  # type: ignore[attr-defined]
        # Now container_val should be namespaceable, assign into last segment
        if not isinstance(container_val, GulfOfMexicoNamespaceable):
            raise_error_at_token(
                filename, code, "Attempted to set a name that is undefined.", name_token
            )
        dotted_target = (container_val, tail[-1])
    elif var is None:
        raise_error_at_token(
            filename, code, "Attempted to set a name that is undefined.", name_token
        )

    # Check type annotation if the variable was declared with one
    # Type is stored in the original VariableDeclaration, but we can't access it here
    # For now, we'll skip type checking on reassignment
    # TODO: Store type_annotation tokens on Variable for reassignment checks

    match debug:
        case 0:
            pass
        case 1:
            debug_print(
                filename,
                code,
                f"Setting {statement.name.value}{''.join([f'[{db_to_string(val).value}]' for val in indexes])} to {db_to_string(new_value).value}",
                statement.name,
            )
        case 2:
            expr = get_built_expression(statement.expression)
            names = gather_names_or_values(expr)
            debug_print(
                filename,
                code,
                f"Setting {statement.name.value}{''.join([f'[{db_to_string(val).value}]' for val in indexes])} to {db_to_string(new_value).value}\nThe value of each name in the expression is the following: \n{chr(10).join([f'  {name}: {db_to_string(get_value_from_namespaces(name, namespaces)).value}' for name in names])}",
                statement.name,
            )
        case 3:
            expr = get_built_expression(statement.expression)
            names = gather_names_or_values(expr)
            debug_print(
                filename,
                code,
                f"Setting {statement.name.value}{''.join([f'[{db_to_string(val).value}]' for val in indexes])} to {db_to_string(new_value).value}\nThe value of each name in the expression is the following: \n{chr(10).join([f'  {name}: {db_to_string(get_value_from_namespaces(name, namespaces)).value}' for name in names])}\nThe expression used to get this value is: \n{expr.to_string()}",
                statement.name,
            )
        case _:
            expr = get_built_expression(statement.expression)
            index_exprs = [get_built_expression(ex) for ex in statement.indexes]
            names = gather_names_or_values(expr)
            for ex in index_exprs:
                names |= gather_names_or_values(ex)
            debug_print(
                filename,
                code,
                f"Setting {statement.name.value}{''.join([f'[{db_to_string(val).value}]' for val in indexes])} to {db_to_string(new_value).value}\nThe value of each name in the program is the following: \n{chr(10).join([f'  {name}: {db_to_string(get_value_from_namespaces(name, namespaces)).value}' for name in names])}\nThe expression used to get this value is: \n{expr.to_string()}\nThe expression used to get the indexes are as follows: \n{(chr(10) * 2).join([ex.to_string(1) for ex in index_exprs])}",
                statement.name,
            )

    visited_whens = []
    if indexes:

        # goes down the list until it can assign something in the list
        def assign_variable_helper(
            value_to_modify: GulfOfMexicoValue,
            remaining_indexes: list[GulfOfMexicoValue],
        ):
            if not value_to_modify or not isinstance(
                value_to_modify, GulfOfMexicoIndexable
            ):
                raise_error_at_line(
                    filename,
                    code,
                    name_token.line,
                    "Attempted to index into an un-indexable object.",
                )
            index = remaining_indexes.pop(0)

            if not remaining_indexes:  # perform actual assignment here
                value_to_modify.assign_index(index, new_value)
            else:
                assign_variable_helper(
                    value_to_modify.access_index(index), remaining_indexes
                )
            # check for some watchers here too!!!!!!!!!!!
            when_watchers = get_code_from_when_statement_watchers(
                id(value_to_modify), when_statement_watchers
            )
            for when_watcher in when_watchers:  # i just wanna be done with this :(
                if any([when_watcher == x for x in visited_whens]):
                    continue
                (condition, inside_statements, captured_namespaces) = when_watcher
                condition_val = evaluate_expression(
                    condition,
                    captured_namespaces,
                    async_statements,
                    when_statement_watchers,
                )
                execute_conditional(
                    condition_val,
                    inside_statements,
                    captured_namespaces,
                    when_statement_watchers,
                    {},
                    [],
                )
                visited_whens.append(when_watcher)

        # Note: For indexed assignment (e.g., list[0] = x), we don't check can_edit_value
        # because const var allows modifying elements, just not replacing the entire value
        if dotted_target is not None:
            container_val, key = dotted_target
            entry = container_val.namespace.get(key)
            if entry is None:
                raise_error_at_token(
                    filename,
                    code,
                    "Attempted to index into an undefined property.",
                    name_token,
                )
            assign_variable_helper(entry.value, indexes)  # type: ignore[attr-defined]
        else:
            assign_variable_helper(var.value, indexes)

    else:
        if dotted_target is not None:
            container_val, key = dotted_target
            existing = container_val.namespace.get(key)
            if existing is None:
                container_val.namespace[key] = Name(key, new_value)
            elif isinstance(existing, Variable):
                if not existing.can_be_reset:
                    raise_error_at_token(
                        filename,
                        code,
                        "Attempted to set a variable that cannot be set.",
                        name_token,
                    )
                existing.add_lifetime(
                    new_value,
                    confidence,
                    100000000000,
                    existing.can_be_reset,
                    existing.can_edit_value,
                    is_temporal=False,
                    temporal_duration=0.0,
                )
            else:  # Name
                existing.value = new_value  # type: ignore[attr-defined]
        else:
            if not isinstance(var, Variable):
                raise_error_at_token(
                    filename,
                    code,
                    "Attempted to set name that is not a variable.",
                    name_token,
                )
            if not var.can_be_reset:
                raise_error_at_token(
                    filename,
                    code,
                    "Attempted to set a variable that cannot be set.",
                    name_token,
                )
            var.add_lifetime(
                new_value,
                confidence,
                100000000000,
                var.can_be_reset,
                var.can_edit_value,
                is_temporal=False,
                temporal_duration=0.0,
            )

    # check if there is a watcher for this name
    watchers_key = (name, id(namespaces[-1]))
    if watcher := name_watchers.get(watchers_key):
        st, stored_nexts, watcher_ns, promise = watcher
        mod_name = get_modified_next_name(*watchers_key)
        watcher_ns[-1][mod_name] = Name(
            mod_name, new_value
        )  # add the value to the uppermost namespace
        stored_nexts.remove(
            watchers_key
        )  # remove the name from the set containing remaining names
        if not stored_nexts:  # not waiting on anybody else, execute the code
            interpret_name_watching_statement(
                st, watcher_ns, promise, async_statements, when_statement_watchers
            )
        del name_watchers[watchers_key]  # stop watching this name

    # check if this name appears in a when statement of the appropriate scope  --  it would have to be watching the name
    if when_watchers := get_code_from_when_statement_watchers(
        id(var), when_statement_watchers
    ):
        for when_watcher in when_watchers:  # i just wanna be done with this :(
            if len(when_watcher) == 3:
                condition, inside_statements, captured_namespaces = when_watcher
            else:
                condition, inside_statements = when_watcher
                captured_namespaces = namespaces
            condition_val = evaluate_expression(
                condition,
                captured_namespaces,
                async_statements,
                when_statement_watchers,
            )
            if isinstance(new_value, GulfOfMexicoMutable):
                if id(new_value) not in when_statement_watchers[-1]:
                    when_statement_watchers[-1][id(new_value)] = []
                if when_watcher not in when_statement_watchers[-1][id(new_value)]:
                    when_statement_watchers[-1][id(new_value)].append(
                        when_watcher
                    )  # remember: this is tuple so it is immutable and copied!
            if isinstance(
                var.prev_values[-1], GulfOfMexicoMutable
            ):  # if prev value was being observed under this statement, remove it
                remove_from_when_statement_watchers(
                    id(var.prev_values[-1]),
                    when_watcher,
                    when_statement_watchers,
                )
            if id(var) not in when_statement_watchers[-1]:
                when_statement_watchers[-1][id(var)] = []
            if when_watcher not in when_statement_watchers[-1][id(var)]:
                when_statement_watchers[-1][id(var)].append(
                    when_watcher
                )  # put this where the new variable is
            execute_conditional(
                condition_val,
                inside_statements,
                captured_namespaces,
                when_statement_watchers,
                {},
                [],
            )
        # Removed: remove_from_all_when_statement_watchers(id(var), when_statement_watchers)


def perform_single_value_operation(
    val: GulfOfMexicoValue, operator_token: Token
) -> GulfOfMexicoValue:
    match operator_token.type:
        case TokenType.SUBTRACT:
            match val:
                case GulfOfMexicoNumber():
                    return GulfOfMexicoNumber(-val.value)
                case GulfOfMexicoList():
                    return GulfOfMexicoList(val.values[::-1])
                case GulfOfMexicoString():
                    return GulfOfMexicoString(val.value[::-1])
                case _:
                    raise_error_at_token(
                        filename,
                        code,
                        f"Cannot negate a value of type {type(val).__name__}",
                        operator_token,
                    )
        case TokenType.SEMICOLON:
            val_bool = db_to_boolean(val)
            return db_not(val_bool)
    raise_error_at_token(
        filename, code, "Something went wrong. My bad.", operator_token
    )


def is_approx_equal(
    left: GulfOfMexicoValue, right: GulfOfMexicoValue
) -> GulfOfMexicoBoolean:
    """Approximate equality with fuzzy matching based on ratios."""
    if type(left) != type(right):
        return GulfOfMexicoBoolean(False)

    match left:
        case GulfOfMexicoNumber():
            if not isinstance(right, GulfOfMexicoNumber):
                return GulfOfMexicoBoolean(False)
            if left.value == right.value:
                return GulfOfMexicoBoolean(True)
            if (
                abs(left.value) < FLOAT_TO_INT_PREC
                and abs(right.value) < FLOAT_TO_INT_PREC
            ):
                return GulfOfMexicoBoolean(True)
            ratio = abs(left.value - right.value) / max(
                abs(left.value), abs(right.value)
            )
            return GulfOfMexicoBoolean(ratio <= NUM_EQUALITY_RATIO)

        case GulfOfMexicoString():
            if not isinstance(right, GulfOfMexicoString):
                return GulfOfMexicoBoolean(False)
            if left.value == right.value:
                return GulfOfMexicoBoolean(True)
            # Use sequence matcher for string similarity
            ratio = SequenceMatcher(None, left.value, right.value).ratio()
            return GulfOfMexicoBoolean(ratio >= STRING_EQUALITY_RATIO)

        case GulfOfMexicoList():
            if not isinstance(right, GulfOfMexicoList):
                return GulfOfMexicoBoolean(False)
            if len(left.values) != len(right.values):
                return GulfOfMexicoBoolean(False)
            if len(left.values) == 0:
                return GulfOfMexicoBoolean(True)
            equal_count = 0
            for l_val, r_val in zip(left.values, right.values):
                if is_approx_equal(l_val, r_val).value:
                    equal_count += 1
            ratio = equal_count / len(left.values)
            return GulfOfMexicoBoolean(ratio >= LIST_EQUALITY_RATIO)

        case GulfOfMexicoMap():
            if not isinstance(right, GulfOfMexicoMap):
                return GulfOfMexicoBoolean(False)
            if len(left.self_dict) != len(right.self_dict):
                return GulfOfMexicoBoolean(False)
            if len(left.self_dict) == 0:
                return GulfOfMexicoBoolean(True)
            equal_count = 0
            for key in left.self_dict:
                if key in right.self_dict:
                    if is_approx_equal(left.self_dict[key], right.self_dict[key]).value:
                        equal_count += 1
            ratio = equal_count / len(left.self_dict)
            return GulfOfMexicoBoolean(ratio >= MAP_EQUALITY_RATIO)

        case GulfOfMexicoFunction():
            if not isinstance(right, GulfOfMexicoFunction):
                return GulfOfMexicoBoolean(False)
            # Functions are equal if they have the same args and code
            if (
                left.args == right.args
                and left.code == right.code
                and left.is_async == right.is_async
            ):
                return GulfOfMexicoBoolean(True)
            return GulfOfMexicoBoolean(False)

        case GulfOfMexicoObject():
            if not isinstance(right, GulfOfMexicoObject):
                return GulfOfMexicoBoolean(False)
            if left.class_name != right.class_name:
                return GulfOfMexicoBoolean(False)
            # Compare namespaces
            equal_count = 0
            total_count = len(left.namespace)
            for key in left.namespace:
                if key in right.namespace:
                    if is_approx_equal(
                        left.namespace[key].value, right.namespace[key].value
                    ).value:
                        equal_count += 1
            if total_count == 0:
                return GulfOfMexicoBoolean(True)
            ratio = equal_count / total_count
            return GulfOfMexicoBoolean(ratio >= OBJECT_EQUALITY_RATIO)

        case _:
            # For other types, use strict equality
            return GulfOfMexicoBoolean(left == right)


def is_equal(left: GulfOfMexicoValue, right: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    """Regular equality - stricter than approximate."""
    if type(left) != type(right):
        return GulfOfMexicoBoolean(False)

    match left:
        case GulfOfMexicoNumber():
            if not isinstance(right, GulfOfMexicoNumber):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(
                abs(left.value - right.value) < FLOAT_TO_INT_PREC
            )

        case GulfOfMexicoString():
            if not isinstance(right, GulfOfMexicoString):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(left.value == right.value)

        case GulfOfMexicoList():
            if not isinstance(right, GulfOfMexicoList):
                return GulfOfMexicoBoolean(False)
            if len(left.values) != len(right.values):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(
                all(
                    is_equal(l_val, r_val).value
                    for l_val, r_val in zip(left.values, right.values)
                )
            )

        case GulfOfMexicoMap():
            if not isinstance(right, GulfOfMexicoMap):
                return GulfOfMexicoBoolean(False)
            if len(left.self_dict) != len(right.self_dict):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(
                all(
                    key in right.self_dict
                    and is_equal(left.self_dict[key], right.self_dict[key]).value
                    for key in left.self_dict
                )
            )

        case GulfOfMexicoFunction():
            if not isinstance(right, GulfOfMexicoFunction):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(
                left.args == right.args
                and left.code == right.code
                and left.is_async == right.is_async
            )

        case GulfOfMexicoObject():
            if not isinstance(right, GulfOfMexicoObject):
                return GulfOfMexicoBoolean(False)
            if left.class_name != right.class_name:
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(
                all(
                    key in right.namespace
                    and is_equal(
                        left.namespace[key].value, right.namespace[key].value
                    ).value
                    for key in left.namespace
                )
            )

        case _:
            return GulfOfMexicoBoolean(left == right)


def is_really_equal(
    left: GulfOfMexicoValue, right: GulfOfMexicoValue
) -> GulfOfMexicoBoolean:
    """Really equal - even stricter, checks identity for mutable objects."""
    if type(left) != type(right):
        return GulfOfMexicoBoolean(False)

    # For mutable objects, check identity
    if isinstance(
        left,
        (GulfOfMexicoList, GulfOfMexicoMap, GulfOfMexicoObject, GulfOfMexicoString),
    ):
        return GulfOfMexicoBoolean(left is right)

    # For immutable objects, use regular equality
    return is_equal(left, right)


def is_really_really_equal(
    left: GulfOfMexicoValue, right: GulfOfMexicoValue
) -> GulfOfMexicoBoolean:
    """Really really equal - strictest equality, always checks identity."""
    return GulfOfMexicoBoolean(left is right)


def is_less_than(
    left: GulfOfMexicoValue, right: GulfOfMexicoValue
) -> GulfOfMexicoBoolean:
    """Less than comparison."""
    if type(left) != type(right):
        return GulfOfMexicoBoolean(False)

    match left:
        case GulfOfMexicoNumber():
            if not isinstance(right, GulfOfMexicoNumber):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(left.value < right.value)

        case GulfOfMexicoString():
            if not isinstance(right, GulfOfMexicoString):
                return GulfOfMexicoBoolean(False)
            return GulfOfMexicoBoolean(left.value < right.value)

        case GulfOfMexicoList():
            if not isinstance(right, GulfOfMexicoList):
                return GulfOfMexicoBoolean(False)
            # Compare lexicographically
            for l_val, r_val in zip(left.values, right.values):
                if is_really_equal(l_val, r_val).value:
                    continue
                return is_less_than(l_val, r_val)
            return GulfOfMexicoBoolean(len(left.values) < len(right.values))

        case _:
            # For other types, not comparable
            return GulfOfMexicoBoolean(False)


def perform_two_value_operation(
    left: GulfOfMexicoValue,
    right: GulfOfMexicoValue,
    operator: OperatorType,
    operator_token: Token,
) -> GulfOfMexicoValue:
    match operator:
        case OperatorType.ADD:
            if isinstance(left, GulfOfMexicoString) or isinstance(
                right, GulfOfMexicoString
            ):
                return GulfOfMexicoString(
                    db_to_string(left).value + db_to_string(right).value
                )
            left_num = db_to_number(left)
            right_num = db_to_number(right)
            return GulfOfMexicoNumber(left_num.value + right_num.value)
        case OperatorType.SUB | OperatorType.MUL | OperatorType.DIV | OperatorType.EXP:
            left_num = db_to_number(left)
            right_num = db_to_number(right)
            if (
                operator == OperatorType.DIV
                and abs(right_num.value) < FLOAT_TO_INT_PREC
            ):  # pretty much zero
                return GulfOfMexicoUndefined()
            elif (
                operator == OperatorType.EXP
                and left_num.value < -FLOAT_TO_INT_PREC
                and not is_int(right_num.value)
            ):
                raise_error_at_line(
                    filename,
                    code,
                    current_line,
                    "Cannot raise a negative base to a non-integer exponent.",
                )
            match operator:
                case OperatorType.SUB:
                    result = left_num.value - right_num.value
                case OperatorType.MUL:
                    result = left_num.value * right_num.value
                case OperatorType.DIV:
                    result = left_num.value / right_num.value
                case OperatorType.EXP:
                    result = pow(left_num.value, right_num.value)
            return GulfOfMexicoNumber(result)
        case OperatorType.OR:
            left_bool = db_to_boolean(left)
            right_bool = db_to_boolean(right)
            match left_bool.value, right_bool.value:
                case True, _:
                    return left  # yes
                case False, _:
                    return right  # depends
                case None, True:
                    return right  # yes
                case None, False:
                    return left  # maybe?
                case None, None:
                    return left if random.random() < 0.50 else right  # maybe?
        case OperatorType.AND:
            left_bool = db_to_boolean(left)
            right_bool = db_to_boolean(right)
            match left_bool.value, right_bool.value:
                case True, _:
                    return right  # depends
                case False, _:
                    return left  # nope
                case None, True:
                    return left  # maybe?
                case None, False:
                    return right  # nope
                case None, None:
                    return left if random.random() < 0.50 else right  # maybe?
        case OperatorType.E:
            return is_approx_equal(left, right)

        # i'm gonna call this lasagna code because it's stacked like lasagna and looks stupid
        case OperatorType.EE | OperatorType.NE:
            if operator == OperatorType.EE:
                return is_equal(left, right)
            return db_not(is_equal(left, right))
        case OperatorType.EEE | OperatorType.NEE:
            if operator == OperatorType.EEE:
                return is_really_equal(left, right)
            return db_not(is_really_equal(left, right))
        case OperatorType.EEEE | OperatorType.NEEE:
            if operator == OperatorType.EEEE:
                return is_really_really_equal(left, right)
            return db_not(is_really_really_equal(left, right))
        case OperatorType.GT | OperatorType.LE:
            is_eq = is_really_equal(left, right)
            is_less = is_less_than(left, right)
            is_le = False
            match is_eq.value, is_less.value:  # performs the OR operation
                case (True, _) | (_, True):
                    is_le = True
                case (None, _) | (_, None):
                    is_le = None
            if operator == OperatorType.LE:
                return GulfOfMexicoBoolean(is_le)
            return db_not(GulfOfMexicoBoolean(is_le))
        case OperatorType.LT | OperatorType.GE:
            if operator == OperatorType.LT:
                return is_less_than(left, right)
            return db_not(is_less_than(left, right))

    raise_error_at_token(filename, code, "Something went wrong here.", operator_token)


def get_value_from_namespaces(
    name_or_value: Token, namespaces: list[Namespace]
) -> GulfOfMexicoValue:

    # what the frick am i doing rn
    if v := get_name_from_namespaces(name_or_value.value, namespaces):
        if isinstance(v.value, GulfOfMexicoPromise):
            return deepcopy(
                v.value.value
            )  # consider not deepcopying this but it doesnt really matter
        return v.value
    return determine_non_name_value(name_or_value)


def print_expression_debug(
    debug: int,
    expr: Union[list[Token], ExpressionTreeNode],
    value: GulfOfMexicoValue,
    namespaces: list[Namespace],
) -> None:
    expr = get_built_expression(expr)
    msg = None
    match debug:
        case 0:
            pass
        case 1:
            msg = f"Expression evaluates to value {db_to_string(value).value}."
        case 2:
            names = gather_names_or_values(expr)
            msg = f"Expression evaluates to value {db_to_string(value).value}.\nThe value of each name in the expression is the following: \n{chr(10).join([f'  {name}: {db_to_string(get_value_from_namespaces(name, namespaces)).value}' for name in names])}"
        case _:
            names = gather_names_or_values(expr)
            msg = f"Expression evaluates to value {db_to_string(value).value}.\nThe value of each name in the expression is the following: \n{chr(10).join([f'  {name}: {db_to_string(get_value_from_namespaces(name, namespaces)).value}' for name in names])}\nThe expression used to get this value is: \n{expr.to_string()}"

    if not msg:
        return
    if t := get_expr_first_token(expr):
        debug_print(filename, code, msg, t)
    else:
        debug_print_no_token(filename, msg)


def interpret_formatted_string(
    string_token: Token,
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
) -> GulfOfMexicoString:
    """Interpret a formatted string with ${} expressions."""
    string_value = string_token.value
    result = ""
    i = 0
    while i < len(string_value):
        if string_value[i : i + 2] == "${":
            # Find the closing }
            j = i + 2
            brace_count = 1
            while j < len(string_value) and brace_count > 0:
                if string_value[j] == "{":
                    brace_count += 1
                elif string_value[j] == "}":
                    brace_count -= 1
                j += 1
            if brace_count > 0:
                raise_error_at_token(
                    filename,
                    code,
                    "Unclosed ${} expression in string",
                    string_token,
                )
            # Extract the expression
            expr_str = string_value[i + 2 : j - 1]
            # Tokenize the expression
            tokens = db_tokenize(filename, expr_str)
            # Build expression tree
            expr_tree = build_expression_tree(filename, tokens, code)
            # Evaluate the expression
            value = evaluate_expression(
                expr_tree, namespaces, async_statements, when_statement_watchers
            )
            # Convert to string
            result += db_to_string(value).value
            i = j
        else:
            result += string_value[i]
            i += 1
    return GulfOfMexicoString(result)


def evaluate_expression(
    expr: Union[list[Token], ExpressionTreeNode],
    namespaces: list[dict[str, Union[Variable, Name]]],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    *,
    ignore_string_escape_sequences: bool = False,
) -> GulfOfMexicoValue:
    """Wrapper for the evaluate_expression_for_real function that checks deleted values on each run."""
    retval = evaluate_expression_for_real(
        expr,
        namespaces,
        async_statements,
        when_statement_watchers,
        ignore_string_escape_sequences,
    )
    if (
        isinstance(retval, (GulfOfMexicoNumber, GulfOfMexicoString))
        and retval in deleted_values
    ):
        raise_error_at_line(
            filename, code, current_line, f"The value {retval.value} has been deleted."
        )
    return retval


def evaluate_escape_sequences(string_value: GulfOfMexicoString) -> GulfOfMexicoString:
    """Process escape sequences in a GulfOfMexicoString."""
    # Simple escape sequence processing
    escaped = string_value.value
    escaped = escaped.replace("\\n", "\n")
    escaped = escaped.replace("\\t", "\t")
    escaped = escaped.replace("\\r", "\r")
    escaped = escaped.replace('\\"', '"')
    escaped = escaped.replace("\\'", "'")
    escaped = escaped.replace("\\\\", "\\")
    return GulfOfMexicoString(escaped)


def evaluate_expression_for_real(
    expr: Union[list[Token], ExpressionTreeNode],
    namespaces: list[dict[str, Union[Variable, Name]]],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    ignore_string_escape_sequences: bool,
) -> GulfOfMexicoValue:

    expr = get_built_expression(expr)
    match expr:
        case FunctionNode():  # done :)

            # for a function, the thing must be in the namespace
            func = get_name_from_namespaces(expr.name.value, namespaces)

            # make sure it exists and it is actually a function in the namespace
            if func is None:
                raise_error_at_token(
                    filename, code, "Cannot find token in namespace.", expr.name
                )

            # check the thing in the await symbol. if awaiting a single function that is async, evaluate it as not async
            force_execute_sync = False
            if isinstance(func.value, GulfOfMexicoKeyword):
                if func.value.value == "await":
                    if len(expr.args) != 1:
                        raise_error_at_token(
                            filename,
                            code,
                            "Expected only one argument for await function.",
                            expr.name,
                        )
                    if not isinstance(expr.args[0], FunctionNode):
                        raise_error_at_token(
                            filename,
                            code,
                            "Expected argument of await function to be a function call.",
                            expr.name,
                        )
                    force_execute_sync = True

                    # check for None again
                    expr = expr.args[0]
                    func = get_name_from_namespaces(expr.name.value, namespaces)
                    if func is None:  # the other check happens in the next statement
                        raise_error_at_token(
                            filename,
                            code,
                            "Cannot find token in namespaces.",
                            expr.name,
                        )

                elif func.value.value == "previous":
                    if len(expr.args) != 1:
                        raise_error_at_token(
                            filename,
                            code,
                            "Expected only one argument for previous function.",
                            expr.name,
                        )
                    if not isinstance(expr.args[0], ValueNode):
                        raise_error_at_token(
                            filename,
                            code,
                            "Expected argument of previous function to be a variable.",
                            expr.name,
                        )
                    force_execute_sync = True

                    # check for None again
                    val = get_name_from_namespaces(
                        expr.args[0].name_or_value.value, namespaces
                    )
                    if not isinstance(val, Variable):
                        raise_error_at_token(
                            filename,
                            code,
                            "Expected argument of previous function to be a defined variable.",
                            expr.args[0].name_or_value,
                        )
                    return val.prev_values[-1]

                elif func.value.value == "next":
                    if len(expr.args) != 1:
                        raise_error_at_token(
                            filename,
                            code,
                            "Expected only one argument for next function.",
                            expr.name,
                        )
                    if not isinstance(expr.args[0], ValueNode):
                        raise_error_at_token(
                            filename,
                            code,
                            "Expected argument of next function to be a variable.",
                            expr.name,
                        )
                    force_execute_sync = True

                    # check for None again
                    val = get_name_from_namespaces(
                        expr.args[0].name_or_value.value, namespaces
                    )
                    if not isinstance(val, Variable):
                        raise_error_at_token(
                            filename,
                            code,
                            "Expected argument of next function to be a defined variable.",
                            expr.args[0].name_or_value,
                        )
                    # For next, we need to return a promise that will resolve to the future value
                    # Create a promise and register a watcher for the variable
                    promise = GulfOfMexicoPromise(None)

                    # Get the namespace ID for the watcher key
                    _, ns = get_name_and_namespace_from_namespaces(
                        expr.args[0].name_or_value.value, namespaces
                    )
                    if not ns:
                        raise_error_at_token(
                            filename,
                            code,
                            "Could not find namespace for variable.",
                            expr.args[0].name_or_value,
                        )
                    ns_id = id(ns)
                    var_name = expr.args[0].name_or_value.value

                    # Create a dummy return statement that will resolve the promise
                    # This is a bit of a hack, but it works with the existing watcher system
                    dummy_return = ReturnStatement(
                        keyword=None,
                        expression=[
                            expr.args[0].name_or_value
                        ],  # Just return the variable value
                        debug=0,
                    )

                    # Register the watcher
                    watchers_key = (var_name, ns_id)
                    name_watchers[watchers_key] = (
                        dummy_return,
                        {watchers_key},  # Only watching this one variable
                        namespaces + [{}],  # Empty namespace for the watcher
                        promise,
                    )

                    return promise

            if not isinstance(func.value, (BuiltinFunction, GulfOfMexicoFunction)):
                raise_error_at_token(
                    filename,
                    code,
                    "Attempted function call on non-function value.",
                    expr.name,
                )

            caller = None
            dotted_call = len(name_split := expr.name.value.split(".")) > 1
            if dotted_call:
                caller = ".".join(name_split[:-1])
                # Only inject caller as first arg for builtin methods that modify the caller
                if (
                    isinstance(func.value, BuiltinFunction)
                    and func.value.modifies_caller
                ):
                    expr = deepcopy(expr)  # avoid mutating original
                    expr.args.insert(
                        0,
                        ValueNode(
                            Token(TokenType.NAME, caller, expr.name.line, expr.name.col)
                        ),
                    )
            args = [
                evaluate_expression(
                    arg, namespaces, async_statements, when_statement_watchers
                )
                for arg in expr.args
            ]
            if isinstance(args[0], GulfOfMexicoSpecialBlankValue):
                args = args[1:]
            # Extend namespaces with caller's namespace for method-style calls
            extended_namespaces = namespaces
            if caller is not None:
                caller_entry = get_name_from_namespaces(caller, namespaces)
                if isinstance(caller_entry, (Variable, Name)):
                    caller_val = caller_entry.value
                    if isinstance(caller_val, GulfOfMexicoNamespaceable):
                        extended_namespaces = namespaces + [caller_val.namespace]
            if (
                isinstance(func.value, GulfOfMexicoFunction)
                and func.value.is_async
                and not force_execute_sync
            ):
                register_async_function(
                    expr, func.value, extended_namespaces, args, async_statements
                )
                return GulfOfMexicoUndefined()
            elif (
                isinstance(func.value, BuiltinFunction) and func.value.modifies_caller
            ):  # special cases where the function itself modifies the caller
                if (
                    caller
                ):  # seems like a needless check but it makes the errors go away
                    caller_var = get_name_from_namespaces(caller, namespaces)
                    if (
                        isinstance(caller_var, Variable)
                        and not caller_var.can_edit_value
                    ):
                        raise_error_at_line(
                            filename,
                            code,
                            current_line,
                            "Cannot edit the value of this variable.",
                        )

                retval = evaluate_normal_function(
                    expr, func.value, extended_namespaces, args, when_statement_watchers
                )
                when_watchers = get_code_from_when_statement_watchers(
                    id(args[0]), when_statement_watchers
                )
                for when_watcher in when_watchers:  # i just wanna be done with this :(
                    if len(when_watcher) == 3:
                        condition, inside_statements, captured_namespaces = when_watcher
                    else:
                        condition, inside_statements = when_watcher
                        captured_namespaces = namespaces
                    condition_val = evaluate_expression(
                        condition,
                        captured_namespaces,
                        async_statements,
                        when_statement_watchers,
                    )
                    execute_conditional(
                        condition_val,
                        inside_statements,
                        captured_namespaces,
                        when_statement_watchers,
                        {},
                        [],
                    )
                return retval

            return evaluate_normal_function(
                expr, func.value, extended_namespaces, args, when_statement_watchers
            )

        case ListNode():  # done :)
            return GulfOfMexicoList(
                [
                    evaluate_expression(
                        x, namespaces, async_statements, when_statement_watchers
                    )
                    for x in expr.values
                ]
            )

        case ValueNode():  # done :)
            if expr.name_or_value.type == TokenType.STRING:
                retval = interpret_formatted_string(
                    expr.name_or_value,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                )
                if not ignore_string_escape_sequences:
                    return evaluate_escape_sequences(retval)
                return retval
            return get_value_from_namespaces(expr.name_or_value, namespaces)

        case IndexNode():  # done :)
            value = evaluate_expression(
                expr.value, namespaces, async_statements, when_statement_watchers
            )
            index = evaluate_expression(
                expr.index, namespaces, async_statements, when_statement_watchers
            )
            if not isinstance(value, GulfOfMexicoIndexable):
                raise_error_at_line(
                    filename,
                    code,
                    current_line,
                    "Attempting to index a value that is not indexable.",
                )
            return value.access_index(index)

        case ExpressionNode():  # done :)
            left = evaluate_expression(
                expr.left, namespaces, async_statements, when_statement_watchers
            )
            if (
                db_to_boolean(left).value == True and expr.operator == OperatorType.OR
            ):  # handle short curcuiting for True or __
                return left
            elif (
                db_to_boolean(left).value == False and expr.operator == OperatorType.AND
            ):  # handle short curcuiting for False and __
                return left
            right = evaluate_expression(
                expr.right, namespaces, async_statements, when_statement_watchers
            )
            return perform_two_value_operation(
                left, right, expr.operator, expr.operator_token
            )

        case SingleOperatorNode():
            val = evaluate_expression(
                expr.expression, namespaces, async_statements, when_statement_watchers
            )
            return perform_single_value_operation(val, expr.operator)

    return GulfOfMexicoUndefined()


def handle_next_expressions(
    expr: ExpressionTreeNode, namespaces: list[Namespace]
) -> tuple[ExpressionTreeNode, set[tuple[str, int]], set[str]]:
    """
    This function looks for the "next" keyword in an expression, and detects separate await modifiers for that keyword.
    Then, it removes the "next" and "await next" nodes from the ExpressionTree, and returns the head of the tree.
    Additionally, every name that appears in the function as a next or async next, its value is saved in a temporary namespace.
    With the returned set of names that are used in "next" and "await next", we can insert these into a dictionary
        that contains information about which names are being "watched" for changes. When this dictionary changes,
        we can execute code accordingly.

    This is my least favorite function in the program.
    """

    normal_nexts: set[tuple[str, int]] = set()
    async_nexts: set[str] = set()
    inner_nexts: list[tuple[set[tuple[str, int]], set[str]]] = []
    match expr:
        case FunctionNode():

            func = get_name_from_namespaces(expr.name.value, namespaces)
            if func is None:
                raise_error_at_token(
                    filename,
                    code,
                    "Attempted function call on undefined variable.",
                    expr.name,
                )

            # check if it is a next or await
            is_next = is_await = (
                False  # i don't need this but it makes my LSP stop crying so it's here
            )
            if isinstance(func.value, GulfOfMexicoKeyword) and (
                (is_next := func.value.value == "next")
                or (is_await := func.value.value == "await")
            ):

                if is_next:

                    # add it to list of things to watch for and change the returned expression to the name being next-ed
                    if len(expr.args) != 1 or not isinstance(expr.args[0], ValueNode):
                        raise_error_at_token(
                            filename,
                            code,
                            '"Next"keyword can only take a single value as an argument.',
                            expr.name,
                        )
                    name = expr.args[0].name_or_value.value
                    _, ns = get_name_and_namespace_from_namespaces(name, namespaces)
                    if not ns:
                        raise_error_at_line(
                            filename,
                            code,
                            current_line,
                            "Attempted to access namespace of a value without a namespace.",
                        )
                    last_name = name.split(".")[-1]
                    normal_nexts.add((name, id(ns)))
                    expr = expr.args[0]
                    expr.name_or_value.value = get_modified_next_name(last_name, id(ns))

                elif is_await:

                    if len(expr.args) != 1 or not isinstance(
                        expr.args[0], FunctionNode
                    ):
                        raise_error_at_token(
                            filename, code, "Can only await a function.", expr.name
                        )
                    inner_expr = expr.args[0]

                    func = get_name_from_namespaces(expr.args[0].name.value, namespaces)
                    if func is None:
                        raise_error_at_token(
                            filename,
                            code,
                            "Attempted function call on undefined variable.",
                            expr.name,
                        )

                    if (
                        isinstance(func.value, GulfOfMexicoKeyword)
                        and func.value.value == "next"
                    ):
                        if len(inner_expr.args) != 1 or not isinstance(
                            inner_expr.args[0], ValueNode
                        ):
                            raise_error_at_token(
                                filename,
                                code,
                                '"Next"keyword can only take a single value as an argument.',
                                inner_expr.name,
                            )
                        name = inner_expr.args[0].name_or_value.value
                        _, ns = get_name_and_namespace_from_namespaces(name, namespaces)
                        if not ns:
                            raise_error_at_line(
                                filename,
                                code,
                                current_line,
                                "Attempted to access namespace of a value without a namespace.",
                            )
                        last_name = name.split(".")[-1]
                        async_nexts.add(
                            name
                        )  # only need to store the name for the async ones because we are going to wait anyways
                        expr = inner_expr.args[0]
                        expr.name_or_value.value = get_modified_next_name(
                            last_name, id(ns)
                        )

            else:
                replacement_args = []
                for arg in expr.args:
                    new_expr, normal_arg_nexts, async_arg_nexts = (
                        handle_next_expressions(arg, namespaces)
                    )
                    inner_nexts.append((normal_arg_nexts, async_arg_nexts))
                    replacement_args.append(new_expr)
                expr.args = replacement_args

        case ListNode():
            replacement_values = []
            for ex in expr.values:
                new_expr, normal_expr_nexts, async_expr_nexts = handle_next_expressions(
                    ex, namespaces
                )
                inner_nexts.append((normal_expr_nexts, async_expr_nexts))
                replacement_values.append(new_expr)
            expr.values = replacement_values
        case IndexNode():
            new_value, normal_value_nexts, async_value_nexts = handle_next_expressions(
                expr.value, namespaces
            )
            new_index, normal_index_nexts, async_index_nexts = handle_next_expressions(
                expr.index, namespaces
            )
            expr.value = new_value
            expr.index = new_index
            inner_nexts.extend(
                [
                    (normal_value_nexts, async_value_nexts),
                    (normal_index_nexts, async_index_nexts),
                ]
            )
        case ExpressionNode():
            new_left, normal_left_nexts, async_left_nexts = handle_next_expressions(
                expr.left, namespaces
            )
            new_right, normal_right_nexts, async_right_nexts = handle_next_expressions(
                expr.right, namespaces
            )
            expr.left = new_left
            expr.right = new_right
            inner_nexts.extend(
                [
                    (normal_left_nexts, async_left_nexts),
                    (normal_right_nexts, async_right_nexts),
                ]
            )
        case SingleOperatorNode():
            new_expr, normal_expr_nexts, async_expr_nexts = handle_next_expressions(
                expr.expression, namespaces
            )
            expr.expression = new_expr
            inner_nexts.append((normal_expr_nexts, async_expr_nexts))
    for nn, an in inner_nexts:
        normal_nexts |= nn
        async_nexts |= an
    return expr, normal_nexts, async_nexts


def save_previous_values_next_expr(
    expr_to_modify: ExpressionTreeNode, nexts: set[str], namespaces: list[Namespace]
) -> Namespace:

    saved_namespace: Namespace = {}
    match expr_to_modify:
        case ValueNode():
            if expr_to_modify.name_or_value.type == TokenType.STRING:
                return {}
            name = expr_to_modify.name_or_value.value
            if name not in nexts:
                return {}
            val = get_name_from_namespaces(name, namespaces)
            if not val:
                val = Name("", determine_non_name_value(expr_to_modify.name_or_value))
            mod_name = get_modified_prev_name(name)
            expr_to_modify.name_or_value.value = mod_name
            return {mod_name: Name(mod_name, val.value)}
        case ExpressionNode():
            left_ns = save_previous_values_next_expr(
                expr_to_modify.left, nexts, namespaces
            )
            right_ns = save_previous_values_next_expr(
                expr_to_modify.right, nexts, namespaces
            )
            return left_ns | right_ns
        case IndexNode():
            value_ns = save_previous_values_next_expr(
                expr_to_modify.value, nexts, namespaces
            )
            index_ns = save_previous_values_next_expr(
                expr_to_modify.index, nexts, namespaces
            )
            return value_ns | index_ns
        case ListNode():
            for ex in expr_to_modify.values:
                saved_namespace |= save_previous_values_next_expr(ex, nexts, namespaces)
            return saved_namespace
        case FunctionNode():
            for arg in expr_to_modify.args:
                saved_namespace |= save_previous_values_next_expr(
                    arg, nexts, namespaces
                )
            return saved_namespace
        case SingleOperatorNode():
            return save_previous_values_next_expr(
                expr_to_modify.expression, nexts, namespaces
            )
    return saved_namespace


def determine_statement_type(
    possible_statements: tuple[CodeStatement, ...], namespaces: list[Namespace]
) -> Optional[CodeStatement]:
    instance_to_keywords: dict[type[CodeStatementKeywordable], set[str]] = {
        Conditional: {"if"},
        WhenStatement: {"when"},
        AfterStatement: {"after"},
        ClassDeclaration: {"class", "className"},
        DeleteStatement: {"delete"},
        ReverseStatement: {"reverse"},
        ImportStatement: {"import"},
        TryWhateverStatement: {"try"},
        ProcrastinationStatement: {"later", "eventually", "whenever"},
        CorporateSpeakStatement: {
            "synergize",
            "leverage",
            "paradigm_shift",
            "circle_back",
            "touch_base",
        },
        EmotionalStatement: {"happy", "sad", "angry", "excited", "tired"},
        SuperstitiousStatement: {"lucky", "unlucky", "cross_fingers", "knock_on_wood"},
        QuantumStatement: {"quantum"},
        GaslightingStatement: {"definitely_not"},
        BlockchainStatement: {
            "blockchain",
            "immutable_ledger",
            "smart_contract",
            "mine",
        },
        AIBuzzwordStatement: {"deep_learning", "neural_network", "ai_powered"},
        AgileStatement: {"sprint", "standup", "retro", "burndown"},
        SecurityTheaterStatement: {
            "encrypt",
            "two_factor",
            "penetration_test",
            "zero_trust",
        },
        DevOpsStatement: {"containerize", "orchestrate", "microservice", "kubernetes"},
        StartupStatement: {"pivot", "disrupt", "unicorn", "hockey_stick"},
    }

    for st in possible_statements:
        if isinstance(st, CodeStatementKeywordable):
            val = get_name_from_namespaces(st.keyword.value, namespaces)
            if (
                val is not None
                and isinstance(val.value, GulfOfMexicoKeyword)
                and val.value.value in instance_to_keywords[type(st)]
            ):
                return st
        elif isinstance(st, ReturnStatement):
            # Prefer explicit return statements. First, handle short-form (no keyword token).
            if st.keyword is None:
                return st
            # Primary path: resolve via namespaces to allow keyword aliasing.
            val = get_name_from_namespaces(st.keyword.value, namespaces)
            if (
                val
                and isinstance(val.value, GulfOfMexicoKeyword)
                and val.value.value == "return"
            ):
                return st
            # Fallback: if the literal token text is 'return', still treat as return.
            # This avoids mis-disambiguation when the keyword namespace isn't visible in scope.
            if st.keyword.value == "return":
                return st
        elif isinstance(
            st, FunctionDefinition
        ):  # allow for async and normal function definitions
            if len(st.keywords) == 1:
                val = get_name_from_namespaces(st.keywords[0].value, namespaces)
                if (
                    val
                    and isinstance(val.value, GulfOfMexicoKeyword)
                    and re.match(r"^f?u?n?c?t?i?o?n?$", val.value.value)
                ):
                    return st
            elif len(st.keywords) == 2:
                val = get_name_from_namespaces(st.keywords[0].value, namespaces)
                other_val = get_name_from_namespaces(st.keywords[1].value, namespaces)
                if (
                    val
                    and other_val
                    and isinstance(val.value, GulfOfMexicoKeyword)
                    and isinstance(other_val.value, GulfOfMexicoKeyword)
                    and re.match(r"^f?u?n?c?t?i?o?n?$", other_val.value.value)
                    and val.value.value == "async"
                ):
                    return st
        elif isinstance(
            st, VariableDeclaration
        ):  # allow for const const const and normal declarations
            if len(st.modifiers) == 1:
                if (
                    (val := get_name_from_namespaces(st.modifiers[0].value, namespaces))
                    is not None
                    and isinstance(val.value, GulfOfMexicoKeyword)
                    and val.value.value in {"const", "var"}
                ):
                    return st
            elif len(st.modifiers) == 2:
                if all(
                    [
                        (val := get_name_from_namespaces(mod.value, namespaces))
                        is not None
                        and isinstance(val.value, GulfOfMexicoKeyword)
                        and val.value.value in {"const", "var"}
                        for mod in st.modifiers
                    ]
                ):
                    return st
            elif len(st.modifiers) == 3:
                if all(
                    [
                        (val := get_name_from_namespaces(mod.value, namespaces))
                        is not None
                        and isinstance(val.value, GulfOfMexicoKeyword)
                        and val.value.value == "const"
                        for mod in st.modifiers
                    ]
                ):
                    return st
        elif isinstance(st, ExportStatement):
            if (
                isinstance(
                    v := get_value_from_namespaces(st.to_keyword, namespaces),
                    GulfOfMexicoKeyword,
                )
                and v.value == "to"
                and isinstance(
                    v := get_value_from_namespaces(st.export_keyword, namespaces),
                    GulfOfMexicoKeyword,
                )
                and v.value == "export"
            ):
                return st

    # now is left: expression evalulation and variable assignment
    for st in possible_statements:
        if isinstance(st, VariableAssignment):
            return st
    for st in possible_statements:
        if isinstance(st, ExpressionStatement):
            return st
    return None


def adjust_for_normal_nexts(
    statement: CodeStatementWithExpression,
    async_nexts: set[str],
    normal_nexts: set[tuple[str, int]],
    promise: Optional[GulfOfMexicoPromise],
    namespaces: list[Namespace],
    prev_namespace: Namespace,
):

    old_async_vals, old_normal_vals = [], []
    get_state_watcher = lambda val: (
        None if not val else len(v) if (v := getattr(val, "prev_values")) else 0
    )
    for name in async_nexts:
        old_async_vals.append(
            get_state_watcher(get_name_from_namespaces(name, namespaces))
        )
    for name, _ in normal_nexts:
        old_normal_vals.append(
            get_state_watcher(get_name_from_namespaces(name, namespaces))
        )

    # for each async one, wait until each one is different
    for name, start_len in zip(async_nexts, old_async_vals):
        curr_len = get_state_watcher(get_name_from_namespaces(name, namespaces))
        while start_len == curr_len:
            exit_on_dead_listener()
            curr_len = get_state_watcher(get_name_from_namespaces(name, namespaces))

    # now, build a namespace for each one
    new_namespace: Namespace = {}
    for name, old_len in zip(async_nexts, old_async_vals):
        v, ns = get_name_and_namespace_from_namespaces(name, namespaces)
        if not v or not ns or (old_len is not None and not isinstance(v, Variable)):
            raise_error_at_line(
                filename,
                code,
                current_line,
                "Something went wrong with accessing the next value of a variable.",
            )
        mod_name = get_modified_next_name(name, id(ns))
        match old_len:
            case None:
                new_namespace[mod_name] = Name(
                    mod_name, v.value if isinstance(v, Name) else v.prev_values[0]
                )
            case i:
                if not isinstance(v, Variable):
                    raise_error_at_line(
                        filename, code, current_line, "Something went wrong."
                    )
                new_namespace[mod_name] = Name(mod_name, v.prev_values[i])

    # now, adjust for any values that may have already been modified by next statements
    for (name, ns_id), old_len in zip(normal_nexts, old_normal_vals):
        new_len = get_state_watcher(v := get_name_from_namespaces(name, namespaces))
        if v is None or new_len == old_len:
            continue
        mod_name = get_modified_next_name(name, ns_id)
        normal_nexts.remove((name, ns_id))
        match old_len:
            case None:
                new_namespace[mod_name] = Name(
                    mod_name, v.value if isinstance(v, Name) else v.prev_values[0]
                )
            case i:
                if not isinstance(v, Variable):
                    raise_error_at_line(
                        filename, code, current_line, "Something went wrong."
                    )
                new_namespace[mod_name] = Name(mod_name, v.prev_values[i])

    # the remaining values are still waiting on a result, add these to the list of name watchers
    # this new_namespace i am adding is purely for use in evaluation of expressions, and the code within
    # a code statement should not use that namespace. therefore, some logic must be done to remove that namespace
    # when the expression of a code statement is executed
    for name, ns_id in normal_nexts:
        name_watchers[(name.split(".")[-1], ns_id)] = (
            statement,
            normal_nexts,
            namespaces + [new_namespace | prev_namespace],
            promise,
        )


def wait_for_async_nexts(
    async_nexts: set[str], namespaces: list[Namespace]
) -> Namespace:

    old_async_vals = []
    get_state_watcher = lambda val: (
        None if not val else len(v) if (v := getattr(val, "prev_values")) else 0
    )
    for name in async_nexts:
        old_async_vals.append(
            get_state_watcher(get_name_from_namespaces(name, namespaces))
        )

    # for each async one, wait until each one is different
    for name, start_len in zip(async_nexts, old_async_vals):
        curr_len = get_state_watcher(get_name_from_namespaces(name, namespaces))
        while start_len == curr_len:
            exit_on_dead_listener()
            curr_len = get_state_watcher(get_name_from_namespaces(name, namespaces))

    # now, build a namespace for each one
    new_namespace: Namespace = {}
    for name, old_len in zip(async_nexts, old_async_vals):
        v, ns = get_name_and_namespace_from_namespaces(name, namespaces)
        if not v or not ns or (old_len is not None and not isinstance(v, Variable)):
            raise_error_at_line(
                filename,
                code,
                current_line,
                "Something went wrong with accessing the next value of a variable.",
            )
        mod_name = get_modified_next_name(name, id(ns))
        new_namespace[mod_name] = Name(mod_name, v.value)
    return new_namespace


def interpret_name_watching_statement(
    statement: CodeStatementWithExpression,
    namespaces: list[Namespace],
    promise: Optional[GulfOfMexicoPromise],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
):

    # evaluate the expression using the names off the top
    expr_val = evaluate_expression(
        statement.expression, namespaces, async_statements, when_statement_watchers
    )
    index_vals = (
        [
            evaluate_expression(
                expr, namespaces, async_statements, when_statement_watchers
            )
            for expr in statement.indexes
        ]
        if isinstance(statement, VariableAssignment)
        else []
    )
    namespaces.pop()  # remove expired namespace  -- THIS IS INCREDIBLY IMPORTANT

    match statement:
        case ReturnStatement():
            if promise is None:
                raise_error_at_line(
                    filename, code, current_line, "Something went wrong."
                )
            promise.value = expr_val  # simply change the promise to that value as the return statement already returned a promise
        case VariableDeclaration():
            declare_new_variable(
                statement,
                expr_val,
                namespaces,
                async_statements,
                when_statement_watchers,
            )
        case VariableAssignment():
            assign_variable(
                statement,
                index_vals,
                expr_val,
                namespaces,
                async_statements,
                when_statement_watchers,
            )
        case Conditional():
            execute_conditional(
                expr_val, statement.code, namespaces, when_statement_watchers, {}, []
            )
        case AfterStatement():
            execute_after_statement(
                expr_val, statement.code, namespaces, when_statement_watchers
            )
        case ExpressionStatement():
            print_expression_debug(
                statement.debug,
                statement.expression,
                expr_val,
                namespaces,
            )


def clear_temp_namespace(
    namespaces: list[Namespace], temp_namespace: Namespace
) -> None:
    for key in temp_namespace:
        del namespaces[-1][key]


# simply execute the conditional inside a new scope
def execute_conditional(
    condition: GulfOfMexicoValue,
    statements_inside_scope: list[tuple[CodeStatement, ...]],
    namespaces: list[Namespace],
    when_statement_watchers: WhenStatementWatchers,
    importable_names: dict[str, dict[str, GulfOfMexicoValue]],
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
) -> Optional[GulfOfMexicoValue]:
    condition = db_to_boolean(condition)
    execute = (
        condition.value == True
        if condition.value is not None
        else random.random() < 0.50
    )
    if execute:
        return interpret_code_statements(
            statements_inside_scope,
            namespaces + [{}],
            [],
            when_statement_watchers + [{}],
            importable_names,
            exported_names,
        )  # empty scope and async statements, just for this :)


# this is the equaivalent of an event listener
def get_mouse_event_object(
    x: int, y: int, button: mouse.Button, event: str
) -> GulfOfMexicoObject:
    return GulfOfMexicoObject(
        "MouseEvent",
        {
            "x": Name("x", GulfOfMexicoNumber(x)),
            "y": Name("y", GulfOfMexicoNumber(y)),
            "button": Name("button", GulfOfMexicoString(str(button).split(".")[-1])),
            "event": Name("event", GulfOfMexicoString(event)),
        },
    )


def get_keyboard_event_object(
    key: Optional[Union[keyboard.Key, keyboard.KeyCode]], event: str
) -> GulfOfMexicoObject:
    return GulfOfMexicoObject(
        "KeyboardEvent",
        {
            "key": Name("key", GulfOfMexicoString(str(key).split(".")[-1])),
            "event": Name("event", GulfOfMexicoString(event)),
        },
    )


def execute_after_statement(
    event: GulfOfMexicoValue,
    statements_inside_scope: list[tuple[CodeStatement, ...]],
    namespaces: list[Namespace],
    when_statement_watchers: WhenStatementWatchers,
    importable_names: dict[str, dict[str, GulfOfMexicoValue]],
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
) -> None:

    if not KEY_MOUSE_IMPORTED:
        raise_error_at_line(
            filename,
            code,
            current_line,
            "Attempted to use mouse and keyboard functionality without importing the [input] extra dependency.",
        )

    if not isinstance(event, GulfOfMexicoString):
        raise_error_at_line(
            filename,
            code,
            current_line,
            f'Invalid event for the "after" statement: "{db_to_string(event)}"',
        )

    match event.value:
        case "mouseclick":
            mouse_buttons = {}

            def listener_func(x: int, y: int, button: mouse.Button, pressed: bool):
                nonlocal namespaces, statements_inside_scope
                if pressed:
                    mouse_buttons[button] = (x, y)
                else:
                    if mouse_buttons[
                        button
                    ]:  # it has been released and then pressed again
                        interpret_code_statements(
                            statements_inside_scope,
                            namespaces
                            + [
                                {
                                    "event": Name(
                                        "event",
                                        get_mouse_event_object(
                                            x, y, button, event.value
                                        ),
                                    )
                                }
                            ],
                            [],
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                    del mouse_buttons[button]

            listener = mouse.Listener(on_click=listener_func)  # type: ignore

        case "mousedown":

            def listener_func(x: int, y: int, button: mouse.Button, pressed: bool):
                nonlocal namespaces, statements_inside_scope
                if pressed:
                    interpret_code_statements(
                        statements_inside_scope,
                        namespaces
                        + [
                            {
                                "event": Name(
                                    "event",
                                    get_mouse_event_object(x, y, button, event.value),
                                )
                            }
                        ],
                        [],
                        when_statement_watchers + [{}],
                        importable_names,
                        exported_names,
                    )

            listener = mouse.Listener(on_click=listener_func)  # type: ignore

        case "mouseup":

            def listener_func(x: int, y: int, button: mouse.Button, pressed: bool):
                nonlocal namespaces, statements_inside_scope
                if not pressed:
                    interpret_code_statements(
                        statements_inside_scope,
                        namespaces
                        + [
                            {
                                "event": Name(
                                    "event",
                                    get_mouse_event_object(x, y, button, event.value),
                                )
                            }
                        ],
                        [],
                        when_statement_watchers + [{}],
                        importable_names,
                        exported_names,
                    )

            listener = mouse.Listener(on_click=listener_func)  # type: ignore

        case "keyclick":
            keys = set()

            def on_press(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]):
                nonlocal namespaces, statements_inside_scope
                keys.add(key)

            def on_release(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]):
                nonlocal namespaces, statements_inside_scope
                if key in keys:
                    event_object = get_keyboard_event_object(key.char if isinstance(key, keyboard.KeyCode) else key, event.value)  # type: ignore
                    interpret_code_statements(statements_inside_scope, namespaces + [{"event": Name("event", event_object)}], [], when_statement_watchers + [{}], importable_names, exported_names)  # type: ignore
                keys.discard(key)

            listener = keyboard.Listener(on_press=on_press, on_release=on_release)  # type: ignore

        case "keydown":

            def on_press(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]):
                nonlocal namespaces, statements_inside_scope
                event_object = get_keyboard_event_object(key.char if isinstance(key, keyboard.KeyCode) else key, event.value)  # type: ignore
                interpret_code_statements(
                    statements_inside_scope,
                    namespaces + [{"event": Name("event", event_object)}],
                    [],
                    when_statement_watchers + [{}],
                    importable_names,
                    exported_names,
                )

            listener = keyboard.Listener(on_press=on_press)  # type: ignore

        case "keyup":

            def on_release(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]):
                nonlocal namespaces, statements_inside_scope
                event_object = get_keyboard_event_object(key.char if isinstance(key, keyboard.KeyCode) else key, event.value)  # type: ignore
                interpret_code_statements(
                    statements_inside_scope,
                    namespaces + [{"event": Name("event", event_object)}],
                    [],
                    when_statement_watchers + [{}],
                    importable_names,
                    exported_names,
                )

            listener = keyboard.Listener(on_release=on_release)  # type: ignore

        case _:
            raise_error_at_line(
                filename,
                code,
                current_line,
                f'Invalid event for the "after" statement: "{db_to_string(event)}"',
            )

    listener.start()
    after_listeners.append(listener)  # pyright: ignore[reportUnknownMemberType]


def gather_names_or_values(expr: ExpressionTreeNode) -> set[Token]:
    names: set[Token] = set()
    match expr:
        case FunctionNode():
            for arg in expr.args:
                names |= gather_names_or_values(arg)
        case ListNode():
            for val in expr.values:
                names |= gather_names_or_values(val)
        case ExpressionNode():
            names |= gather_names_or_values(expr.right) | gather_names_or_values(
                expr.left
            )
        case IndexNode():
            names |= gather_names_or_values(expr.index) | gather_names_or_values(
                expr.value
            )
        case SingleOperatorNode():
            names |= gather_names_or_values(expr.expression)
        case ValueNode():
            names.add(expr.name_or_value)
    return names


def register_when_statement(
    condition: Union[list[Token], ExpressionTreeNode],
    statements_inside_scope: list[tuple[CodeStatement, ...]],
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    importable_names: dict[str, dict[str, GulfOfMexicoValue]],
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
):

    # if it is a variable, store it as the address to that variable.
    # if the internal value is a list, store it as an address to that mutable type.
    built_condition = get_built_expression(condition)
    gathered_names = gather_names_or_values(built_condition)
    caller_names = [
        n for name in gathered_names if (n := ".".join(name.value.split(".")[:-1]))
    ]
    dict_keys = (
        [
            (
                id(v)
                if isinstance(
                    v := get_name_from_namespaces(name.value, namespaces), Variable
                )
                else name.value
            )
            for name in gathered_names
        ]
        + [
            id(v.value)
            for name in gathered_names
            if (v := get_name_from_namespaces(name.value, namespaces)) is not None
            and isinstance(v.value, GulfOfMexicoMutable)
        ]
        + [
            id(v)
            for name in caller_names
            if isinstance(v := get_name_from_namespaces(name, namespaces), Variable)
        ]
        + [
            id(v.value)
            for name in caller_names
            if (v := get_name_from_namespaces(name, namespaces)) is not None
            and isinstance(v.value, GulfOfMexicoMutable)
        ]
    )
    # the last comprehension watches callers of things (like list in list.length), and requires some implementation in the evaluate_expression function
    # so that the caller of a function is also observed for it being called

    # register for future whens
    for name in dict_keys:
        if name not in when_statement_watchers[-1]:
            when_statement_watchers[-1][name] = []
        # store the built condition, the body, and a snapshot of the current
        # namespaces so the watcher runs with the same scope when triggered.
        captured_ns = deepcopy(namespaces)
        # DEBUG: Print what we're capturing
        try:
            debug_keys = [list(ns.keys()) for ns in captured_ns]
            debug_print_no_token(
                filename, f"Capturing namespaces for when: {debug_keys}"
            )
        except Exception:
            pass
        when_statement_watchers[-1][name].append(
            (built_condition, statements_inside_scope, captured_ns)
        )

    # check the condition now
    # Evaluate the condition immediately inside the same namespaces that the
    # when statement was defined. If a name cannot be found, include some
    # cheap debugging info to aid diagnosis of nested scoping issues.
    try:
        condition_value = evaluate_expression(
            built_condition, namespaces, async_statements, when_statement_watchers
        )
    except Exception:
        # Only print a compact debug message so this doesn't pollute
        # normal runs. This will help track down missing names during
        # nested when tests.
        try:
            gathered = [t.value for t in gathered_names]
            available_ns = [list(ns.keys()) for ns in namespaces]
            debug_print_no_token(
                filename,
                f"Failed to evaluate when condition {gathered} "
                f"with namespaces: {available_ns}",
            )
        except Exception:
            pass
        raise
    execute_conditional(
        condition_value,
        statements_inside_scope,
        namespaces,
        when_statement_watchers,
        importable_names,
        exported_names,
    )


def load_globals(
    filename: str,
    code: str,
    arg3,
    arg4,
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
    importable_names: dict[str, GulfOfMexicoValue],
) -> None:
    """Load global variables - this is called before interpretation begins."""
    # Note: Global variable loading is actually handled by load_global_gulfofmexico_variables
    # and load_public_global_variables which are called separately.
    # This function exists for potential future use or custom global loading logic.
    pass


def get_name_from_namespaces(
    name: str, namespaces: list[Namespace]
) -> Optional[Union[Variable, Name]]:
    """Get a name or variable from the namespaces, searching from most local to global.

    Supports dotted access for namespaceable values (object/list/string namespaces).
    """
    # Fast path for simple names
    if "." not in name:
        for namespace in reversed(namespaces):
            if name in namespace:
                return namespace[name]
        return None

    parts = name.split(".")
    # Find the base in any namespace (closest scope wins)
    base_entry: Optional[Union[Variable, Name]] = None
    for namespace in reversed(namespaces):
        if parts[0] in namespace:
            base_entry = namespace[parts[0]]
            break
    if base_entry is None:
        return None

    # Walk through nested namespaces
    current_value: GulfOfMexicoValue = base_entry.value  # type: ignore[attr-defined]
    current_entry: Optional[Union[Variable, Name]] = base_entry
    for seg in parts[1:]:
        if not isinstance(current_value, GulfOfMexicoNamespaceable):
            return None
        if seg not in current_value.namespace:
            return None
        current_entry = current_value.namespace[seg]
        current_value = current_entry.value  # type: ignore[attr-defined]
    return current_entry


def get_name_and_namespace_from_namespaces(
    name: str, namespaces: list[Namespace]
) -> tuple[Optional[Union[Variable, Name]], Optional[Namespace]]:
    """Get a name or variable and its containing namespace from the namespaces."""
    for namespace in reversed(namespaces):
        if name in namespace:
            return namespace[name], namespace
    return None, None


def determine_non_name_value(name_or_value: Token) -> GulfOfMexicoValue:
    """Determine the value of a token that is not a name in the namespace."""
    match name_or_value.type:
        case TokenType.STRING:
            return GulfOfMexicoString(name_or_value.value)
        case TokenType.NAME:
            # Try to parse as number
            try:
                # Check if it's an integer
                if (
                    "." not in name_or_value.value
                    and "e" not in name_or_value.value.lower()
                ):
                    return GulfOfMexicoNumber(int(name_or_value.value))
                else:
                    return GulfOfMexicoNumber(float(name_or_value.value))
            except ValueError:
                # Not a number, check if it's a keyword or undefined
                if name_or_value.value in ["true", "false", "maybe", "undefined"]:
                    # Handle keywords not in KEYWORDS
                    match name_or_value.value:
                        case "true":
                            return GulfOfMexicoBoolean(True)
                        case "false":
                            return GulfOfMexicoBoolean(False)
                        case "maybe":
                            return GulfOfMexicoBoolean(None)
                        case "undefined":
                            return GulfOfMexicoUndefined()
                # If it's not a recognized literal, it's an undefined name
                raise_error_at_token(
                    filename,
                    code,
                    f"Undefined name: {name_or_value.value}",
                    name_or_value,
                )
        case _:
            raise_error_at_token(
                filename,
                code,
                f"Unexpected token type: {name_or_value.type}",
                name_or_value,
            )


# Global variables for current file context
filename: str = ""
code: str = ""

# Global variable for current line
current_line: int = 0

# Set of deleted values
deleted_values: set[GulfOfMexicoValue] = set()

# Global watchers for reactive programming
name_watchers: NameWatchers = {}
after_listeners: list = []

# Global flags
is_lifetime_temporal: bool = False


def exit_on_dead_listener() -> None:
    """Exit if there are no active listeners remaining."""
    if not after_listeners:
        exit()


def interpret_code_statements_main_wrapper(
    statements: list[tuple[CodeStatement, ...]],
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    importable_names: dict[str, dict[str, GulfOfMexicoValue]],
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
) -> Optional[GulfOfMexicoValue]:
    """Main wrapper for interpreting code statements."""
    return interpret_code_statements(
        statements,
        namespaces,
        async_statements,
        when_statement_watchers,
        importable_names,
        exported_names,
    )


def interpret_code_statements(
    statements: list[tuple[CodeStatement, ...]],
    namespaces: list[Namespace],
    async_statements: AsyncStatements,
    when_statement_watchers: WhenStatementWatchers,
    importable_names: dict[str, dict[str, GulfOfMexicoValue]],
    exported_names: list[tuple[str, str, GulfOfMexicoValue]],
) -> Optional[GulfOfMexicoValue]:
    """Interpret a list of code statements."""
    result = None

    # Process each statement
    for statement_tuple in statements:
        # Determine the actual statement type
        statement = determine_statement_type(statement_tuple, namespaces)
        if statement is None:
            continue

        # Update current line for error reporting
        global current_line
        if hasattr(statement, "name") and hasattr(statement.name, "line"):
            current_line = statement.name.line
        elif hasattr(statement, "keyword") and hasattr(statement.keyword, "line"):
            current_line = statement.keyword.line

        # Execute the statement based on its type
        match statement:
            case ExpressionStatement():
                result = evaluate_expression(
                    statement.expression,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                )
                print_expression_debug(
                    statement.debug,
                    statement.expression,
                    result,
                    namespaces,
                )

            case VariableDeclaration():
                value = evaluate_expression(
                    statement.expression,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                )
                declare_new_variable(
                    statement,
                    value,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                )

            case VariableAssignment():
                indexes = [
                    evaluate_expression(
                        expr,
                        namespaces,
                        async_statements,
                        when_statement_watchers,
                    )
                    for expr in statement.indexes
                ]
                new_value = evaluate_expression(
                    statement.expression,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                )
                assign_variable(
                    statement,
                    indexes,
                    new_value,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                )

            case ReturnStatement():
                result = evaluate_expression(
                    statement.expression,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                )
                print_expression_debug(
                    statement.debug,
                    statement.expression,
                    result,
                    namespaces,
                )
                return result  # Return immediately

            case Conditional():
                condition = evaluate_expression(
                    statement.expression,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                )
                result = execute_conditional(
                    condition,
                    statement.code,
                    namespaces,
                    when_statement_watchers,
                    importable_names,
                    exported_names,
                )

            case WhenStatement():
                register_when_statement(
                    statement.expression,
                    statement.code,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                    importable_names,
                    exported_names,
                )

            case AfterStatement():
                event = evaluate_expression(
                    statement.expression,
                    namespaces,
                    async_statements,
                    when_statement_watchers,
                )
                execute_after_statement(
                    event,
                    statement.code,
                    namespaces,
                    when_statement_watchers,
                    importable_names,
                    exported_names,
                )

            case FunctionDefinition():
                # Create the function object
                func = GulfOfMexicoFunction(
                    [arg.value for arg in statement.args],
                    statement.code,
                    statement.is_async,
                )
                # Add to namespace
                namespaces[-1][statement.name.value] = Variable(
                    statement.name.value,
                    [VariableLifetime(func, 100000000000, 0, True, True)],
                    [],
                )

            case ClassDeclaration():
                # Create a class object (simplified for now)
                class_obj = GulfOfMexicoObject(statement.name.value, {})
                # Execute the class body in a new scope
                class_namespace = {
                    statement.name.value: Name(statement.name.value, class_obj)
                }
                interpret_code_statements(
                    statement.code,
                    namespaces + [class_namespace],
                    async_statements,
                    when_statement_watchers + [{}],
                    importable_names,
                    exported_names,
                )
                # Populate class members into the class object's namespace (exclude the class self-name)
                for k, v in class_namespace.items():
                    if k == statement.name.value:
                        continue
                    class_obj.namespace[k] = v
                # Add the class to the namespace
                namespaces[-1][statement.name.value] = Name(
                    statement.name.value, class_obj
                )

            case DeleteStatement():
                # Mark value as deleted
                var, ns = get_name_and_namespace_from_namespaces(
                    statement.name.value, namespaces
                )
                if var and isinstance(var, Variable):
                    deleted_values.add(var.value)
                    if ns:
                        del ns[statement.name.value]

            case TryWhateverStatement():
                # Try to execute try block, if error occurs, run whatever block dismissively
                try:
                    interpret_code_statements(
                        statement.try_code,
                        namespaces + [{}],
                        async_statements,
                        when_statement_watchers + [{}],
                        importable_names,
                        exported_names,
                    )
                except Exception:
                    # Passive-aggressive error handling - just run the whatever block
                    interpret_code_statements(
                        statement.whatever_code,
                        namespaces + [{}],
                        async_statements,
                        when_statement_watchers + [{}],
                        importable_names,
                        exported_names,
                    )

            case ProcrastinationStatement():
                # Procrastination - maybe execute the code, maybe not
                probabilities = {
                    "later": 0.50,  # 50% chance
                    "eventually": 0.75,  # 75% chance
                    "whenever": 0.90,  # 90% chance
                }
                keyword = statement.keyword.value
                should_execute = random.random() < probabilities.get(keyword, 0.50)

                if should_execute:
                    interpret_code_statements(
                        statement.code,
                        namespaces + [{}],
                        async_statements,
                        when_statement_watchers + [{}],
                        importable_names,
                        exported_names,
                    )

            case CorporateSpeakStatement():
                # Corporate speak with satirical implementations
                keyword = statement.keyword.value
                args_values = [
                    evaluate_expression(
                        arg, namespaces, async_statements, when_statement_watchers
                    )
                    for arg in statement.args
                ]

                match keyword:
                    case "synergize":
                        # Combine two values (concatenate or add)
                        if len(args_values) >= 2:
                            val1, val2 = args_values[0], args_values[1]
                            if isinstance(val1, GulfOfMexicoString) or isinstance(
                                val2, GulfOfMexicoString
                            ):
                                result = GulfOfMexicoString(
                                    str(val1.value) + str(val2.value)
                                )
                            elif isinstance(val1, GulfOfMexicoNumber) and isinstance(
                                val2, GulfOfMexicoNumber
                            ):
                                result = GulfOfMexicoNumber(val1.value + val2.value)
                            else:
                                result = GulfOfMexicoString(
                                    str(val1.value) + str(val2.value)
                                )

                    case "leverage":
                        # Multiply value by 2 (leverage for maximum impact!)
                        if len(args_values) >= 1:
                            val = args_values[0]
                            if isinstance(val, GulfOfMexicoNumber):
                                result = GulfOfMexicoNumber(val.value * 2)
                            elif isinstance(val, GulfOfMexicoString):
                                result = GulfOfMexicoString(val.value * 2)
                            else:
                                result = val

                    case "paradigm_shift":
                        # Negate or reverse the value (complete paradigm shift!)
                        if len(args_values) >= 1:
                            val = args_values[0]
                            if isinstance(val, GulfOfMexicoNumber):
                                result = GulfOfMexicoNumber(-val.value)
                            elif isinstance(val, GulfOfMexicoBoolean):
                                result = GulfOfMexicoBoolean(
                                    not val.value if val.value is not None else None
                                )
                            elif isinstance(val, GulfOfMexicoString):
                                result = GulfOfMexicoString(val.value[::-1])
                            else:
                                result = val

                    case "circle_back":
                        # Defer execution (like 'later') - does nothing
                        pass

                    case "touch_base":
                        # Print a status update (touching base with stakeholders)
                        status_msgs = [
                            "Let's touch base on this.",
                            "I'll ping you later.",
                            "Let's put a pin in that.",
                            "Let's take this offline.",
                            "Let's loop back on this.",
                        ]
                        msg = random.choice(status_msgs)
                        print(f"[TOUCH_BASE] {msg}")

            case EmotionalStatement():
                # Emotional programming - execute based on program mood
                # Mood is tracked by error count in current scope
                keyword = statement.keyword.value
                error_count = getattr(interpret_code_statements, "_error_count", 0)

                execute = False
                match keyword:
                    case "happy":
                        # Execute if no recent errors (happy mood)
                        execute = error_count == 0
                        if execute:
                            print("😊 [HAPPY MODE]")

                    case "sad":
                        # Execute if 1-2 recent errors (sad mood)
                        execute = 1 <= error_count <= 2
                        if execute:
                            print("😢 [SAD MODE]")

                    case "angry":
                        # Execute if 3+ recent errors (angry mood)
                        execute = error_count >= 3
                        if execute:
                            print("😠 [ANGRY MODE]")

                    case "excited":
                        # Execute randomly with high energy (70% chance)
                        execute = random.random() < 0.70
                        if execute:
                            print("🎉 [EXCITED MODE]")

                    case "tired":
                        # Always execute but add a delay (0.5s)
                        execute = True
                        print("😴 [TIRED MODE] (executing slowly...)")
                        import time

                        time.sleep(0.5)

                if execute:
                    interpret_code_statements(
                        statement.code,
                        namespaces + [{}],
                        async_statements,
                        when_statement_watchers + [{}],
                        importable_names,
                        exported_names,
                    )

            case SuperstitiousStatement():
                # Superstitious programming - luck-based execution
                keyword = statement.keyword.value

                match keyword:
                    case "lucky":
                        # Lucky block - execute with good fortune
                        print("🍀 [LUCKY] Fingers crossed!")
                        try:
                            interpret_code_statements(
                                statement.code,
                                namespaces + [{}],
                                async_statements,
                                when_statement_watchers + [{}],
                                importable_names,
                                exported_names,
                            )
                            print("🍀 [LUCKY] Success! The luck held!")
                        except Exception as e:
                            # Even in lucky block, show error but continue
                            print(
                                f"🍀 [LUCKY] Uh oh, ran out of luck: {type(e).__name__}"
                            )

                    case "unlucky":
                        # Unlucky block - expect things to go wrong
                        print("💀 [UNLUCKY] This probably won't end well...")
                        try:
                            interpret_code_statements(
                                statement.code,
                                namespaces + [{}],
                                async_statements,
                                when_statement_watchers + [{}],
                                importable_names,
                                exported_names,
                            )
                            print("💀 [UNLUCKY] Wait, it actually worked? Surprising!")
                        except Exception as e:
                            print(f"💀 [UNLUCKY] Yep, knew it. {type(e).__name__}")

                    case "cross_fingers":
                        # Cross fingers - 50/50 chance
                        print("🤞 [CROSS_FINGERS] Here goes nothing...")
                        if random.random() < 0.50:
                            interpret_code_statements(
                                statement.code,
                                namespaces + [{}],
                                async_statements,
                                when_statement_watchers + [{}],
                                importable_names,
                                exported_names,
                            )
                            print("🤞 [CROSS_FINGERS] Phew, that worked out!")
                        else:
                            print("🤞 [CROSS_FINGERS] Nope, bad luck this time.")

                    case "knock_on_wood":
                        # Knock on wood - suppress errors
                        print("🪵 [KNOCK_ON_WOOD] *knock knock*")
                        try:
                            interpret_code_statements(
                                statement.code,
                                namespaces + [{}],
                                async_statements,
                                when_statement_watchers + [{}],
                                importable_names,
                                exported_names,
                            )
                        except Exception:
                            # Silently suppress errors (the wood protected us)
                            print("🪵 [KNOCK_ON_WOOD] The wood absorbed the bad luck!")

            case QuantumStatement():
                # Quantum programming - superposition variables
                # Create a variable that holds multiple possible values until observed
                var_name = statement.name.value

                # Evaluate the superposition value (statement.value is already tokens)
                expr_tree = build_expression_tree(filename, statement.value, code)
                superposition_value = evaluate_expression(
                    expr_tree,
                    namespaces,
                    filename,
                    code,
                )

                # Import global quantum states storage
                from gulfofmexico.builtin import QUANTUM_STATES

                # If it's a list, store all values as superposition
                if isinstance(superposition_value, GulfOfMexicoList):
                    QUANTUM_STATES[var_name] = superposition_value.values.copy()
                    print(
                        f"⚛️  [QUANTUM] Variable '{var_name}' in superposition of {len(superposition_value.values)} states"
                    )
                elif (
                    isinstance(superposition_value, GulfOfMexicoBoolean)
                    and superposition_value.value == 2
                ):
                    # 'maybe' creates true/false superposition
                    QUANTUM_STATES[var_name] = [
                        GulfOfMexicoBoolean(1),  # true
                        GulfOfMexicoBoolean(0),  # false
                    ]
                    print(
                        f"⚛️  [QUANTUM] Variable '{var_name}' in true/false superposition"
                    )
                else:
                    # Single value quantum state
                    QUANTUM_STATES[var_name] = [superposition_value]
                    print(f"⚛️  [QUANTUM] Variable '{var_name}' in quantum state")

                # Don't assign to namespace yet - it exists only in superposition!

            case GaslightingStatement():
                # Gaslighting variables - deny their existence
                var_name = statement.name.value

                # Evaluate the value
                expr_tree = build_expression_tree(filename, statement.value, code)
                value = evaluate_expression(
                    expr_tree,
                    namespaces,
                    filename,
                    code,
                )

                # Store as gaslighting variable with random behavior
                print(f"🤥 [GASLIGHTING] Creating variable '{var_name}' (or am I?)")

                # Actually create it but mark it as gaslighting
                from gulfofmexico.builtin import GASLIGHTING_VARS

                GASLIGHTING_VARS[var_name] = value

                # Also add to namespace so it "exists"
                namespaces[-1][var_name] = Name(var_name, value)

            case BlockchainStatement():
                # Blockchain buzzword satire
                keyword = statement.keyword.value

                match keyword:
                    case "blockchain":
                        print("⛓️  [BLOCKCHAIN] Initiating decentralized consensus...")
                        import time

                        time.sleep(0.3)  # "Mining" delay
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print(
                            "⛓️  [BLOCKCHAIN] Transaction validated on distributed ledger!"
                        )

                    case "smart_contract":
                        print(
                            "📜 [SMART_CONTRACT] Deploying trustless code execution..."
                        )
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("📜 [SMART_CONTRACT] Contract executed on chain!")

                    case "mine":
                        # Mining - waste CPU cycles
                        expr_tree = build_expression_tree(
                            filename, statement.args, code
                        )
                        blocks = evaluate_expression(
                            expr_tree, namespaces, filename, code
                        )
                        num_blocks = (
                            int(blocks.value)
                            if isinstance(blocks, GulfOfMexicoNumber)
                            else 1
                        )

                        print(f"⛏️  [MINING] Mining {num_blocks} block(s)...")
                        import time
                        import random

                        for i in range(num_blocks):
                            time.sleep(0.2)  # Simulate mining
                            hash_val = random.randint(1000, 9999)
                            print(f"⛏️  [MINING] Block {i+1} mined! Hash: 0x{hash_val}")

                        print(
                            f"⛏️  [MINING] Earned {num_blocks * 0.00001} cryptocurrency!"
                        )

                    case "immutable_ledger":
                        # Store value as "immutable" (but we can still change it because irony)
                        print(
                            "📒 [IMMUTABLE_LEDGER] Recording on permanent blockchain..."
                        )
                        # Just execute the args as an expression
                        expr_tree = build_expression_tree(
                            filename, statement.args, code
                        )
                        value = evaluate_expression(
                            expr_tree, namespaces, filename, code
                        )
                        print(
                            f"📒 [IMMUTABLE_LEDGER] Value permanently recorded: {value}"
                        )

            case AIBuzzwordStatement():
                # AI/ML buzzword satire
                keyword = statement.keyword.value

                match keyword:
                    case "deep_learning":
                        print("🧠 [DEEP_LEARNING] Initializing neural networks...")
                        print("🧠 [DEEP_LEARNING] Training on big data...")
                        import time

                        time.sleep(0.4)
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🧠 [DEEP_LEARNING] Model trained to 99.9% accuracy!")

                    case "neural_network":
                        print("🤖 [NEURAL_NETWORK] Forwarding through hidden layers...")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🤖 [NEURAL_NETWORK] Backpropagation complete!")

                    case "ai_powered":
                        print("🤖 [AI_POWERED] Applying machine learning algorithms...")
                        import time
                        import random

                        time.sleep(0.3)

                        # Add some "AI thinking"
                        confidence = random.randint(85, 99)
                        print(f"🤖 [AI_POWERED] AI confidence: {confidence}%")

                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🤖 [AI_POWERED] AI processing complete!")

            case AgileStatement():
                # Agile/Scrum methodology satire
                keyword = statement.keyword.value

                match keyword:
                    case "sprint":
                        print("🏃 [SPRINT] Starting 2-week sprint...")
                        import time

                        time.sleep(0.2)
                        print("🏃 [SPRINT] Sprint velocity: 42 story points")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🏃 [SPRINT] Sprint completed! Retrospective next.")

                    case "standup":
                        print("🗣️  [STANDUP] Daily standup meeting...")
                        print("🗣️  [STANDUP] Yesterday: Wrote code")
                        print("🗣️  [STANDUP] Today: Will write more code")
                        print("🗣️  [STANDUP] Blockers: None (lying)")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )

                    case "retro":
                        print("🔄 [RETRO] Retrospective meeting...")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🔄 [RETRO] What went well: Everything!")
                        print("🔄 [RETRO] What to improve: Nothing!")
                        print("🔄 [RETRO] Action items: [Empty]")

                    case "burndown":
                        print("📉 [BURNDOWN] Tracking burndown chart...")
                        import time

                        for i in range(3, 0, -1):
                            print(f"📉 [BURNDOWN] Tasks remaining: {i}")
                            time.sleep(0.15)
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("📉 [BURNDOWN] Sprint complete! (maybe)")

            case SecurityTheaterStatement():
                # Security theater satire
                keyword = statement.keyword.value

                match keyword:
                    case "encrypt":
                        print("🔐 [ENCRYPT] Applying military-grade encryption...")
                        print("🔐 [ENCRYPT] Algorithm: ROT13")
                        import time

                        time.sleep(0.3)
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🔐 [ENCRYPT] Data secured! (not really)")

                    case "two_factor":
                        print("🔑 [2FA] Initiating two-factor authentication...")
                        print("🔑 [2FA] Please confirm: Are you sure?")
                        print("🔑 [2FA] Please confirm again: Are you REALLY sure?")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🔑 [2FA] Authentication successful!")

                    case "penetration_test":
                        print("🔨 [PENTEST] Running penetration test...")
                        import time

                        time.sleep(0.2)
                        print("🔨 [PENTEST] *knock knock*")
                        time.sleep(0.2)
                        print("🔨 [PENTEST] Trying to break in...")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🔨 [PENTEST] Vulnerabilities found: 0 (we think)")

                    case "zero_trust":
                        print("🚫 [ZERO_TRUST] Applying zero-trust architecture...")
                        print("🚫 [ZERO_TRUST] Trust level: 0%")
                        print("🚫 [ZERO_TRUST] Verifying everything...")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🚫 [ZERO_TRUST] Still don't trust anyone.")

            case DevOpsStatement():
                # DevOps cargo cult satire
                keyword = statement.keyword.value

                match keyword:
                    case "containerize":
                        print("📦 [CONTAINER] Containerizing application...")
                        print("📦 [CONTAINER] FROM ubuntu:latest")
                        print("📦 [CONTAINER] RUN apt-get install everything")
                        import time

                        time.sleep(0.3)
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("📦 [CONTAINER] Image size: 8.5 GB (it's fine)")

                    case "orchestrate":
                        print("🎼 [ORCHESTRATE] Orchestrating containers...")
                        print("🎼 [ORCHESTRATE] Starting pod 1/47...")
                        print("🎼 [ORCHESTRATE] Configuring service mesh...")
                        import time

                        time.sleep(0.4)
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🎼 [ORCHESTRATE] Cluster healthy! (probably)")

                    case "microservice":
                        print("🔬 [MICROSERVICE] Converting to microservice...")
                        print("🔬 [MICROSERVICE] Latency increased by 300ms")
                        print("🔬 [MICROSERVICE] Complexity multiplied by 10")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🔬 [MICROSERVICE] Now distributed! (and broken)")

                    case "kubernetes":
                        print("☸️  [K8S] Deploying to Kubernetes...")
                        print("☸️  [K8S] Writing 47 YAML files...")
                        import time

                        time.sleep(0.5)
                        print("☸️  [K8S] kubectl apply -f *.yaml")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("☸️  [K8S] Error: CrashLoopBackOff (normal)")

            case StartupStatement():
                # Startup culture satire
                keyword = statement.keyword.value

                match keyword:
                    case "pivot":
                        print("🔄 [PIVOT] Pivoting business model...")
                        print("🔄 [PIVOT] Old idea: Abandoned")
                        print("🔄 [PIVOT] New idea: Revolutionary!")
                        import time

                        time.sleep(0.3)
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🔄 [PIVOT] We're definitely going to succeed now!")

                    case "disrupt":
                        print("💥 [DISRUPT] Disrupting the industry...")
                        print("💥 [DISRUPT] Move fast and break things!")
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("💥 [DISRUPT] Industry: Disrupted ✓")
                        print("💥 [DISRUPT] Things: Broken ✓")

                    case "unicorn":
                        print("🦄 [UNICORN] Achieving unicorn status...")
                        print("🦄 [UNICORN] Valuation: $1 billion (on paper)")
                        print("🦄 [UNICORN] Revenue: $47")
                        import time

                        time.sleep(0.4)
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🦄 [UNICORN] Welcome to the unicorn club! 🎉")

                    case "hockey_stick":
                        print("🏒 [HOCKEY_STICK] Achieving hockey stick growth...")
                        import time

                        # Exponential delays
                        for i in range(4):
                            delay = 0.1 * (1.5**i)
                            time.sleep(delay)
                            print(
                                f"🏒 [HOCKEY_STICK] Growth month {i+1}: {int(10 * (2**i))}%"
                            )
                        interpret_code_statements(
                            statement.code,
                            namespaces + [{}],
                            async_statements,
                            when_statement_watchers + [{}],
                            importable_names,
                            exported_names,
                        )
                        print("🏒 [HOCKEY_STICK] Exponential growth achieved! 📈")

            case ReverseStatement():
                # Reverse operation - reverses lists and strings in-place
                var, ns = get_name_and_namespace_from_namespaces(
                    statement.name.value, namespaces
                )
                if var is None:
                    raise_error_at_token(
                        filename,
                        code,
                        f"Cannot reverse undefined name: {statement.name.value}",
                        statement.name,
                    )

                value = var.value if isinstance(var, Name) else var.value

                if isinstance(value, GulfOfMexicoList):
                    # Reverse list in-place
                    value.values.reverse()
                    value.create_namespace()
                elif isinstance(value, GulfOfMexicoString):
                    # Reverse string - create new reversed string
                    reversed_str = value.value[::-1]
                    new_value = GulfOfMexicoString(reversed_str)
                    if isinstance(var, Variable):
                        var.add_lifetime(
                            new_value,
                            0,  # confidence 0 for auto-generated
                            100000000000,  # infinite duration
                            var.can_be_reset,
                            var.can_edit_value,
                        )
                    elif isinstance(var, Name):
                        var.value = new_value
                else:
                    raise_error_at_token(
                        filename,
                        code,
                        f"Cannot reverse type {type(value).__name__}. Only lists and strings can be reversed.",
                        statement.name,
                    )

            case ImportStatement():
                for name_token in statement.names:
                    name = name_token.value
                    found = False
                    for file_dict in importable_names.values():
                        if name in file_dict:
                            namespaces[-1][name] = Name(name, file_dict[name])
                            found = True
                            break
                    if not found:
                        raise_error_at_token(
                            filename,
                            code,
                            f"Cannot find imported name: {name}",
                            name_token,
                        )

            case ExportStatement():
                for name_token in statement.names:
                    name = name_token.value
                    v = get_name_from_namespaces(name, namespaces)
                    if v is None:
                        raise_error_at_token(
                            filename,
                            code,
                            f"Cannot export undefined name: {name}",
                            name_token,
                        )
                    value = v.value if isinstance(v, Name) else v.value
                    target = statement.target_file.value
                    exported_names.append((target, name, value))

    # Process async statements
    while async_statements:
        async_stmt = async_statements.pop(0)
        (statements_list, async_namespaces, current_index, direction) = async_stmt

        if current_index < len(statements_list):
            # Execute the current statement
            result = interpret_code_statements(
                [statements_list[current_index]],
                async_namespaces,
                async_statements,
                when_statement_watchers,
                importable_names,
                exported_names,
            )

            # Update index for next execution
            new_index = current_index + (1 if direction == 1 else -1)
            if 0 <= new_index < len(statements_list):
                async_statements.append(
                    (statements_list, async_namespaces, new_index, direction)
                )

    return result
