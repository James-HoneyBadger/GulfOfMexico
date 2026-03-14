"""
Built-in Types and Functions for Gulf of Mexico

Defines all value types, variables, and built-in functions available in Gulf of Mexico.

Value Types:
    - GulfOfMexicoNumber: Numeric values with indexing support
    - GulfOfMexicoString: Strings with fractional indexing
    - GulfOfMexicoList: Lists with -1 based indexing
    - GulfOfMexicoBoolean: Three-valued logic (true/false/maybe)
    - GulfOfMexicoFunction: User-defined and async functions
    - GulfOfMexicoObject: Class instances with namespaces
    - GulfOfMexicoMap: Key-value dictionaries
    - GulfOfMexicoPromise: Async value placeholders
    - GulfOfMexicoKeyword: Reserved language keywords
    - GulfOfMexicoUndefined: Undefined/null value

Variable System:
    - Variable: Probabilistic values with confidence levels
    - VariableLifetime: Temporal and line-based expiration
    - Name: Immutable named values

Key Features:
    - Fractional indexing: insert between elements (list[0.5] = x)
    - -1 indexing: arrays start at -1 instead of 0
    - Three-valued boolean logic for uncertainty
    - Confidence-based variable lifetimes
    - Mutable vs immutable modifiers (const/var)

Built-in Functions:
    - Type conversions: Number(), String(), Boolean()
    - I/O: print(), read(), write()
    - Control: sleep(), exit()
    - Data structures: Map(), use() for signals
    - Regex: regex_match(), regex_findall(), regex_replace()
    - Word numbers: one, two, twenty, thirty, etc.
"""

from __future__ import annotations

import functools
import math as _math
import random as _random
import time
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from time import sleep
from typing import Callable, Optional, Union

from gulfofmexico.base import NonFormattedError
from gulfofmexico.processor.syntax_tree import CodeStatement

__all__ = [
    "GulfOfMexicoFunction",
    "BuiltinFunction",
    "GulfOfMexicoList",
    "GulfOfMexicoNumber",
    "GulfOfMexicoString",
    "GulfOfMexicoBoolean",
    "GulfOfMexicoUndefined",
    "GulfOfMexicoSpecialBlankValue",
    "GulfOfMexicoObject",
    "GulfOfMexicoPendingInit",
    "GulfOfMexicoMap",
    "GulfOfMexicoKeyword",
    "GulfOfMexicoPromise",
]

FLOAT_TO_INT_PREC = 0.00000001


def is_int(x: Union[float, int]) -> bool:
    return min(x % 1, 1 - x % 1) < FLOAT_TO_INT_PREC


def db_not(x: GulfOfMexicoBoolean) -> GulfOfMexicoBoolean:
    if x.value is None:
        return GulfOfMexicoBoolean(None)
    return GulfOfMexicoBoolean(not x.value)


def db_list_push(self: GulfOfMexicoList, val: GulfOfMexicoValue) -> None:
    self.values.append(val)
    new_index = max(self.indexer.keys()) + 1 if self.indexer else 0
    self.indexer[new_index] = len(self.values) - 1
    self.create_namespace()  # update the length


def db_list_pop(
    self: GulfOfMexicoList,
    index: Union[GulfOfMexicoNumber, GulfOfMexicoSpecialBlankValue],
) -> GulfOfMexicoValue:
    if isinstance(index, GulfOfMexicoSpecialBlankValue):
        retval = self.values.pop()
        self.create_namespace()
        return retval
    elif not isinstance(index, GulfOfMexicoNumber) or not is_int(index.value):
        raise NonFormattedError("Expected integer for list popping.")
    elif not -1 <= index.value <= len(self.values) - 2:
        raise NonFormattedError("Indexing out of list bounds.")
    retval = self.values.pop(round(index.value) + 1)
    self.create_namespace()
    return retval


def db_str_push(self: GulfOfMexicoString, val: GulfOfMexicoValue) -> None:
    val_str = db_to_string(val).value
    max_user_index = max(self.indexer.keys())
    if len(val_str) > 1:
        self.indexer[max_user_index + 1] = (len(self.value) - 1, val_str[1:])
    else:
        self.indexer[max_user_index + 1] = (len(self.value) - 1, "")
    self.value += val_str
    # print(max(self.indexer.keys())+1)
    self.create_namespace()  # update the length


def db_str_pop(
    self: GulfOfMexicoString,
    index: Union[GulfOfMexicoNumber, GulfOfMexicoSpecialBlankValue],
) -> GulfOfMexicoValue:
    if isinstance(index, GulfOfMexicoSpecialBlankValue):
        retval = self.value[-1]
        self.value = self.value[:-1]
        return GulfOfMexicoString(retval)
    elif not isinstance(index, GulfOfMexicoNumber) or not is_int(index.value):
        raise NonFormattedError("Expected integer for string popping.")
    elif not -1 <= index.value <= len(self.value) - 1:
        raise NonFormattedError("Indexing out of string bounds.")
    index_val = round(index.value) + 1
    retval = self.value[index_val]
    self.value = self.value[:index_val] + self.value[index_val + 1:]
    return GulfOfMexicoString(retval)


