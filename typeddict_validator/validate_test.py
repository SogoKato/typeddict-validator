from typing import Any, Optional, Type, TypedDict, Union
import unittest

from .validate import (
    DictMissingKeyException,
    DictValueTypeMismatchException,
    validate_typeddict,
)


class BasicTypedDict(TypedDict):
    s: str
    i: int
    b: bool


class HasListValueTypedDict(TypedDict):
    l: list[str]
    l_union: list[Union[str, int]]
    l_optional: list[Optional[str]]
    l_any: list[Any]


class HasDictValueTypedDict(TypedDict):
    d: dict[str, str]
    d_union: dict[str, Union[str, int]]
    d_optional: dict[str, Optional[str]]
    d_any: dict[str, Any]


class HasTypedDictValueTypedDict(TypedDict):
    td: BasicTypedDict


class HasUnionValueTypedDict(TypedDict):
    u: Union[str, int]
    o: Optional[str]
    o_list: Optional[list[str]]
    o_dict: Optional[dict[str, str]]


class TestValidateTypedDict(unittest.TestCase):

    Param = tuple[dict[str, Any], Any]

    success_params_list: list[Param] = [
        (
            {"s": "a", "i": 0, "b": False},
            BasicTypedDict,
        ),
        (
            {
                "l": ["a", "b"],
                "l_union": ["a", 0],
                "l_optional": ["a", None],
                "l_any": ["a", False],
            },
            HasListValueTypedDict,
        ),
        (
            {
                "l": [],
                "l_union": [],
                "l_optional": [],
                "l_any": [],
            },
            HasListValueTypedDict,
        ),
        (
            {
                "d": {"s": "a"},
                "d_union": {"k1": "a", "k2": 0},
                "d_optional": {"k1": "a", "k2": None},
                "d_any": {"k1": "a", "k2": False},
            },
            HasDictValueTypedDict,
        ),
        (
            {
                "d": {},
                "d_union": {},
                "d_optional": {},
                "d_any": {},
            },
            HasDictValueTypedDict,
        ),
        (
            {"td": {"s": "a", "i": 0, "b": False}},
            HasTypedDictValueTypedDict,
        ),
        (
            {"u": "a", "o": "b", "o_list": ["a", "b"], "o_dict": {"s": "a"}},
            HasUnionValueTypedDict,
        ),
        (
            {"u": 0, "o": None, "o_list": None, "o_dict": None},
            HasUnionValueTypedDict,
        ),
    ]

    failure_params_list: list[tuple[Param, Type[Exception]]] = [
        (
            (
                {},
                dict[str, Any],  # must be a TypeDict
            ),
            ValueError,
        ),
        (
            (
                {"s": "a", "i": 0},  # b is missing
                BasicTypedDict,
            ),
            DictMissingKeyException,
        ),
        (
            (
                {"s": "a", "i": 0, "b": "False"},  # b is invalid
                BasicTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "l": ["a", 0],  # l is invalid
                    "l_union": ["a", 0],
                    "l_optional": ["a", None],
                    "l_any": ["a", False],
                },
                HasListValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "l": ["a", "b"],
                    "l_union": ["a", 0, False],  # l_union is invalid
                    "l_optional": ["a", None],
                    "l_any": ["a", False],
                },
                HasListValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "d": {"s": 0},  # d is invalid
                    "d_union": {"k1": "a", "k2": 0},
                    "d_optional": {"k1": "a", "k2": None},
                    "d_any": {"k1": "a", "k2": False},
                },
                HasDictValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "d": {"s": "a"},
                    "d_union": {"k1": "a", "k2": False},  # d_union is invalid
                    "d_optional": {"k1": "a", "k2": None},
                    "d_any": {"k1": "a", "k2": False},
                },
                HasDictValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {"td": {"s": "a", "i": 0, "b": "False"}},  # b is invalid
                HasTypedDictValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "u": False,  # u is invalid
                    "o": "b",
                    "o_list": ["a", "b"],
                    "o_dict": {"s": "a"},
                },
                HasUnionValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "u": "a",
                    "o": False,  # o is invalid
                    "o_list": ["a", "b"],
                    "o_dict": {"s": "a"},
                },
                HasUnionValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "u": "a",
                    "o": "b",
                    "o_list": False,  # o_list is invalid
                    "o_dict": {"s": "a"},
                },
                HasUnionValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "u": "a",
                    "o": "b",
                    "o_list": ["a", "b"],
                    "o_dict": False,  # o_dict is invalid
                },
                HasUnionValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "u": "a",
                    "o": "b",
                    "o_list": [0],  # o_list is invalid
                    "o_dict": {"s": "a"},
                },
                HasUnionValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
        (
            (
                {
                    "u": "a",
                    "o": "b",
                    "o_list": ["a", "b"],
                    "o_dict": {"s": 0},  # o_dict is invalid
                },
                HasUnionValueTypedDict,
            ),
            DictValueTypeMismatchException,
        ),
    ]

    def test_success(self):
        for success_params in self.success_params_list:
            with self.subTest():
                is_valid = validate_typeddict(*success_params)
                self.assertEqual(is_valid, True)

    def test_success_with_silent(self):
        for success_params in self.success_params_list:
            with self.subTest():
                is_valid = validate_typeddict(*success_params, silent=True)
                self.assertEqual(is_valid, True)

    def test_failure(self):
        for failure_params, error in self.failure_params_list:
            with self.subTest():
                with self.assertRaises(error):
                    validate_typeddict(*failure_params)

    def test_failure_with_silent(self):
        for failure_params, error in self.failure_params_list:
            with self.subTest():
                if error == ValueError:
                    continue
                is_valid = validate_typeddict(*failure_params, silent=True)
                self.assertEqual(is_valid, False)
