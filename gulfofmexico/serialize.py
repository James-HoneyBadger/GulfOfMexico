"""
Serialization for Gulf of Mexico Values

Converts Gulf of Mexico values and Python objects to/from JSON for:
    - Export/import between file sections
    - Global variable storage (const const const)
    - GitHub-based public globals repository

Serialization Format:
    {
        "gulfofmexico_obj_type": "GulfOfMexicoNumber",  # or "Name", "Variable", etc.
        "value": <serialized_data>
    }

Supported Types:
    - All GulfOfMexico value types (Number, String, List, etc.)
    - Name and Variable with lifetimes
    - Token and CodeStatement AST nodes
    - Python primitives (int, float, str, bool, list, dict)

Usage:
    - serialize_obj(value) -> dict: Convert to JSON-serializable dict
    - deserialize_obj(dict) -> value: Reconstruct from serialized dict

Note: Used by export/import statements and const const const global storage.
"""

import dataclasses
from typing import Any, Callable, Type, Union, assert_never
from gulfofmexico.base import NonFormattedError, Token, TokenType

from gulfofmexico.builtin import *
from gulfofmexico.processor.syntax_tree import *

from gulfofmexico.builtin import (
    KEYWORDS,
    BuiltinFunction,
    Name,
    GulfOfMexicoValue,
    Variable,
)
from gulfofmexico.processor.syntax_tree import CodeStatement

SerializedDict = dict[str, Union[str, dict, list]]
DataclassSerializations = Union[Name, Variable, GulfOfMexicoValue, CodeStatement, Token]


def serialize_obj(obj: Any) -> SerializedDict:
    """Convert Gulf of Mexico or Python object to JSON-serializable dict."""
    match obj:
        case Name() | Variable() | GulfOfMexicoValue() | CodeStatement() | Token():
            return serialize_gulfofmexico_obj(obj)
        case _:
            return serialize_python_obj(obj)


def deserialize_obj(val: dict) -> Any:
    if "gulfofmexico_obj_type" in val:
        return deserialize_gulfofmexico_obj(val)
    elif "python_obj_type" in val:
        return deserialize_python_obj(val)
    else:
        raise NonFormattedError(
            "Invalid object type in GulfOfMexico Variable deserialization."
        )


def serialize_python_obj(obj: Any) -> dict[str, Union[str, dict, list]]:
    match obj:
        case TokenType():
            val = obj.value
        case dict():
            if not all(isinstance(k, str) for k in obj):
                raise NonFormattedError(
                    "Serialization Error: Encountered non-string dictionary keys."
                )
            val = {k: serialize_obj(v) for k, v in obj.items()}
        case list() | tuple():
            val = [serialize_obj(x) for x in obj]
        case str():
            val = obj
        case None | int() | float() | bool():
            val = str(obj)
        case func if isinstance(func, Callable):
            val = func.__name__
        case _:
            assert_never(obj)
    return {
        "python_obj_type": (
            type(obj).__name__ if not isinstance(obj, Callable) else "function"
        ),
        "value": val,
    }


def deserialize_python_obj(val: dict) -> Any:
    if val["python_obj_type"] not in [
        "int",
        "float",
        "dict",
        "function",
        "list",
        "tuple",
        "str",
        "TokenType",
        "NoneType",
        "bool",
    ]:
        print(val["python_obj_type"])
        raise NonFormattedError(
            "Invalid `python_obj_type` detected in deserialization."
        )

    match val["python_obj_type"]:
        case "list":
            return [deserialize_obj(x) for x in val["value"]]
        case "tuple":
            return tuple(deserialize_obj(x) for x in val["value"])
        case "dict":
            return {k: deserialize_obj(v) for k, v in val["value"].items()}
        case "int" | "float" | "str":
            return eval(val["python_obj_type"])(val["value"])  # RAISES ValueError
        case "NoneType":
            return None
        case "bool":
            if val["value"] not in ["True", "False"]:
                raise NonFormattedError(
                    "Invalid boolean detected in object deserialization."
                )
            return eval(val["value"])
        case "TokenType":
            if v := TokenType.from_val(val["value"]):
                return v
            raise NonFormattedError(
                "Invalid TokenType detected in object deserialization."
            )
        case "function":
            if val["value"] in [
                "db_list_pop",
                "db_list_push",
                "db_str_pop",
                "db_str_push",
            ]:
                return eval(val["value"])  # trust me bro this is W code
            if not (v := KEYWORDS.get(val["value"])) or not isinstance(
                v.value, BuiltinFunction
            ):
                raise NonFormattedError(
                    "Invalid builtin function detected in object deserialization."
                )
            return v.value.function
        case invalid:
            assert_never(invalid)


def serialize_gulfofmexico_obj(
    val: DataclassSerializations,
) -> dict[str, Union[str, dict, list]]:
    return {
        "gulfofmexico_obj_type": type(val).__name__,
        "attributes": [
            {"name": field.name, "value": serialize_obj(getattr(val, field.name))}
            for field in dataclasses.fields(val)  # type: ignore
        ],
    }


def get_subclass_name_list(cls: Type[DataclassSerializations]) -> list[str]:
    return [*map(lambda x: x.__name__, cls.__subclasses__())]


def deserialize_gulfofmexico_obj(val: dict) -> DataclassSerializations:
    if val["gulfofmexico_obj_type"] not in [
        "Name",
        "Variable",
        "Token",
        *get_subclass_name_list(CodeStatement),
        *get_subclass_name_list(GulfOfMexicoValue),
    ]:
        raise NonFormattedError(
            "Invalid `gulfofmexico_obj_type` detected in deserialization."
        )

    # beautiful, elegant, error-free, safe python code :D
    attrs = {at["name"]: deserialize_obj(at["value"]) for at in val["attributes"]}
    return eval(val["gulfofmexico_obj_type"])(**attrs)


if __name__ == "__main__":

    list_test_case = GulfOfMexicoList(
        [
            GulfOfMexicoString("Hello world!"),
            GulfOfMexicoNumber(123.45),
        ]
    )
    serialized = serialize_obj(list_test_case)
    __import__("pprint").pprint(serialized)
    assert list_test_case == deserialize_obj(serialized)