# Note: Consider metaclass approach for future extensibility
# class Value(metaclass=ABCMeta):   # Could allow for more objects without much complexity
#     @abstractmethod
#     def to_bool(self) -> Value: pass
#     @abstractmethod
#     def to_num(self) -> Value: pass
#     @abstractmethod
#     def to_str(self) -> Value: pass


class GulfOfMexicoValue:  # base class for shit
    pass


class GulfOfMexicoMutable(GulfOfMexicoValue):  # mutable values
    pass


class GulfOfMexicoIndexable(GulfOfMexicoValue, metaclass=ABCMeta):
    @abstractmethod
    def access_index(self, index: GulfOfMexicoValue) -> GulfOfMexicoValue:
        pass

    @abstractmethod
    def assign_index(self, index: GulfOfMexicoValue, val: GulfOfMexicoValue) -> None:
        pass


class GulfOfMexicoNamespaceable(GulfOfMexicoValue, metaclass=ABCMeta):
    namespace: dict[str, Union[Name, Variable]]


@dataclass
class GulfOfMexicoFunction(GulfOfMexicoValue):
    args: list[str]
    code: list[tuple[CodeStatement, ...]]
    is_async: bool


@dataclass
class BuiltinFunction(GulfOfMexicoValue):
    arg_count: int
    function: Callable
    modifies_caller: bool = False


