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
    - Graphics: Canvas(), Color() for drawing
    - Math functions: All from Python's math module
    - Regex: regex_match(), regex_findall(), regex_replace()
    - Word numbers: one, two, twenty, thirty, etc.
"""

from __future__ import annotations
import functools
import time
from time import sleep

import math
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union
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

# Global storage for quantum and time travel features
QUANTUM_STATES: dict[str, list] = {}
TIME_TRAVEL_HISTORY: dict[str, list] = {}
GASLIGHTING_VARS: dict[str, Any] = {}


def is_int(x: Union[float, int]) -> bool:
    return min(x % 1, 1 - x % 1) < FLOAT_TO_INT_PREC


def db_not(x: GulfOfMexicoBoolean) -> GulfOfMexicoBoolean:
    if x.value is None:
        return GulfOfMexicoBoolean(None)
    return GulfOfMexicoBoolean(not x.value)


def db_list_push(self: GulfOfMexicoList, val: GulfOfMexicoValue) -> None:
    self.indexer[max(self.indexer.keys()) + 1] = len(self.values) - 1
    self.values.append(val)
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
    elif not -1 <= index.value <= len(self.values) - 1:
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
    self.value = self.value[:index_val] + self.value[index_val + 1 :]
    return GulfOfMexicoString(retval)


# class Value(metaclass=ABCMeta):   # TODO POTENTIALLY DO THIS TO ALLOW FOR MORE OBJECTS WITHOUT MUCH HASSLE
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
    indexer: dict[float, int] = field(
        init=False
    )  # used for converting the user decimal indecies to the real indecies
    namespace: dict[str, Union[Name, Variable]] = field(default_factory=dict)

    def __post_init__(self):
        self.create_namespace(False)
        self.indexer = dict()
        for index in range(-1, len(self.values) - 1):
            self.indexer[index] = index

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
        if not -1 <= index.value <= len(self.values) - 1:
            raise NonFormattedError("Indexing out of list bounds.")
        elif index.value not in self.indexer:
            raise NonFormattedError(
                "No value assigned to that index"
            )  # if inbounds index doesnt have assigned val
        user_index = index.value
        # print("user index:" + str(user_index))
        realIndex = self.indexer.get(user_index)
        # print("real index:" + str(realIndex))
        return self.values[round(realIndex)]

    def assign_index(self, index: GulfOfMexicoValue, val: GulfOfMexicoValue) -> None:
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a list with a non-number value.")
        if index.value in self.indexer:
            if not -1 <= index.value <= len(self.values) - 1:
                raise NonFormattedError("Indexing out of list bounds.")
            self.values[round(index.value)] = val
            self.indexer[round(index.value)] = round(index.value)
        else:  # assign in the middle of the array
            if not -1 <= index.value <= len(self.values) - 1:
                raise NonFormattedError("Indexing out of list bounds.")
            nearest_int_down = round(max((index.value + 2) // 1, 0))
            self.values[nearest_int_down:nearest_int_down] = [val]
            self.indexer[index.value] = (
                nearest_int_down - 1
            )  # if adding to end, user index is real index
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
        elif not -1 <= index.value <= len(self_val_str) - 1:
            raise NonFormattedError("Indexing out of number bounds.")
        return GulfOfMexicoNumber(int(self_val_str[round(index.value) + 1]))

    def assign_index(self, index: GulfOfMexicoValue, val: GulfOfMexicoValue) -> None:
        self_val_str = self._get_self_str()
        sign = self.value / abs(self.value)
        if not is_int(self.value):
            raise NonFormattedError("Cannot assign into a non-interger number.")
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a number with a non-number value.")
        if (
            not isinstance(val, GulfOfMexicoNumber)
            or not is_int(val.value)
            or not 0 <= val.value <= 9
        ):
            raise NonFormattedError(
                "Cannot assign into a number with a non-integer value."
            )
        if is_int(index.value):
            if not -1 <= index.value <= len(self_val_str) - 1:
                raise NonFormattedError("Indexing out of number bounds.")
            index_num = round(index.value) + 1
            self.value = sign * int(
                self_val_str[:index_num]
                + str(round(val.value))
                + self_val_str[index_num + 1 :]
            )
        else:  # assign in the middle of the array
            index_num = round(max((index.value + 2) // 1, 0))
            self.value = sign * int(
                self_val_str[:index_num]
                + str(round(val.value))
                + self_val_str[index_num:]
            )


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
    namespace: dict[str, Union[Name, Variable]] = field(
        default_factory=dict, hash=False
    )

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
            self.namespace["length"] = Name(
                "length", GulfOfMexicoNumber(len(self.value))
            )

    def access_index(self, index: GulfOfMexicoValue) -> GulfOfMexicoValue:
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a string with a non-number value.")
        # if not is_int(index.value):
        #    raise NonFormattedError("Expected integer for string indexing.")
        if not -1 <= index.value <= len(self.value) - 1:
            raise NonFormattedError("Indexing out of string bounds.")
        elif index.value not in self.indexer:
            raise NonFormattedError(
                "No value assigned to that index"
            )  # if inbounds index doesnt have assigned val
        user_index = index.value
        index_data = self.indexer[user_index]
        real_index = index_data[0]
        extra_characters = index_data[1]
        return self.value[real_index + 1] + extra_characters

    def assign_index(self, index: GulfOfMexicoValue, val: GulfOfMexicoValue) -> None:
        if not isinstance(index, GulfOfMexicoNumber):
            raise NonFormattedError("Cannot index a string with a non-number value.")
        val_str = db_to_string(val).value
        if index.value in self.indexer:
            # # add, when modifying, reduce user indexes by the length of the replaced index's extra characters
            indexer_data = self.indexer[index.value]
            index_num = indexer_data[0] + 1
            excess_length = len(indexer_data[1])
            self.value = (
                self.value[:index_num]
                + val_str
                + self.value[index_num + excess_length + 1 :]
            )
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
            if not -1 <= index.value <= len(self.value) - 1:
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
    creation_time: float = field(default_factory=lambda: time.time())
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
        for i in range(len(self.lifetimes) + 1):
            if i == len(self.lifetimes) or self.lifetimes[i].confidence >= confidence:
                if i == 0 and self.lifetimes:
                    self.prev_values.append(self.value)
                self.lifetimes[i:i] = [
                    VariableLifetime(
                        value,
                        duration,
                        confidence,
                        can_be_reset,
                        can_edit_value,
                        is_temporal=is_temporal,
                        temporal_duration=temporal_duration,
                    )
                ]
                break

    def clear_outdated_lifetimes(self) -> None:
        remove_indeces = []
        current_time = time.time()
        for i, l in enumerate(self.lifetimes):
            if l.lines_left == 0 or (
                l.is_temporal and current_time - l.creation_time >= l.temporal_duration
            ):
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
    for f in range(2):
        for u in range(2):
            for n in range(2):
                for c in range(2):
                    for t in range(2):
                        for i in range(2):
                            for o in range(2):
                                for n_ in range(2):
                                    keywords.add(
                                        "".join(
                                            [
                                                c * i
                                                for c, i in zip(
                                                    "function",
                                                    [f, u, n, c, t, i, o, n_],
                                                )
                                            ]
                                        )
                                        or "fn"
                                    )  # the `or` allows the empty string to not count
    return list(keywords)


FUNCTION_KEYWORDS = all_function_keywords()
KEYWORDS = {
    kw: Name(kw, GulfOfMexicoKeyword(kw))
    for kw in [
        "class",
        "className",
        "after",
        "const",
        "var",
        "when",
        "if",
        "async",
        "return",
        "delete",
        "await",
        "previous",
        "next",
        "reverse",
        "export",
        "import",
        "try",
        "whatever",
        "later",
        "eventually",
        "whenever",
        "synergize",
        "leverage",
        "paradigm_shift",
        "circle_back",
        "touch_base",
        "happy",
        "sad",
        "angry",
        "excited",
        "tired",
        "lucky",
        "unlucky",
        "cross_fingers",
        "knock_on_wood",
        "quantum",
        "definitely_not",
        "blockchain",
        "immutable_ledger",
        "smart_contract",
        "mine",
        "deep_learning",
        "neural_network",
        "ai_powered",
        "sprint",
        "standup",
        "retro",
        "burndown",
        "encrypt",
        "two_factor",
        "penetration_test",
        "zero_trust",
        "containerize",
        "orchestrate",
        "microservice",
        "kubernetes",
        "pivot",
        "disrupt",
        "unicorn",
        "hockey_stick",
    ]
    + FUNCTION_KEYWORDS
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
            return_bool = bool(val.value.strip()) or (None if len(val.value) else False)
        case (
            GulfOfMexicoNumber()
        ):  # maybe if it is 0.xxx, false if it is 0, true if anything else
            return_bool = bool(round(val.value)) or (
                None if abs(val.value) > FLOAT_TO_INT_PREC else False
            )
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
            return_string = (
                f"[{', '.join([db_to_string(v).value for v in val.values])}]"
            )
        case GulfOfMexicoBoolean():
            return_string = (
                "true" if val.value else "maybe" if val.value is None else "false"
            )
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


def db_print(*vals: GulfOfMexicoValue) -> None:
    import sys
    import os

    output = " ".join([db_to_string(v).value for v in vals])
    print(output)
    sys.stdout.flush()


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
    import sys
    import os

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
    import os

    if not _DEBUG_LOGS:
        return

    # If the user explicitly asked for debug, we may have already written lines.
    # Still write any buffered messages to stderr for completeness.
    for entry in _DEBUG_LOGS:
        sys.stderr.write(entry + "\n")
    sys.stderr.flush()
    _DEBUG_LOGS.clear()


def db_to_number(val: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    return_number = 0
    match val:
        case GulfOfMexicoNumber():
            return_number = val.value
        case GulfOfMexicoString():
            return_number = float(val.value)
        case GulfOfMexicoUndefined():
            return_number = 0
        case GulfOfMexicoBoolean():
            return_number = (
                int(val.value is not None and val.value) + (val.value is None) * 0.5
            )
        case GulfOfMexicoList():
            if val.values:
                raise NonFormattedError("Cannot turn a non-empty list into a number.")
            return_number = 0
        case GulfOfMexicoMap():
            if val.self_dict:
                raise NonFormattedError("Cannot turn a non-empty map into a number.")
            return_number = 0
        case _:
            raise NonFormattedError(
                f"Cannot turn type {type(val).__name__} into a number."
            )
    return GulfOfMexicoNumber(return_number)


def db_signal(starting_value: GulfOfMexicoValue) -> GulfOfMexicoValue:
    obj = Name("", starting_value)

    def signal_func(setter_val: GulfOfMexicoValue) -> Optional[GulfOfMexicoValue]:
        nonlocal obj
        if isinstance(setter_val, GulfOfMexicoSpecialBlankValue):
            return obj.value
        obj.value = setter_val

    return BuiltinFunction(1, signal_func)


def db_sleep(t: GulfOfMexicoValue) -> None:
    if not isinstance(t, GulfOfMexicoNumber):
        raise NonFormattedError("'sleep' function requires numerical input.")
    sleep(t.value)


def db_read(path: GulfOfMexicoValue) -> GulfOfMexicoString:
    if not isinstance(path, GulfOfMexicoString):
        raise NonFormattedError("'read' function requires argument to be a string")
    with open(path.value) as f:
        s = f.read()
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
        raise NonFormattedError(f"Invalid regex pattern: {e}")


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
        raise NonFormattedError(f"Invalid regex pattern: {e}")


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
        raise NonFormattedError(f"Invalid regex pattern: {e}")


def db_write(path: GulfOfMexicoValue, content: GulfOfMexicoValue) -> None:
    if not isinstance(path, GulfOfMexicoString):
        raise NonFormattedError("'write' requires path to be a string")
    content_str = db_to_string(content).value
    with open(path.value, "w") as f:
        f.write(content_str)


def db_exit() -> None:
    exit()


def __math_function_decorator(func: Callable):
    @functools.wraps(func)
    def inner(*args) -> GulfOfMexicoNumber:  # no kwargs
        for arg in args:
            if not isinstance(arg, GulfOfMexicoNumber):
                raise NonFormattedError(
                    "Cannot pass in a non-number value into a math function."
                )
        return GulfOfMexicoNumber(func(*[arg.value for arg in args]))

    return inner


def __number_function_maker(num: int) -> BuiltinFunction:
    def the_func(n: GulfOfMexicoNumber) -> GulfOfMexicoNumber:
        nonlocal num
        if not isinstance(n, GulfOfMexicoNumber):
            raise NonFormattedError(
                f"Expected a number in the ones digit. Instead received a "
                f"{type(n).__name__}"
            )
        return GulfOfMexicoNumber(num + n.value)

    return BuiltinFunction(1, the_func)


# Graphics functions
def db_create_canvas(
    width: GulfOfMexicoValue,
    height: GulfOfMexicoValue,
    bg_color: Optional[GulfOfMexicoValue] = None,
) -> GulfOfMexicoValue:
    """Create a new Canvas for drawing."""
    if not isinstance(width, GulfOfMexicoNumber) or not isinstance(
        height, GulfOfMexicoNumber
    ):
        raise NonFormattedError("Canvas width and height must be numbers")

    try:
        from gulfofmexico.graphics import GulfOfMexicoCanvas, GulfOfMexicoColor
    except ImportError:
        raise NonFormattedError(
            "Graphics module not available. Install Pillow:\n" "  pip install Pillow"
        )

    # Parse background color if provided
    background = GulfOfMexicoColor(255, 255, 255)  # default white
    if bg_color and not isinstance(bg_color, GulfOfMexicoSpecialBlankValue):
        if isinstance(bg_color, GulfOfMexicoString):
            from gulfofmexico.graphics import parse_color

            background = parse_color(bg_color.value)

    canvas = GulfOfMexicoCanvas(int(width.value), int(height.value), background)

    # Create canvas object with methods as namespace
    canvas_obj = GulfOfMexicoObject("Canvas", {})
    canvas_obj._gom_canvas = canvas  # Store the actual canvas

    # Add canvas methods to namespace
    canvas_obj.namespace.update(
        {
            "width": Name("width", GulfOfMexicoNumber(canvas.width)),
            "height": Name("height", GulfOfMexicoNumber(canvas.height)),
            "clear": Name(
                "clear", BuiltinFunction(1, lambda c: _canvas_clear(canvas_obj, c))
            ),
            "pixel": Name(
                "pixel",
                BuiltinFunction(3, lambda x, y, c: _canvas_pixel(canvas_obj, x, y, c)),
            ),
            "rect": Name(
                "rect",
                BuiltinFunction(-1, lambda *args: _canvas_rect(canvas_obj, *args)),
            ),
            "circle": Name(
                "circle",
                BuiltinFunction(-1, lambda *args: _canvas_circle(canvas_obj, *args)),
            ),
            "line": Name(
                "line",
                BuiltinFunction(5, lambda *args: _canvas_line(canvas_obj, *args)),
            ),
            "polygon": Name(
                "polygon",
                BuiltinFunction(2, lambda pts, c: _canvas_polygon(canvas_obj, pts, c)),
            ),
            "text": Name(
                "text",
                BuiltinFunction(-1, lambda *args: _canvas_text(canvas_obj, *args)),
            ),
            "save": Name(
                "save", BuiltinFunction(1, lambda path: _canvas_save(canvas_obj, path))
            ),
            "show": Name("show", BuiltinFunction(0, lambda: _canvas_show(canvas_obj))),
            "translate": Name(
                "translate",
                BuiltinFunction(2, lambda x, y: _canvas_translate(canvas_obj, x, y)),
            ),
            "rotate": Name(
                "rotate", BuiltinFunction(1, lambda a: _canvas_rotate(canvas_obj, a))
            ),
            "scale": Name(
                "scale",
                BuiltinFunction(-1, lambda *args: _canvas_scale(canvas_obj, *args)),
            ),
            "saveTransform": Name(
                "saveTransform",
                BuiltinFunction(0, lambda: _canvas_save_transform(canvas_obj)),
            ),
            "restoreTransform": Name(
                "restoreTransform",
                BuiltinFunction(0, lambda: _canvas_restore_transform(canvas_obj)),
            ),
        }
    )

    return canvas_obj


def db_create_color(*args: GulfOfMexicoValue) -> GulfOfMexicoValue:
    """Create a Color object from RGB or RGBA values."""
    try:
        from gulfofmexico.graphics import GulfOfMexicoColor, parse_color
    except ImportError:
        raise NonFormattedError("Graphics module not available")

    # Handle named colors
    if len(args) == 1 and isinstance(args[0], GulfOfMexicoString):
        color = parse_color(args[0].value)
    # RGB
    elif len(args) == 3:
        r = args[0].value if isinstance(args[0], GulfOfMexicoNumber) else None
        g = args[1].value if isinstance(args[1], GulfOfMexicoNumber) else None
        b = args[2].value if isinstance(args[2], GulfOfMexicoNumber) else None
        color = GulfOfMexicoColor(r, g, b)
    # RGBA
    elif len(args) == 4:
        r = args[0].value if isinstance(args[0], GulfOfMexicoNumber) else None
        g = args[1].value if isinstance(args[1], GulfOfMexicoNumber) else None
        b = args[2].value if isinstance(args[2], GulfOfMexicoNumber) else None
        a = args[3].value if isinstance(args[3], GulfOfMexicoNumber) else None
        color = GulfOfMexicoColor(r, g, b, a)
    else:
        raise NonFormattedError(
            "Color requires 1 (name), 3 (RGB) or 4 (RGBA) arguments"
        )

    # Return as a GulfOfMexico object
    color_obj = GulfOfMexicoObject("Color", {})
    color_obj._gom_color = color
    color_obj.namespace.update(
        {
            "r": Name("r", GulfOfMexicoNumber(color.r if color.r is not None else 127)),
            "g": Name("g", GulfOfMexicoNumber(color.g if color.g is not None else 127)),
            "b": Name("b", GulfOfMexicoNumber(color.b if color.b is not None else 127)),
            "a": Name("a", GulfOfMexicoNumber(color.a if color.a is not None else 127)),
            "hex": Name(
                "hex", BuiltinFunction(0, lambda: GulfOfMexicoString(color.to_hex()))
            ),
        }
    )
    return color_obj


# Canvas method wrappers
def _get_canvas(canvas_obj: GulfOfMexicoObject):
    """Extract the underlying canvas from a canvas object."""
    if not hasattr(canvas_obj, "_gom_canvas"):
        raise NonFormattedError("Not a valid Canvas object")
    return canvas_obj._gom_canvas


def _parse_color_arg(color_arg: GulfOfMexicoValue) -> str:
    """Convert a GulfOfMexico value to a color specification."""
    from gulfofmexico.graphics import GulfOfMexicoColor

    if isinstance(color_arg, GulfOfMexicoString):
        return color_arg.value
    elif isinstance(color_arg, GulfOfMexicoObject) and hasattr(color_arg, "_gom_color"):
        return color_arg._gom_color
    elif isinstance(color_arg, GulfOfMexicoBoolean):
        # Three-valued logic for colors!
        if color_arg.value is True:
            return "white"
        elif color_arg.value is False:
            return "black"
        else:  # maybe
            return "maybe"
    return "black"


def _canvas_clear(canvas_obj, color_arg):
    canvas = _get_canvas(canvas_obj)
    if isinstance(color_arg, GulfOfMexicoSpecialBlankValue):
        canvas.clear()
    else:
        color = _parse_color_arg(color_arg)
        canvas.clear(color)


def _canvas_pixel(canvas_obj, x, y, color_arg):
    canvas = _get_canvas(canvas_obj)
    if not isinstance(x, GulfOfMexicoNumber) or not isinstance(y, GulfOfMexicoNumber):
        raise NonFormattedError("pixel coordinates must be numbers")
    color = _parse_color_arg(color_arg)
    canvas.pixel(x.value, y.value, color)


def _canvas_rect(canvas_obj, *args):
    canvas = _get_canvas(canvas_obj)
    if len(args) < 5:
        raise NonFormattedError("rect requires x, y, width, height, color")
    x, y, w, h = args[0].value, args[1].value, args[2].value, args[3].value
    color = _parse_color_arg(args[4])
    fill = True
    if len(args) > 5 and isinstance(args[5], GulfOfMexicoBoolean):
        fill = args[5].value if args[5].value is not None else True
    canvas.rect(x, y, w, h, color, fill)


def _canvas_circle(canvas_obj, *args):
    canvas = _get_canvas(canvas_obj)
    if len(args) < 4:
        raise NonFormattedError("circle requires x, y, radius, color")
    x, y, r = args[0].value, args[1].value, args[2].value
    color = _parse_color_arg(args[3])
    fill = True
    if len(args) > 4 and isinstance(args[4], GulfOfMexicoBoolean):
        fill = args[4].value if args[4].value is not None else True
    canvas.circle(x, y, r, color, fill)


def _canvas_line(canvas_obj, x1, y1, x2, y2, color_arg):
    canvas = _get_canvas(canvas_obj)
    if not all(isinstance(v, GulfOfMexicoNumber) for v in [x1, y1, x2, y2]):
        raise NonFormattedError("line coordinates must be numbers")
    color = _parse_color_arg(color_arg)
    canvas.line(x1.value, y1.value, x2.value, y2.value, color)


def _canvas_polygon(canvas_obj, points_list, color_arg):
    canvas = _get_canvas(canvas_obj)
    if not isinstance(points_list, GulfOfMexicoList):
        raise NonFormattedError("polygon points must be a list")

    points = []
    for point in points_list.values:
        if isinstance(point, GulfOfMexicoList) and len(point.values) >= 2:
            x = (
                point.values[0].value
                if isinstance(point.values[0], GulfOfMexicoNumber)
                else 0
            )
            y = (
                point.values[1].value
                if isinstance(point.values[1], GulfOfMexicoNumber)
                else 0
            )
            points.append((x, y))

    color = _parse_color_arg(color_arg)
    canvas.polygon(points, color)


def _canvas_text(canvas_obj, *args):
    canvas = _get_canvas(canvas_obj)
    if len(args) < 4:
        raise NonFormattedError("text requires text, x, y, color")
    text = db_to_string(args[0]).value
    x, y = args[1].value, args[2].value
    color = _parse_color_arg(args[3])
    size = 16
    if len(args) > 4 and isinstance(args[4], GulfOfMexicoNumber):
        size = int(args[4].value)
    canvas.text(text, x, y, color, size)


def _canvas_save(canvas_obj, path_arg):
    canvas = _get_canvas(canvas_obj)
    if not isinstance(path_arg, GulfOfMexicoString):
        raise NonFormattedError("save path must be a string")
    canvas.save(path_arg.value)


def _canvas_show(canvas_obj):
    canvas = _get_canvas(canvas_obj)
    canvas.show()


def _canvas_translate(canvas_obj, x, y):
    canvas = _get_canvas(canvas_obj)
    if not isinstance(x, GulfOfMexicoNumber) or not isinstance(y, GulfOfMexicoNumber):
        raise NonFormattedError("translate requires number arguments")
    canvas.translate(x.value, y.value)


def _canvas_rotate(canvas_obj, angle):
    canvas = _get_canvas(canvas_obj)
    if not isinstance(angle, GulfOfMexicoNumber):
        raise NonFormattedError("rotate requires a number argument")
    canvas.rotate(angle.value)


def _canvas_scale(canvas_obj, *args):
    canvas = _get_canvas(canvas_obj)
    if len(args) < 1:
        raise NonFormattedError("scale requires at least one argument")
    sx = args[0].value if isinstance(args[0], GulfOfMexicoNumber) else 1
    sy = (
        args[1].value
        if len(args) > 1 and isinstance(args[1], GulfOfMexicoNumber)
        else sx
    )
    canvas.scale(sx, sy)


def _canvas_save_transform(canvas_obj):
    canvas = _get_canvas(canvas_obj)
    canvas.save_transform()


def _canvas_restore_transform(canvas_obj):
    canvas = _get_canvas(canvas_obj)
    canvas.restore_transform()


def db_observe(var_name: GulfOfMexicoString) -> GulfOfMexicoValue:
    """Collapse quantum superposition to a single value."""
    if not isinstance(var_name, GulfOfMexicoString):
        raise NonFormattedError("observe requires a string variable name")

    import random

    name = var_name.value
    if name in QUANTUM_STATES:
        superposition = QUANTUM_STATES[name]
        if superposition:
            collapsed_value = random.choice(superposition)
            print(f"⚛️  [OBSERVE] Wavefunction collapsed! '{name}' = {collapsed_value}")
            # Remove from superposition after observation
            del QUANTUM_STATES[name]
            return collapsed_value

    raise NonFormattedError(f"Variable '{var_name.value}' not in quantum state")


def db_past(
    var_name: GulfOfMexicoString, steps: GulfOfMexicoNumber
) -> GulfOfMexicoValue:
    """Access past value of a variable."""
    if not isinstance(var_name, GulfOfMexicoString):
        raise NonFormattedError("past requires a string variable name")
    if not isinstance(steps, GulfOfMexicoNumber):
        raise NonFormattedError("past requires number of steps back")

    name = var_name.value
    n = int(steps.value)

    if name in TIME_TRAVEL_HISTORY:
        history = TIME_TRAVEL_HISTORY[name]
        if len(history) > n:
            past_value = history[-(n + 1)]
            print(f"⏰ [TIME TRAVEL] Retrieved '{name}' from {n} steps ago")
            return past_value

    print(f"⏰ [TIME TRAVEL] No history for '{name}' at -{n} steps, returning 0")
    return GulfOfMexicoNumber(0)


def db_future(var_name: GulfOfMexicoString) -> GulfOfMexicoValue:
    """Predict future value of a variable (spoiler: it's random)."""
    if not isinstance(var_name, GulfOfMexicoString):
        raise NonFormattedError("future requires a string variable name")

    import random

    # Future is unknowable, so we return a random prediction
    prediction = GulfOfMexicoNumber(random.randint(0, 100))
    print(
        f"🔮 [FUTURE] Predicting '{var_name.value}' will be {prediction.value} (maybe)"
    )
    return prediction


# ===== Base/Radix Number System Functions =====


def db_to_base(
    number: GulfOfMexicoValue, base: GulfOfMexicoValue
) -> GulfOfMexicoString:
    """Convert a number to a string representation in the specified base (2-36)."""
    if not isinstance(number, GulfOfMexicoNumber):
        raise NonFormattedError("to_base requires a number as first argument")
    if not isinstance(base, GulfOfMexicoNumber):
        raise NonFormattedError("to_base requires a number as second argument (base)")

    num = int(number.value)
    radix = int(base.value)

    if radix < 2 or radix > 36:
        raise NonFormattedError("Base must be between 2 and 36")

    if num == 0:
        return GulfOfMexicoString("0")

    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = []
    negative = num < 0
    num = abs(num)

    while num > 0:
        result.append(digits[num % radix])
        num //= radix

    if negative:
        result.append("-")

    return GulfOfMexicoString("".join(reversed(result)))


def db_from_base(
    number_str: GulfOfMexicoValue, base: GulfOfMexicoValue
) -> GulfOfMexicoNumber:
    """Convert a string representation in the specified base to a decimal number."""
    if not isinstance(number_str, GulfOfMexicoString):
        raise NonFormattedError("from_base requires a string as first argument")
    if not isinstance(base, GulfOfMexicoNumber):
        raise NonFormattedError("from_base requires a number as second argument (base)")

    num_str = number_str.value.strip().upper()
    radix = int(base.value)

    if radix < 2 or radix > 36:
        raise NonFormattedError("Base must be between 2 and 36")

    try:
        result = int(num_str, radix)
        return GulfOfMexicoNumber(result)
    except ValueError:
        raise NonFormattedError(f"Invalid number '{num_str}' for base {radix}")


def db_base_add(
    num1: GulfOfMexicoValue,
    base1: GulfOfMexicoValue,
    num2: GulfOfMexicoValue,
    base2: GulfOfMexicoValue,
    result_base: GulfOfMexicoValue,
) -> GulfOfMexicoString:
    """Add two numbers in potentially different bases and return result in specified base."""
    if not isinstance(num1, (GulfOfMexicoString, GulfOfMexicoNumber)):
        raise NonFormattedError("base_add requires number or string as first argument")
    if not isinstance(base1, GulfOfMexicoNumber):
        raise NonFormattedError("base_add requires base1 (number)")
    if not isinstance(num2, (GulfOfMexicoString, GulfOfMexicoNumber)):
        raise NonFormattedError("base_add requires number or string as third argument")
    if not isinstance(base2, GulfOfMexicoNumber):
        raise NonFormattedError("base_add requires base2 (number)")
    if not isinstance(result_base, GulfOfMexicoNumber):
        raise NonFormattedError("base_add requires result_base (number)")

    # Convert both to decimal
    if isinstance(num1, GulfOfMexicoString):
        val1 = db_from_base(num1, base1).value
    else:
        val1 = num1.value

    if isinstance(num2, GulfOfMexicoString):
        val2 = db_from_base(num2, base2).value
    else:
        val2 = num2.value

    # Add in decimal
    result = val1 + val2

    # Convert to result base
    return db_to_base(GulfOfMexicoNumber(result), result_base)


def db_base_sub(
    num1: GulfOfMexicoValue,
    base1: GulfOfMexicoValue,
    num2: GulfOfMexicoValue,
    base2: GulfOfMexicoValue,
    result_base: GulfOfMexicoValue,
) -> GulfOfMexicoString:
    """Subtract two numbers in potentially different bases and return result in specified base."""
    if not isinstance(num1, (GulfOfMexicoString, GulfOfMexicoNumber)):
        raise NonFormattedError("base_sub requires number or string as first argument")
    if not isinstance(base1, GulfOfMexicoNumber):
        raise NonFormattedError("base_sub requires base1 (number)")
    if not isinstance(num2, (GulfOfMexicoString, GulfOfMexicoNumber)):
        raise NonFormattedError("base_sub requires number or string as third argument")
    if not isinstance(base2, GulfOfMexicoNumber):
        raise NonFormattedError("base_sub requires base2 (number)")
    if not isinstance(result_base, GulfOfMexicoNumber):
        raise NonFormattedError("base_sub requires result_base (number)")

    # Convert both to decimal
    if isinstance(num1, GulfOfMexicoString):
        val1 = db_from_base(num1, base1).value
    else:
        val1 = num1.value

    if isinstance(num2, GulfOfMexicoString):
        val2 = db_from_base(num2, base2).value
    else:
        val2 = num2.value

    # Subtract in decimal
    result = val1 - val2

    # Convert to result base
    return db_to_base(GulfOfMexicoNumber(result), result_base)


def db_base_mul(
    num1: GulfOfMexicoValue,
    base1: GulfOfMexicoValue,
    num2: GulfOfMexicoValue,
    base2: GulfOfMexicoValue,
    result_base: GulfOfMexicoValue,
) -> GulfOfMexicoString:
    """Multiply two numbers in potentially different bases and return result in specified base."""
    if not isinstance(num1, (GulfOfMexicoString, GulfOfMexicoNumber)):
        raise NonFormattedError("base_mul requires number or string as first argument")
    if not isinstance(base1, GulfOfMexicoNumber):
        raise NonFormattedError("base_mul requires base1 (number)")
    if not isinstance(num2, (GulfOfMexicoString, GulfOfMexicoNumber)):
        raise NonFormattedError("base_mul requires number or string as third argument")
    if not isinstance(base2, GulfOfMexicoNumber):
        raise NonFormattedError("base_mul requires base2 (number)")
    if not isinstance(result_base, GulfOfMexicoNumber):
        raise NonFormattedError("base_mul requires result_base (number)")

    # Convert both to decimal
    if isinstance(num1, GulfOfMexicoString):
        val1 = db_from_base(num1, base1).value
    else:
        val1 = num1.value

    if isinstance(num2, GulfOfMexicoString):
        val2 = db_from_base(num2, base2).value
    else:
        val2 = num2.value

    # Multiply in decimal
    result = val1 * val2

    # Convert to result base
    return db_to_base(GulfOfMexicoNumber(result), result_base)


def db_base_div(
    num1: GulfOfMexicoValue,
    base1: GulfOfMexicoValue,
    num2: GulfOfMexicoValue,
    base2: GulfOfMexicoValue,
    result_base: GulfOfMexicoValue,
) -> GulfOfMexicoString:
    """Divide two numbers in potentially different bases and return result in specified base."""
    if not isinstance(num1, (GulfOfMexicoString, GulfOfMexicoNumber)):
        raise NonFormattedError("base_div requires number or string as first argument")
    if not isinstance(base1, GulfOfMexicoNumber):
        raise NonFormattedError("base_div requires base1 (number)")
    if not isinstance(num2, (GulfOfMexicoString, GulfOfMexicoNumber)):
        raise NonFormattedError("base_div requires number or string as third argument")
    if not isinstance(base2, GulfOfMexicoNumber):
        raise NonFormattedError("base_div requires base2 (number)")
    if not isinstance(result_base, GulfOfMexicoNumber):
        raise NonFormattedError("base_div requires result_base (number)")

    # Convert both to decimal
    if isinstance(num1, GulfOfMexicoString):
        val1 = db_from_base(num1, base1).value
    else:
        val1 = num1.value

    if isinstance(num2, GulfOfMexicoString):
        val2 = db_from_base(num2, base2).value
    else:
        val2 = num2.value

    if val2 == 0:
        raise NonFormattedError("Division by zero")

    # Integer divide in decimal
    result = int(val1 // val2)

    # Convert to result base
    return db_to_base(GulfOfMexicoNumber(result), result_base)


# Convenience functions for common bases
def db_to_binary(number: GulfOfMexicoValue) -> GulfOfMexicoString:
    """Convert a number to binary (base 2)."""
    return db_to_base(number, GulfOfMexicoNumber(2))


def db_to_octal(number: GulfOfMexicoValue) -> GulfOfMexicoString:
    """Convert a number to octal (base 8)."""
    return db_to_base(number, GulfOfMexicoNumber(8))


def db_to_hex(number: GulfOfMexicoValue) -> GulfOfMexicoString:
    """Convert a number to hexadecimal (base 16)."""
    return db_to_base(number, GulfOfMexicoNumber(16))


def db_from_binary(number_str: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Convert a binary string to decimal."""
    return db_from_base(number_str, GulfOfMexicoNumber(2))


def db_from_octal(number_str: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Convert an octal string to decimal."""
    return db_from_base(number_str, GulfOfMexicoNumber(8))


def db_from_hex(number_str: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Convert a hexadecimal string to decimal."""
    return db_from_base(number_str, GulfOfMexicoNumber(16))


# ===== Statistical Functions =====


def _get_list_values(lst: GulfOfMexicoValue) -> list[float]:
    """Extract numeric values from a GulfOfMexico list."""
    if not isinstance(lst, GulfOfMexicoList):
        raise NonFormattedError("Function requires a list argument")
    return [v.value for v in lst.values if isinstance(v, GulfOfMexicoNumber)]


def db_mean(lst: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Calculate the arithmetic mean (average) of a list of numbers."""
    values = _get_list_values(lst)
    if not values:
        raise NonFormattedError("Cannot calculate mean of empty list")
    return GulfOfMexicoNumber(sum(values) / len(values))


def db_median(lst: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Calculate the median (middle value) of a list of numbers."""
    values = _get_list_values(lst)
    if not values:
        raise NonFormattedError("Cannot calculate median of empty list")
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 0:
        return GulfOfMexicoNumber((sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2)
    else:
        return GulfOfMexicoNumber(sorted_vals[n // 2])


def db_mode(lst: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Calculate the mode (most frequent value) of a list of numbers."""
    values = _get_list_values(lst)
    if not values:
        raise NonFormattedError("Cannot calculate mode of empty list")
    from collections import Counter

    counts = Counter(values)
    mode_val = counts.most_common(1)[0][0]
    return GulfOfMexicoNumber(mode_val)


def db_variance(lst: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Calculate the variance of a list of numbers."""
    values = _get_list_values(lst)
    if not values:
        raise NonFormattedError("Cannot calculate variance of empty list")
    mean_val = sum(values) / len(values)
    variance = sum((x - mean_val) ** 2 for x in values) / len(values)
    return GulfOfMexicoNumber(variance)


def db_stdev(lst: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Calculate the standard deviation of a list of numbers."""
    variance = db_variance(lst).value
    return GulfOfMexicoNumber(variance**0.5)


def db_min_val(lst: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Find the minimum value in a list of numbers."""
    values = _get_list_values(lst)
    if not values:
        raise NonFormattedError("Cannot find min of empty list")
    return GulfOfMexicoNumber(min(values))


def db_max_val(lst: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Find the maximum value in a list of numbers."""
    values = _get_list_values(lst)
    if not values:
        raise NonFormattedError("Cannot find max of empty list")
    return GulfOfMexicoNumber(max(values))


def db_sum_list(lst: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Calculate the sum of all numbers in a list."""
    values = _get_list_values(lst)
    return GulfOfMexicoNumber(sum(values))


def db_percentile(lst: GulfOfMexicoValue, p: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Calculate the p-th percentile of a list (p should be 0-100)."""
    values = _get_list_values(lst)
    if not isinstance(p, GulfOfMexicoNumber):
        raise NonFormattedError("Percentile requires a number for p")
    if not values:
        raise NonFormattedError("Cannot calculate percentile of empty list")

    percentile = p.value
    if percentile < 0 or percentile > 100:
        raise NonFormattedError("Percentile must be between 0 and 100")

    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (percentile / 100)
    f = int(k)
    c = k - f

    if f + 1 < len(sorted_vals):
        result = sorted_vals[f] + c * (sorted_vals[f + 1] - sorted_vals[f])
    else:
        result = sorted_vals[f]

    return GulfOfMexicoNumber(result)


def db_correlation(
    lst1: GulfOfMexicoValue, lst2: GulfOfMexicoValue
) -> GulfOfMexicoNumber:
    """Calculate the Pearson correlation coefficient between two lists."""
    values1 = _get_list_values(lst1)
    values2 = _get_list_values(lst2)

    if len(values1) != len(values2):
        raise NonFormattedError("Lists must have the same length for correlation")
    if not values1:
        raise NonFormattedError("Cannot calculate correlation of empty lists")

    n = len(values1)
    mean1 = sum(values1) / n
    mean2 = sum(values2) / n

    numerator = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(n))
    denominator = (
        sum((x - mean1) ** 2 for x in values1) * sum((y - mean2) ** 2 for y in values2)
    ) ** 0.5

    if denominator == 0:
        return GulfOfMexicoNumber(0)

    return GulfOfMexicoNumber(numerator / denominator)


# ===== Financial Functions =====


def db_compound_interest(
    principal: GulfOfMexicoValue,
    rate: GulfOfMexicoValue,
    time: GulfOfMexicoValue,
    n: GulfOfMexicoValue,
) -> GulfOfMexicoNumber:
    """Calculate compound interest: A = P(1 + r/n)^(nt)."""
    if not all(isinstance(x, GulfOfMexicoNumber) for x in [principal, rate, time, n]):
        raise NonFormattedError("compound_interest requires 4 numbers")

    p = principal.value
    r = rate.value
    t = time.value
    n_val = n.value

    amount = p * ((1 + r / n_val) ** (n_val * t))
    return GulfOfMexicoNumber(amount)


def db_simple_interest(
    principal: GulfOfMexicoValue,
    rate: GulfOfMexicoValue,
    time: GulfOfMexicoValue,
) -> GulfOfMexicoNumber:
    """Calculate simple interest: I = P * r * t."""
    if not all(isinstance(x, GulfOfMexicoNumber) for x in [principal, rate, time]):
        raise NonFormattedError("simple_interest requires 3 numbers")

    p = principal.value
    r = rate.value
    t = time.value

    interest = p * r * t
    return GulfOfMexicoNumber(interest)


def db_pmt(
    rate: GulfOfMexicoValue,
    nper: GulfOfMexicoValue,
    pv: GulfOfMexicoValue,
) -> GulfOfMexicoNumber:
    """Calculate periodic payment for a loan: PMT = (PV * r) / (1 - (1 + r)^-n)."""
    if not all(isinstance(x, GulfOfMexicoNumber) for x in [rate, nper, pv]):
        raise NonFormattedError("pmt requires 3 numbers: rate, nper, pv")

    r = rate.value
    n = nper.value
    pv_val = pv.value

    if r == 0:
        payment = pv_val / n
    else:
        payment = (pv_val * r) / (1 - (1 + r) ** -n)

    return GulfOfMexicoNumber(payment)


def db_fv(
    rate: GulfOfMexicoValue,
    nper: GulfOfMexicoValue,
    pmt: GulfOfMexicoValue,
    pv: GulfOfMexicoValue,
) -> GulfOfMexicoNumber:
    """Calculate future value of an investment."""
    if not all(isinstance(x, GulfOfMexicoNumber) for x in [rate, nper, pmt, pv]):
        raise NonFormattedError("fv requires 4 numbers")

    r = rate.value
    n = nper.value
    pmt_val = pmt.value
    pv_val = pv.value

    if r == 0:
        fv_val = -pv_val - pmt_val * n
    else:
        fv_val = -pv_val * (1 + r) ** n - pmt_val * (((1 + r) ** n - 1) / r)

    return GulfOfMexicoNumber(fv_val)


def db_pv(
    rate: GulfOfMexicoValue,
    nper: GulfOfMexicoValue,
    pmt: GulfOfMexicoValue,
) -> GulfOfMexicoNumber:
    """Calculate present value of an investment."""
    if not all(isinstance(x, GulfOfMexicoNumber) for x in [rate, nper, pmt]):
        raise NonFormattedError("pv requires 3 numbers")

    r = rate.value
    n = nper.value
    pmt_val = pmt.value

    if r == 0:
        pv_val = -pmt_val * n
    else:
        pv_val = -pmt_val * ((1 - (1 + r) ** -n) / r)

    return GulfOfMexicoNumber(pv_val)


def db_npv(rate: GulfOfMexicoValue, cashflows: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Calculate Net Present Value of cash flows."""
    if not isinstance(rate, GulfOfMexicoNumber):
        raise NonFormattedError("npv requires rate as first argument")

    values = _get_list_values(cashflows)
    if not values:
        raise NonFormattedError("npv requires non-empty cashflows list")

    r = rate.value
    npv_val = sum(cf / (1 + r) ** i for i, cf in enumerate(values))

    return GulfOfMexicoNumber(npv_val)


# ===== Business Metrics =====


def db_roi(gain: GulfOfMexicoValue, cost: GulfOfMexicoValue) -> GulfOfMexicoNumber:
    """Calculate Return on Investment: (Gain - Cost) / Cost * 100."""
    if not all(isinstance(x, GulfOfMexicoNumber) for x in [gain, cost]):
        raise NonFormattedError("roi requires 2 numbers")

    g = gain.value
    c = cost.value

    if c == 0:
        raise NonFormattedError("Cost cannot be zero for ROI calculation")

    roi_val = ((g - c) / c) * 100
    return GulfOfMexicoNumber(roi_val)


def db_profit_margin(
    revenue: GulfOfMexicoValue, cost: GulfOfMexicoValue
) -> GulfOfMexicoNumber:
    """Calculate Profit Margin: (Revenue - Cost) / Revenue * 100."""
    if not all(isinstance(x, GulfOfMexicoNumber) for x in [revenue, cost]):
        raise NonFormattedError("profit_margin requires 2 numbers")

    r = revenue.value
    c = cost.value

    if r == 0:
        raise NonFormattedError("Revenue cannot be zero for profit margin")

    margin = ((r - c) / r) * 100
    return GulfOfMexicoNumber(margin)


def db_cagr(
    beginning_value: GulfOfMexicoValue,
    ending_value: GulfOfMexicoValue,
    years: GulfOfMexicoValue,
) -> GulfOfMexicoNumber:
    """Calculate Compound Annual Growth Rate: (Ending/Beginning)^(1/years) - 1."""
    if not all(
        isinstance(x, GulfOfMexicoNumber)
        for x in [beginning_value, ending_value, years]
    ):
        raise NonFormattedError("cagr requires 3 numbers")

    bv = beginning_value.value
    ev = ending_value.value
    y = years.value

    if bv <= 0 or y <= 0:
        raise NonFormattedError("Beginning value and years must be positive")

    cagr_val = ((ev / bv) ** (1 / y) - 1) * 100
    return GulfOfMexicoNumber(cagr_val)


def db_break_even(
    fixed_costs: GulfOfMexicoValue,
    price_per_unit: GulfOfMexicoValue,
    variable_cost_per_unit: GulfOfMexicoValue,
) -> GulfOfMexicoNumber:
    """Calculate break-even point in units."""
    if not all(
        isinstance(x, GulfOfMexicoNumber)
        for x in [fixed_costs, price_per_unit, variable_cost_per_unit]
    ):
        raise NonFormattedError("break_even requires 3 numbers")

    fc = fixed_costs.value
    price = price_per_unit.value
    vc = variable_cost_per_unit.value

    if price <= vc:
        raise NonFormattedError("Price must be greater than variable cost")

    units = fc / (price - vc)
    return GulfOfMexicoNumber(units)


# ===== Scientific/Mathematical Functions =====


def db_linear_regression(
    x_list: GulfOfMexicoValue, y_list: GulfOfMexicoValue
) -> GulfOfMexicoList:
    """Calculate linear regression y = mx + b, returns [slope, intercept]."""
    x_values = _get_list_values(x_list)
    y_values = _get_list_values(y_list)

    if len(x_values) != len(y_values):
        raise NonFormattedError("X and Y lists must have same length")
    if len(x_values) < 2:
        raise NonFormattedError("Need at least 2 data points for regression")

    n = len(x_values)
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n

    numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
    denominator = sum((x - x_mean) ** 2 for x in x_values)

    if denominator == 0:
        raise NonFormattedError("Cannot calculate regression with constant X values")

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    return GulfOfMexicoList([GulfOfMexicoNumber(slope), GulfOfMexicoNumber(intercept)])


def db_predict(
    x: GulfOfMexicoValue, slope: GulfOfMexicoValue, intercept: GulfOfMexicoValue
) -> GulfOfMexicoNumber:
    """Predict y value using linear equation y = mx + b."""
    if not all(isinstance(v, GulfOfMexicoNumber) for v in [x, slope, intercept]):
        raise NonFormattedError("predict requires 3 numbers")

    y = slope.value * x.value + intercept.value
    return GulfOfMexicoNumber(y)


def db_derivative(
    func_values: GulfOfMexicoValue,
    h: GulfOfMexicoValue,
) -> GulfOfMexicoList:
    """Approximate derivative using finite differences."""
    values = _get_list_values(func_values)
    if not isinstance(h, GulfOfMexicoNumber):
        raise NonFormattedError("h (step size) must be a number")
    if len(values) < 2:
        raise NonFormattedError("Need at least 2 values for derivative")

    step = h.value
    derivatives = []

    for i in range(len(values) - 1):
        deriv = (values[i + 1] - values[i]) / step
        derivatives.append(GulfOfMexicoNumber(deriv))

    return GulfOfMexicoList(derivatives)


def db_integrate(
    func_values: GulfOfMexicoValue,
    h: GulfOfMexicoValue,
) -> GulfOfMexicoNumber:
    """Approximate definite integral using trapezoidal rule."""
    values = _get_list_values(func_values)
    if not isinstance(h, GulfOfMexicoNumber):
        raise NonFormattedError("h (step size) must be a number")
    if len(values) < 2:
        raise NonFormattedError("Need at least 2 values for integration")

    step = h.value
    integral = step * (values[0] / 2 + sum(values[1:-1]) + values[-1] / 2)

    return GulfOfMexicoNumber(integral)


def db_quadratic_solve(
    a: GulfOfMexicoValue, b: GulfOfMexicoValue, c: GulfOfMexicoValue
) -> GulfOfMexicoList:
    """Solve quadratic equation ax^2 + bx + c = 0, returns [root1, root2]."""
    if not all(isinstance(v, GulfOfMexicoNumber) for v in [a, b, c]):
        raise NonFormattedError("quadratic_solve requires 3 numbers")

    a_val = a.value
    b_val = b.value
    c_val = c.value

    if a_val == 0:
        raise NonFormattedError("Coefficient 'a' cannot be zero")

    discriminant = b_val**2 - 4 * a_val * c_val

    if discriminant < 0:
        raise NonFormattedError("No real solutions (negative discriminant)")

    root1 = (-b_val + discriminant**0.5) / (2 * a_val)
    root2 = (-b_val - discriminant**0.5) / (2 * a_val)

    return GulfOfMexicoList([GulfOfMexicoNumber(root1), GulfOfMexicoNumber(root2)])


# get ready, this is boutta be crazy
MATH_FUNCTION_KEYWORDS = {
    name: Name(
        name,
        (
            BuiltinFunction(
                (
                    (
                        -1
                        if any(
                            [
                                arg[0] == "*" and len(arg) > 1
                                for arg in (
                                    v.__text_signature__[1:-1].split(", ")
                                    if v.__text_signature__
                                    else []
                                )
                            ]
                        )
                        else len(
                            [
                                arg
                                for arg in (
                                    v.__text_signature__[1:-1].split(", ")
                                    if v.__text_signature__
                                    else []
                                )
                                if arg.isalpha()
                            ]
                        )
                    )
                    if v.__text_signature__
                    else 1 if name == "log" else -1
                ),
                __math_function_decorator(v),
            )
            if isinstance(v := getattr(math, name), type(math.ulp))
            else GulfOfMexicoNumber(v)
        ),
    )
    for name in dir(math)
    if not name.startswith("__")
}  # the frick is this
BUILTIN_FUNCTION_KEYWORDS = {
    "new": Name(
        "new", BuiltinFunction(-1, db_new)
    ),  # Variadic - accepts class + optional init args
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
    "write": Name("write", BuiltinFunction(-1, db_write)),
    "regex_match": Name("regex_match", BuiltinFunction(1, db_regex_match)),
    "regex_findall": Name("regex_findall", BuiltinFunction(1, db_regex_findall)),
    "regex_replace": Name("regex_replace", BuiltinFunction(1, db_regex_replace)),
    "Canvas": Name("Canvas", BuiltinFunction(-1, db_create_canvas)),
    "Color": Name("Color", BuiltinFunction(-1, db_create_color)),
    "observe": Name("observe", BuiltinFunction(1, db_observe)),
    "past": Name("past", BuiltinFunction(2, db_past)),
    "future": Name("future", BuiltinFunction(1, db_future)),
    # Base/Radix number system functions
    "to_base": Name("to_base", BuiltinFunction(2, db_to_base)),
    "from_base": Name("from_base", BuiltinFunction(2, db_from_base)),
    "base_add": Name("base_add", BuiltinFunction(5, db_base_add)),
    "base_sub": Name("base_sub", BuiltinFunction(5, db_base_sub)),
    "base_mul": Name("base_mul", BuiltinFunction(5, db_base_mul)),
    "base_div": Name("base_div", BuiltinFunction(5, db_base_div)),
    "to_binary": Name("to_binary", BuiltinFunction(1, db_to_binary)),
    "to_octal": Name("to_octal", BuiltinFunction(1, db_to_octal)),
    "to_hex": Name("to_hex", BuiltinFunction(1, db_to_hex)),
    "from_binary": Name("from_binary", BuiltinFunction(1, db_from_binary)),
    "from_octal": Name("from_octal", BuiltinFunction(1, db_from_octal)),
    "from_hex": Name("from_hex", BuiltinFunction(1, db_from_hex)),
    # Statistical functions
    "mean": Name("mean", BuiltinFunction(1, db_mean)),
    "median": Name("median", BuiltinFunction(1, db_median)),
    "mode": Name("mode", BuiltinFunction(1, db_mode)),
    "variance": Name("variance", BuiltinFunction(1, db_variance)),
    "stdev": Name("stdev", BuiltinFunction(1, db_stdev)),
    "min_val": Name("min_val", BuiltinFunction(1, db_min_val)),
    "max_val": Name("max_val", BuiltinFunction(1, db_max_val)),
    "sum_list": Name("sum_list", BuiltinFunction(1, db_sum_list)),
    "percentile": Name("percentile", BuiltinFunction(2, db_percentile)),
    "correlation": Name("correlation", BuiltinFunction(2, db_correlation)),
    # Financial functions
    "compound_interest": Name(
        "compound_interest", BuiltinFunction(4, db_compound_interest)
    ),
    "simple_interest": Name("simple_interest", BuiltinFunction(3, db_simple_interest)),
    "pmt": Name("pmt", BuiltinFunction(3, db_pmt)),
    "fv": Name("fv", BuiltinFunction(4, db_fv)),
    "pv": Name("pv", BuiltinFunction(3, db_pv)),
    "npv": Name("npv", BuiltinFunction(2, db_npv)),
    # Business metrics
    "roi": Name("roi", BuiltinFunction(2, db_roi)),
    "profit_margin": Name("profit_margin", BuiltinFunction(2, db_profit_margin)),
    "cagr": Name("cagr", BuiltinFunction(3, db_cagr)),
    "break_even": Name("break_even", BuiltinFunction(3, db_break_even)),
    # Scientific/Mathematical functions
    "linear_regression": Name(
        "linear_regression", BuiltinFunction(2, db_linear_regression)
    ),
    "predict": Name("predict", BuiltinFunction(3, db_predict)),
    "derivative": Name("derivative", BuiltinFunction(2, db_derivative)),
    "integrate": Name("integrate", BuiltinFunction(2, db_integrate)),
    "quadratic_solve": Name("quadratic_solve", BuiltinFunction(3, db_quadratic_solve)),
}
BUILTIN_VALUE_KEYWORDS = {
    "true": Name("true", GulfOfMexicoBoolean(True)),
    "maybe": Name("maybe", GulfOfMexicoBoolean(None)),
    "false": Name("false", GulfOfMexicoBoolean(False)),
    "undefined": Name("undefined", GulfOfMexicoUndefined()),
    "": Name("", GulfOfMexicoSpecialBlankValue()),
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
}  # this is so cursed

KEYWORDS |= (
    BUILTIN_FUNCTION_KEYWORDS
    | BUILTIN_VALUE_KEYWORDS
    | MATH_FUNCTION_KEYWORDS
    | NUMBER_NAME_KEYWORDS
)