@dataclass
class GulfOfMexicoList(
    GulfOfMexicoIndexable,
    GulfOfMexicoNamespaceable,
    GulfOfMexicoMutable,
    GulfOfMexicoValue,
):
    values: list[GulfOfMexicoValue]
    indexer: dict[float, int] = field(init=False)  # used for converting the user decimal indecies to the real indecies
    namespace: dict[str, Union[Name, Variable]] = field(default_factory=dict)

    def __post_init__(self):
        self.create_namespace(False)
        self.indexer = dict()
        # Initialize indexer with -1 based indexing per spec
        # User index -1 = first element (real 0), 0 = second (real 1), etc.
        list_len = len(self.values)
        for i in range(list_len):
            self.indexer[i - 1] = i  # user (i-1) → real i

    def create_namespace(self, is_update: bool = True) -> None:
        if not is_update:
            self.namespace = {
                "push": Name("push", BuiltinFunction(2, db_list_push, True)),
                "pop": Name("pop", BuiltinFunction(2, db_list_pop, True)),
                "length": Name("length", GulfOfMexicoNumber(len(self.values))),
            }
        elif is_update:
            self.namespace |= {
                "length": Name("length", GulfOfMexicoNumber(len(self.values))),
            }

    def access_index(self, index: GulfOfMexicoValue) -> GulfOfMexicoValue:
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a list with a non-number value.")
        list_len = len(self.values)
        # -1 based: valid range is -1 to list_len - 2
        if not -1 <= index.value <= list_len - 2:
            raise NonFormattedError("Indexing out of list bounds.")
        elif index.value not in self.indexer:
            raise NonFormattedError("No value assigned to that index")  # if inbounds index doesnt have assigned val
        user_index = index.value
        # print("user index:" + str(user_index))
        realIndex = self.indexer.get(user_index)
        # print("real index:" + str(realIndex))
        if realIndex is None:
            raise NonFormattedError("Index not found")
        return self.values[round(realIndex)]

    def assign_index(self, index: GulfOfMexicoValue, val: GulfOfMexicoValue) -> None:
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a list with a non-number value.")
        list_len = len(self.values)
        if index.value in self.indexer:
            # -1 based: valid range is -1 to list_len - 2
            if not -1 <= index.value <= list_len - 2:
                raise NonFormattedError("Indexing out of list bounds.")
            real_idx = self.indexer.get(index.value)
            if real_idx is None:
                raise NonFormattedError("Index not found")
            self.values[round(real_idx)] = val
        else:  # assign in the middle of the array (fractional indexing)
            if not -1 <= index.value <= list_len - 2:
                raise NonFormattedError("Indexing out of list bounds.")
            # Convert -1-based user index to real position: real = user + 1
            nearest_int_down = round(max((index.value + 2) // 1, 0))
            self.values[nearest_int_down:nearest_int_down] = [val]
            self.indexer[index.value] = nearest_int_down
            self.create_namespace()
            # all real indexes after the inserted item need 1 to be added to them
            user_indicies = self.indexer.keys()
            for user_index in user_indicies:
                if user_index > index.value:
                    self.indexer[user_index] += 1


@dataclass(unsafe_hash=True)
class GulfOfMexicoNumber(GulfOfMexicoIndexable, GulfOfMexicoMutable, GulfOfMexicoValue):
    value: Union[int, float]

    def _get_self_str(self) -> str:
        return str(self.value).replace(".", "").replace("-", "")

    def access_index(self, index: GulfOfMexicoValue) -> GulfOfMexicoValue:
        self_val_str = self._get_self_str()
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a number with a non-number value.")
        if not is_int(index.value):
            raise NonFormattedError("Expected integer for number indexing.")
        elif not -1 <= index.value <= len(self_val_str) - 2:
            raise NonFormattedError("Indexing out of number bounds.")
        return GulfOfMexicoNumber(int(self_val_str[round(index.value) + 1]))

    def assign_index(self, index: GulfOfMexicoValue, val: GulfOfMexicoValue) -> None:
        self_val_str = self._get_self_str()
        if not is_int(self.value):
            raise NonFormattedError("Cannot assign into a non-integer number.")
        if self.value == 0:
            sign = 1
        else:
            sign = int(self.value / abs(self.value))
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a number with a non-number value.")
        if not isinstance(val, GulfOfMexicoNumber) or not is_int(val.value) or not 0 <= val.value <= 9:
            raise NonFormattedError("Cannot assign into a number with a non-integer value.")
        if is_int(index.value):
            if not -1 <= index.value <= len(self_val_str) - 2:
                raise NonFormattedError("Indexing out of number bounds.")
            index_num = round(index.value) + 1
            self.value = sign * int(self_val_str[:index_num] + str(round(val.value)) + self_val_str[index_num + 1:])
        else:  # assign in the middle of the array
            index_num = round(max((index.value + 2) // 1, 0))
            self.value = sign * int(self_val_str[:index_num] + str(round(val.value)) + self_val_str[index_num:])


@dataclass(unsafe_hash=True)
class GulfOfMexicoString(
    GulfOfMexicoIndexable,
    GulfOfMexicoNamespaceable,
    GulfOfMexicoMutable,
    GulfOfMexicoValue,
):
    value: str = field(hash=True)
    indexer: dict[float, tuple] = field(
        init=False, hash=False
    )  # used for converting the user decimal indecies to the real indecies
    # tuple stores the real index in the first slot and any extra characters in the second
    namespace: dict[str, Union[Name, Variable]] = field(default_factory=dict, hash=False)

    def __post_init__(self):
        self.create_namespace(False)
        self.indexer = dict()
        for index in range(len(self.value)):
            self.indexer[index - 1] = (index - 1, "")

    def create_namespace(self, is_update: bool = True):
        if not is_update:
            self.namespace |= {
                "push": Name("push", BuiltinFunction(2, db_str_push, True)),
                "pop": Name("pop", BuiltinFunction(2, db_str_pop, True)),
                "length": Name("length", GulfOfMexicoNumber(len(self.value))),
            }
        else:
            self.namespace["length"] = Name("length", GulfOfMexicoNumber(len(self.value)))

    def access_index(self, index: GulfOfMexicoValue) -> GulfOfMexicoValue:
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a string with a non-number value.")
        # if not is_int(index.value):
        #    raise NonFormattedError("Expected integer for string indexing.")
        if not -1 <= index.value <= len(self.value) - 2:
            raise NonFormattedError("Indexing out of string bounds.")
        elif index.value not in self.indexer:
            raise NonFormattedError("No value assigned to that index")  # if inbounds index doesnt have assigned val
        user_index = index.value
        index_data = self.indexer[user_index]
        real_index = index_data[0]
        extra_characters = index_data[1]
        return GulfOfMexicoString(self.value[real_index + 1] + extra_characters)

    def assign_index(self, index: GulfOfMexicoValue, val: GulfOfMexicoValue) -> None:
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a string with a non-number value.")
        val_str = db_to_string(val).value
        if index.value in self.indexer:
            # # add, when modifying, reduce user indexes by the length of the replaced index's extra characters
            indexer_data = self.indexer[index.value]
            index_num = indexer_data[0] + 1
            excess_length = len(indexer_data[1])
            self.value = self.value[:index_num] + val_str + self.value[index_num + excess_length + 1:]
            if len(val_str) > 1:
                indexer_data = (indexer_data[0], val_str[:-1])
            else:
                indexer_data = (indexer_data[0], "")
            self.indexer[index.value] = indexer_data
            user_indicies = self.indexer.keys()
            for user_index in user_indicies:
                if user_index > index.value:
                    indexer_data = self.indexer[user_index]
                    indexer_data = (indexer_data[0] - excess_length, indexer_data[1])
                    self.indexer[user_index] = indexer_data
            self.create_namespace()

        else:  # assign in the middle of the array
            if not -1 <= index.value <= len(self.value) - 2:
                raise NonFormattedError("Indexing out of string bounds.")
            index_num = round(max((index.value + 2) // 1, 0))
            self.value = self.value[:index_num] + val_str + self.value[index_num:]
            if len(val_str) > 1:
                indexer_data = (index_num - 1, val_str[1:])
            else:
                indexer_data = (index_num - 1, "")
            self.indexer[index.value] = indexer_data
            user_indicies = self.indexer.keys()
            for user_index in user_indicies:
                if user_index > index.value:
                    # print(f"updating user index {user_index},{self.indexer[user_index]}")
                    indexer_data = self.indexer[user_index]
                    indexer_data = (indexer_data[0] + len(val_str), indexer_data[1])
                    self.indexer[user_index] = indexer_data
            self.create_namespace()


@dataclass
class GulfOfMexicoBoolean(GulfOfMexicoValue):
    value: Optional[bool]  # none represents maybe?


@dataclass
class GulfOfMexicoUndefined(GulfOfMexicoValue):
    pass


@dataclass
class GulfOfMexicoSpecialBlankValue(GulfOfMexicoValue):
    pass


@dataclass
class GulfOfMexicoObject(GulfOfMexicoNamespaceable, GulfOfMexicoValue):
    class_name: str
    namespace: dict[str, Union[Name, Variable]] = field(default_factory=dict)


@dataclass(unsafe_hash=True)
class GulfOfMexicoPendingInit(GulfOfMexicoValue):
    """Wrapper for newly created object with pending init call."""

    instance: GulfOfMexicoObject
    init_args: tuple[GulfOfMexicoValue, ...]


@dataclass
class GulfOfMexicoMap(GulfOfMexicoIndexable, GulfOfMexicoValue):
    self_dict: dict[Union[int, float, str], GulfOfMexicoValue]

    def access_index(self, index: GulfOfMexicoValue) -> GulfOfMexicoValue:
        if not isinstance(index, (GulfOfMexicoString, GulfOfMexicoNumber)):
            raise NonFormattedError("Keys of a map must be an index or a number.")
        if index.value not in self.self_dict:
            raise NonFormattedError(f"Key '{index.value}' not found in map.")
        return self.self_dict[index.value]

    def assign_index(self, index: GulfOfMexicoValue, val: GulfOfMexicoValue) -> None:
        if not isinstance(index, (GulfOfMexicoString, GulfOfMexicoNumber)):
            raise NonFormattedError("Keys of a map must be an index or a number.")
        self.self_dict[index.value] = val


@dataclass
class GulfOfMexicoKeyword(GulfOfMexicoValue):
    value: str


@dataclass
class GulfOfMexicoPromise(GulfOfMexicoValue):
    value: Optional[GulfOfMexicoValue]


@dataclass
class Name:
    name: str
    value: GulfOfMexicoValue


@dataclass
class VariableLifetime:
    value: GulfOfMexicoValue
    lines_left: int
    confidence: int
    can_be_reset: bool
    can_edit_value: bool
    creation_time: float = field(default_factory=time.time)
    is_temporal: bool = False
    temporal_duration: float = 0.0


@dataclass
class Variable:
    name: str
    lifetimes: list[VariableLifetime]
    prev_values: list[GulfOfMexicoValue]

    def __init__(
        self,
        name: str,
        lifetimes: list[VariableLifetime],
        prev_values: list[GulfOfMexicoValue],
    ):
        self.name = name
        self.lifetimes = lifetimes
        self.prev_values = prev_values

    @property
    def can_be_reset(self) -> bool:
        if self.lifetimes:
            return self.lifetimes[0].can_be_reset
        raise NonFormattedError("Variable is undefined.")

    @property
    def can_edit_value(self) -> bool:
        if self.lifetimes:
            return self.lifetimes[0].can_edit_value
        raise NonFormattedError("Variable is undefined.")

    def add_lifetime(
        self,
        value: GulfOfMexicoValue,
        confidence: int,
        duration: int,
        can_be_reset: bool,
        can_edit_value: bool,
        is_temporal: bool = False,
        temporal_duration: float = 0.0,
    ) -> None:
        # Insert sorted by *descending* confidence so lifetimes[0] is the
        # highest-priority value (more !'s = higher priority per spec).
        new_lt = VariableLifetime(
            value,
            duration,
            confidence,
            can_be_reset,
            can_edit_value,
            is_temporal=is_temporal,
            temporal_duration=temporal_duration,
        )
        inserted = False
        for i in range(len(self.lifetimes)):
            if confidence >= self.lifetimes[i].confidence:
                if i == 0:
                    self.prev_values.append(self.value)
                self.lifetimes.insert(i, new_lt)
                inserted = True
                break
        if not inserted:
            self.lifetimes.append(new_lt)

    def clear_outdated_lifetimes(self) -> None:
        remove_indeces = []
        current_time = time.time()
        for i, lt in enumerate(self.lifetimes):
            if lt.lines_left == 0 or (lt.is_temporal and current_time - lt.creation_time >= lt.temporal_duration):
                remove_indeces.append(i)
        for i in reversed(remove_indeces):
            del self.lifetimes[i]

    @property
    def value(self) -> GulfOfMexicoValue:
        if self.lifetimes:
            return self.lifetimes[0].value
        raise NonFormattedError("Variable is undefined.")


def all_function_keywords() -> list[str]:
    # this code boutta be crazy
    # i refuse to use the builtin combinations
    keywords = set()
    for f_ in range(2):
        for u_ in range(2):
            for n_ in range(2):
                for c_ in range(2):
                    for t_ in range(2):
                        for i_ in range(2):
                            for o_ in range(2):
                                for n2_ in range(2):
                                    kw = "" .join(
                                        [
                                            ch * flag
                                            for ch, flag in zip(
                                                "function",
                                                [f_, u_, n_, c_, t_, i_, o_, n2_],
                                            )
                                        ]
                                    ) or "fn"
                                    keywords.add(kw)
    return list(keywords)


FUNCTION_KEYWORDS = all_function_keywords()
_KEYWORD_LIST = [
    "class",
    "className",
    "after",
    "const",
    "var",
    "when",
    "if",
    "else",
    "async",
    "return",
    "delete",
    "await",
    "previous",
    "next",
    "reverse",
    "export",
    "import",
    "to",
] + FUNCTION_KEYWORDS

KEYWORDS = {
    kw: Name(kw, GulfOfMexicoKeyword(kw))
    for kw in _KEYWORD_LIST
}


def db_identity(val: GulfOfMexicoValue) -> GulfOfMexicoValue:
    return val


def db_new(val: GulfOfMexicoValue, *args: GulfOfMexicoValue) -> GulfOfMexicoValue:
    """Instantiate a new object from a class object.

    If the input is a GulfOfMexicoObject (class), create a fresh instance with
    the same class_name and a deep-copied namespace so instances don't share
    mutable state. If additional arguments are provided and an 'init' method
    exists, returns a PendingInit wrapper for the interpreter to process.
    Otherwise, behave like identity.
    """
    from copy import deepcopy

    if isinstance(val, GulfOfMexicoObject):
        # Deep copy the namespace entries into a brand new object
        new_namespace: dict[str, Union[Name, Variable]] = {}
        for key, entry in val.namespace.items():
            if isinstance(entry, Variable):
                # Copy current lifetime value and preserve permissions/confidence
                if not entry.lifetimes:
                    continue
                top = entry.lifetimes[0]
                copied_value = deepcopy(top.value)
                new_var = Variable(key, [], [])
                new_var.add_lifetime(
                    copied_value,
                    top.confidence,
                    100000000000,  # effectively infinite
                    entry.can_be_reset,
                    entry.can_edit_value,
                )
                new_namespace[key] = new_var
            elif isinstance(entry, Name):
                new_namespace[key] = Name(key, deepcopy(entry.value))

        instance = GulfOfMexicoObject(val.class_name, new_namespace)

        # If args provided and init exists, return pending init wrapper
        if args and "init" in new_namespace:
            return GulfOfMexicoPendingInit(instance, args)

        return instance

    # Fallback to identity for non-class values
    return val


def db_map() -> GulfOfMexicoMap:
    return GulfOfMexicoMap({})


def db_to_boolean(val: GulfOfMexicoValue) -> GulfOfMexicoBoolean:
    return_bool = None
    match val:
        case GulfOfMexicoString():
            return_bool = bool(val.value.strip()) or (None if val.value and not val.value.strip() else False)
        case GulfOfMexicoNumber():  # maybe if it is 0.xxx, false if it is 0, true if anything else
            return_bool = bool(round(val.value)) or (None if abs(val.value) > FLOAT_TO_INT_PREC else False)
        case GulfOfMexicoList():
            return_bool = bool(val.values)
        case GulfOfMexicoMap():
            return_bool = bool(val.self_dict)
        case GulfOfMexicoBoolean():
            return_bool = val.value
        case GulfOfMexicoUndefined():
            return_bool = False
        case GulfOfMexicoFunction() | GulfOfMexicoObject() | GulfOfMexicoKeyword():
            return_bool = None  # maybe for these cause im mischevious
    return GulfOfMexicoBoolean(return_bool)


def db_to_string(val: GulfOfMexicoValue) -> GulfOfMexicoString:
    return_string = str(val)
    match val:
        case GulfOfMexicoString():
            return_string = val.value
        case GulfOfMexicoList():
            return_string = f"[{', '.join([db_to_string(v).value for v in val.values])}]"
        case GulfOfMexicoBoolean():
            return_string = "true" if val.value else "maybe" if val.value is None else "false"
        case GulfOfMexicoNumber():
            return_string = str(val.value)
        case GulfOfMexicoFunction():
            return_string = f"<function ({', '.join(val.args)})>"
        case GulfOfMexicoObject():
            return_string = f"<object {val.class_name}>"
        case GulfOfMexicoUndefined():
            return_string = "undefined"
        case GulfOfMexicoKeyword():
            return_string = val.value
        case GulfOfMexicoMap():
            return_string = f'{{{", ".join([f"{k}: {db_to_string(v).value}" for k, v in val.self_dict.items()])}}}'
    return GulfOfMexicoString(return_string)


# Buffer for debug messages. We collect debug-related messages here and only
# flush them to stderr when an unexpected error occurs (or when the
# GULFOFMEXICO_DEBUG env var is explicitly set).
_DEBUG_LOGS: list[str] = []


def db_print(*vals: GulfOfMexicoValue) -> None:
    """Primary print function exposed to GOM programs.

    This prints program output to stdout immediately. Debug metadata that was
    previously written to stderr (the "[DB_PRINT] ..." lines) is now buffered
    in `_DEBUG_LOGS`. The buffer is flushed to stderr only when an error
    occurs or when the environment variable `GULFOFMEXICO_DEBUG` is set.
    """
    import os
    import sys

    output = " ".join([db_to_string(v).value for v in vals])
    print(output)
    sys.stdout.flush()

    # Prepare debug entry
    debug_entry = f"[DB_PRINT] Called with: {repr(output)}"

    # If explicit debug mode is enabled, write immediately. Otherwise buffer.
    if os.environ.get("GULFOFMEXICO_DEBUG"):
        sys.stderr.write(debug_entry + "\n")
        sys.stderr.flush()
    else:
        _DEBUG_LOGS.append(debug_entry)


def flush_debug_logs() -> None:
    """Flush buffered debug messages to stderr.

    Called by the interpreter when an exception occurs so the developer can see
    the recent internal debug lines that led up to the failure.
    """
    import sys

    if not _DEBUG_LOGS:
        return

    # If the user explicitly asked for debug, we may have already written lines.
    # Still write any buffered messages to stderr for completeness.
    for entry in _DEBUG_LOGS:
        sys.stderr.write(entry + "\n")
    sys.stderr.flush()
    _DEBUG_LOGS.clear()


def db_to_number(val: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    return_number: int | float = 0
    match val:
        case GulfOfMexicoNumber():
            return_number = val.value
        case GulfOfMexicoString():
            try:
                return_number = float(val.value)
            except ValueError as exc:
                raise NonFormattedError(f"Cannot convert string '{val.value}' to a number.") from exc
        case GulfOfMexicoUndefined():
            return_number = 0
        case GulfOfMexicoBoolean():
            return_number = int(val.value is not None and val.value) + (val.value is None) * 0.5
        case GulfOfMexicoList():
            if val.values:
                raise NonFormattedError("Cannot turn a non-empty list into a number.")
            return_number = 0
        case GulfOfMexicoMap():
            if val.self_dict:
                raise NonFormattedError("Cannot turn a non-empty map into a number.")
            return_number = 0
        case _:
            raise NonFormattedError(f"Cannot turn type {type(val).__name__} into a number.")
    return GulfOfMexicoNumber(return_number)


def db_signal(starting_value: GulfOfMexicoValue) -> GulfOfMexicoValue:
    obj = Name("", starting_value)

    def signal_func(*args: GulfOfMexicoValue) -> Optional[GulfOfMexicoValue]:
        nonlocal obj
        if not args or isinstance(args[0], GulfOfMexicoSpecialBlankValue):
            return obj.value
        else:
            obj.value = args[0]
            return None

    return BuiltinFunction(-1, signal_func)


def db_sleep(t: GulfOfMexicoValue) -> None:
    if not isinstance(t, GulfOfMexicoNumber):
        raise NonFormattedError("'sleep' function requires numerical input.")
    sleep(t.value)


def db_read(prompt: GulfOfMexicoValue) -> GulfOfMexicoString:
    """Read a line from stdin with an optional prompt per spec."""
    if not isinstance(prompt, GulfOfMexicoString):
        raise NonFormattedError("'read' function requires argument to be a string")
    try:
        result = input(prompt.value)
    except EOFError:
        result = ""
    return GulfOfMexicoString(result)


def db_readfile(path: GulfOfMexicoValue) -> GulfOfMexicoString:
    """Read contents of a file and return as a string."""
    if not isinstance(path, GulfOfMexicoString):
        raise NonFormattedError("'readfile' function requires argument to be a string")
    try:
        with open(path.value, encoding="utf-8") as f:
            s = f.read()
    except FileNotFoundError as exc:
        raise NonFormattedError(f"File not found: '{path.value}'") from exc
    except PermissionError as exc:
        raise NonFormattedError(f"Permission denied: '{path.value}'") from exc
    except OSError as exc:
        raise NonFormattedError(f"Error reading file '{path.value}': {exc}") from exc
    return GulfOfMexicoString(s)


def db_regex_match(arg: GulfOfMexicoString) -> GulfOfMexicoBoolean:
    if not isinstance(arg, GulfOfMexicoString):
        raise NonFormattedError("regex_match requires pattern,string")

    parts = arg.value.split(",", 1)
    if len(parts) != 2:
        raise NonFormattedError("regex_match requires pattern,string")

    pattern, string = parts
    import re

    try:
        return GulfOfMexicoBoolean(bool(re.search(pattern, string)))
    except re.error as e:
        raise NonFormattedError(f"Invalid regex pattern: {e}") from e


def db_regex_findall(arg: GulfOfMexicoString) -> GulfOfMexicoList:
    if not isinstance(arg, GulfOfMexicoString):
        raise NonFormattedError("regex_findall requires pattern,string")

    parts = arg.value.split(",", 1)
    if len(parts) != 2:
        raise NonFormattedError("regex_findall requires pattern,string")

    pattern, string = parts
    import re

    try:
        matches = re.findall(pattern, string)
        return GulfOfMexicoList([GulfOfMexicoString(match) for match in matches])
    except re.error as e:
        raise NonFormattedError(f"Invalid regex pattern: {e}") from e


def db_regex_replace(arg: GulfOfMexicoString) -> GulfOfMexicoString:
    if not isinstance(arg, GulfOfMexicoString):
        raise NonFormattedError("regex_replace: pattern,replacement,string")

    parts = arg.value.split(",", 2)
    if len(parts) != 3:
        raise NonFormattedError("regex_replace: pattern,replacement,string")

    pattern, replacement, string = parts
    import re

    try:
        result = re.sub(pattern, replacement, string)
        return GulfOfMexicoString(result)
    except re.error as e:
        raise NonFormattedError(f"Invalid regex pattern: {e}") from e


def db_write(path: GulfOfMexicoValue, content: GulfOfMexicoValue) -> None:
    if not isinstance(path, GulfOfMexicoString):
        raise NonFormattedError("'write' requires path to be a string")
    content_str = db_to_string(content).value
    try:
        with open(path.value, "w", encoding="utf-8") as f:
            f.write(content_str)
    except PermissionError as exc:
        raise NonFormattedError(f"Permission denied: '{path.value}'") from exc
    except OSError as exc:
        raise NonFormattedError(f"Error writing file '{path.value}': {exc}") from exc


def db_exit() -> None:
    import sys as _sys  # pylint: disable=import-outside-toplevel
    _sys.exit()


def __number_function_maker(num: int) -> BuiltinFunction:
    def the_func(n: GulfOfMexicoNumber) -> GulfOfMexicoNumber:
        nonlocal num
        if not isinstance(n, GulfOfMexicoNumber):
            raise NonFormattedError(f"Expected a number in the ones digit. Instead received a " f"{type(n).__name__}")
        return GulfOfMexicoNumber(num + n.value)

    return BuiltinFunction(1, the_func)


def __number_function_maker_mult(multiplier: int) -> BuiltinFunction:
    def the_func(n: GulfOfMexicoNumber) -> GulfOfMexicoNumber:
        if not isinstance(n, GulfOfMexicoNumber):
            raise NonFormattedError(f"Expected a number. Instead received a {type(n).__name__}")
        return GulfOfMexicoNumber(n.value * multiplier)

    return BuiltinFunction(1, the_func)


# Date.now() support
class DateObject:
    """Provides Date.now() functionality per spec."""
    _time_offset: float = 0.0

    @classmethod
    def now(cls) -> GulfOfMexicoNumber:
        return GulfOfMexicoNumber(int(time.time() * 1000) + int(cls._time_offset))

    @classmethod
    def set_offset(cls, offset: float) -> None:
        cls._time_offset = offset


def db_date_now() -> GulfOfMexicoNumber:
    return DateObject.now()


# Create a Date object with now() method
_date_obj = GulfOfMexicoObject("Date", {})
_date_obj.namespace["now"] = Name("now", BuiltinFunction(0, db_date_now))


# ---------------------------------------------------------------------------
# Math function helpers
# ---------------------------------------------------------------------------

def _math_unary(n: GulfOfMexicoValue, fn: Callable) -> GulfOfMexicoNumber:
    if not isinstance(n, GulfOfMexicoNumber):
        raise NonFormattedError(f"Expected a number, got {type(n).__name__}")
    return GulfOfMexicoNumber(fn(n.value))


def _math_binary(a: GulfOfMexicoValue, b: GulfOfMexicoValue, fn: Callable) -> GulfOfMexicoNumber:
    if not isinstance(a, GulfOfMexicoNumber) or not isinstance(b, GulfOfMexicoNumber):
        raise NonFormattedError("Expected numbers for math function")
    return GulfOfMexicoNumber(fn(a.value, b.value))


BUILTIN_FUNCTION_KEYWORDS = {
    "new": Name("new", BuiltinFunction(-1, db_new)),  # Variadic - accepts class + optional init args
    "current": Name("current", BuiltinFunction(1, db_identity)),
    "Map": Name("Map", BuiltinFunction(0, db_map)),
    "Boolean": Name("Boolean", BuiltinFunction(1, db_to_boolean)),
    "String": Name("String", BuiltinFunction(1, db_to_string)),
    "print": Name("print", BuiltinFunction(-1, db_print)),
    "exit": Name("exit", BuiltinFunction(0, db_exit)),
    "Number": Name("Number", BuiltinFunction(1, db_to_number)),
    "use": Name("use", BuiltinFunction(1, db_signal)),
    "sleep": Name("sleep", BuiltinFunction(1, db_sleep)),
    "read": Name("read", BuiltinFunction(-1, db_read)),
    "readfile": Name("readfile", BuiltinFunction(1, db_readfile)),
    "write": Name("write", BuiltinFunction(-1, db_write)),
    "regex_match": Name("regex_match", BuiltinFunction(1, db_regex_match)),
    "regex_findall": Name("regex_findall", BuiltinFunction(1, db_regex_findall)),
    "regex_replace": Name("regex_replace", BuiltinFunction(1, db_regex_replace)),
    # Math functions per spec
    "abs": Name("abs", BuiltinFunction(1, lambda n: _math_unary(n, abs))),
    "floor": Name("floor", BuiltinFunction(1, lambda n: _math_unary(n, _math.floor))),
    "ceil": Name("ceil", BuiltinFunction(1, lambda n: _math_unary(n, _math.ceil))),
    "round": Name("round", BuiltinFunction(1, lambda n: _math_unary(n, round))),
    "sqrt": Name("sqrt", BuiltinFunction(1, lambda n: _math_unary(n, _math.sqrt))),
    "sin": Name("sin", BuiltinFunction(1, lambda n: _math_unary(n, _math.sin))),
    "cos": Name("cos", BuiltinFunction(1, lambda n: _math_unary(n, _math.cos))),
    "tan": Name("tan", BuiltinFunction(1, lambda n: _math_unary(n, _math.tan))),
    "log": Name("log", BuiltinFunction(1, lambda n: _math_unary(n, _math.log))),
    "exp": Name("exp", BuiltinFunction(1, lambda n: _math_unary(n, _math.exp))),
    "degrees": Name("degrees", BuiltinFunction(1, lambda n: _math_unary(n, _math.degrees))),
    "radians": Name("radians", BuiltinFunction(1, lambda n: _math_unary(n, _math.radians))),
    "pow": Name("pow", BuiltinFunction(2, lambda a, b: _math_binary(a, b, lambda x, y: x ** y))),
    "min": Name("min", BuiltinFunction(2, lambda a, b: _math_binary(a, b, min))),
    "max": Name("max", BuiltinFunction(2, lambda a, b: _math_binary(a, b, max))),
    "random": Name("random", BuiltinFunction(0, lambda: GulfOfMexicoNumber(_random.random()))),
    "randomInt": Name(
        "randomInt",
        BuiltinFunction(2, lambda a, b: _math_binary(
            a, b, lambda x, y: _random.randint(int(x), int(y))
        )),
    ),
}
BUILTIN_VALUE_KEYWORDS = {
    "true": Name("true", GulfOfMexicoBoolean(True)),
    "maybe": Name("maybe", GulfOfMexicoBoolean(None)),
    "false": Name("false", GulfOfMexicoBoolean(False)),
    "undefined": Name("undefined", GulfOfMexicoUndefined()),
    "": Name("", GulfOfMexicoSpecialBlankValue()),
    "Date": Name("Date", _date_obj),
    "noop": Name("noop", GulfOfMexicoString("noop")),  # per spec: noop is just a string taking up a line
}
NUMBER_NAME_KEYWORDS = {
    name: Name(name, GulfOfMexicoNumber(num))
    for num, name in enumerate(
        [
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
        ]
    )
} | {
    name: Name(name, __number_function_maker(num))
    for num, name in zip(
        range(20, 100, 10),
        ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"],
    )
} | {
    # Multiplier names as functions: hundred(5) = 500, thousand(2) = 2000
    "hundred": Name("hundred", __number_function_maker_mult(100)),
    "thousand": Name("thousand", __number_function_maker_mult(1000)),
    "million": Name("million", __number_function_maker_mult(1000000)),
    # Fraction names per spec ("Gulf of Mexico proudly supports fractions!")
    "half": Name("half", GulfOfMexicoNumber(0.5)),
    "third": Name("third", GulfOfMexicoNumber(1 / 3)),
    "quarter": Name("quarter", GulfOfMexicoNumber(0.25)),
}  # this is so cursed

KEYWORDS |= BUILTIN_FUNCTION_KEYWORDS | BUILTIN_VALUE_KEYWORDS | NUMBER_NAME_KEYWORDS
