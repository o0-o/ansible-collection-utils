# vim: ts=4:sw=4:sts=4:et:ft=python
# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; -*-
#
# GNU General Public License v3.0+
# SPDX-License-Identifier: GPL-3.0-or-later
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Copyright (c) 2025 oØ.o (@o0-o)
#
# This file is part of the o0_o.utils Ansible Collection.

"""Unit tests for list utilities."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Tuple

import pytest

from ansible_collections.o0_o.utils.plugins.module_utils import (
    string2items,
    wantlist,
)


@pytest.mark.parametrize(
    "value,delimiter,trim,expected",
    [
        ("foo,bar,baz", ",", True, ["foo", "bar", "baz"]),
        ("foo, bar , baz", ",", True, ["foo", "bar", "baz"]),
        ("foo, bar , baz", ",", False, ["foo", " bar ", " baz"]),
        ("foo||bar||baz", "||", True, ["foo", "bar", "baz"]),
        ("foo,,bar", ",", True, ["foo", "bar"]),
        ("foo,,bar", ",", False, ["foo", "", "bar"]),
        (",foo,bar,", ",", True, ["foo", "bar"]),
        (",foo,bar,", ",", False, ["", "foo", "bar", ""]),
        ("", ",", True, []),
        ("", ",", False, [""]),
        (123, ",", True, ["123"]),
        (True, ",", True, ["True"]),
    ],
)
def test_string2items(
    value: Any, delimiter: str, trim: bool, expected: List[str]
) -> None:
    """Verify string2items behaviours for common inputs."""
    assert string2items(value, delimiter=delimiter, trim=trim) == expected


def test_string2items_multichar_delimiter() -> None:
    """Ensure multi-character delimiters split correctly."""
    assert string2items("foo::bar::baz", delimiter="::") == [
        "foo",
        "bar",
        "baz",
    ]


def test_string2items_cast_error() -> None:
    """Objects that cannot be stringified should raise a TypeError."""

    class UnStringable:
        def __str__(self) -> str:
            raise ValueError("Cannot convert to string")

    with pytest.raises(TypeError):
        string2items(UnStringable())


ValueFactory = Callable[[], Any]

# Helpers wrap callables to avoid pylint lambda warnings while creating
# fresh iterables for each parametrised invocation.


def make_constant(value: Any) -> ValueFactory:
    """Return a factory that always yields the provided value."""

    def _factory() -> Any:
        return value

    return _factory


def make_generator(limit: int) -> ValueFactory:
    """Return a factory that creates a fresh range-based generator."""

    def _factory() -> Iterable[int]:
        return (x for x in range(limit))

    return _factory


def make_dict_items(mapping: Dict[str, int]) -> ValueFactory:
    """Return a factory that exposes dictionary item views."""

    def _factory() -> Iterable[Tuple[str, int]]:
        return mapping.items()

    return _factory


@pytest.mark.parametrize(
    "value_factory,want_list,expected,unordered",
    [
        (make_constant(None), True, [], False),
        (make_constant("foo"), True, ["foo"], False),
        (make_constant(""), True, [""], False),
        (make_constant(["foo", "bar"]), True, ["foo", "bar"], False),
        (make_constant(("foo", "bar")), True, ["foo", "bar"], False),
        (make_constant(tuple()), True, [], False),
        (make_constant(range(3)), True, [0, 1, 2], False),
        (make_generator(3), True, [0, 1, 2], False),
        (make_constant({1, 2, 3}), True, {1, 2, 3}, True),
        (make_constant(set()), True, [], False),
        (make_constant({"key": "value"}), True, [{"key": "value"}], False),
        (make_dict_items({"a": 1, "b": 2}), True, [("a", 1), ("b", 2)], False),
        (make_constant(b"ab"), True, [97, 98], False),
        (make_constant(None), False, None, False),
        (make_constant("foo"), False, "foo", False),
        (make_constant(""), False, "", False),
        (make_constant([]), False, None, False),
        (make_constant(["foo"]), False, "foo", False),
        (make_constant([1, 2]), False, [1, 2], False),
        (make_constant(()), False, None, False),
        (make_constant(("foo",)), False, "foo", False),
        (make_constant(("foo", "bar")), False, ["foo", "bar"], False),
        (make_constant(set()), False, None, False),
        (make_constant({42}), False, 42, False),
        (make_constant({1, 2}), False, {1, 2}, True),
        (make_constant(range(0)), False, None, False),
        (make_constant(range(1)), False, 0, False),
        (make_constant(range(3)), False, [0, 1, 2], False),
        (make_generator(1), False, 0, False),
        (make_generator(3), False, [0, 1, 2], False),
        (make_constant({"key": "value"}), False, {"key": "value"}, False),
        (
            make_dict_items({"a": 1, "b": 2}),
            False,
            [("a", 1), ("b", 2)],
            False,
        ),
    ],
)
def test_wantlist_behaviour(
    value_factory: ValueFactory,
    want_list: bool,
    expected: Any,
    unordered: bool,
) -> None:
    """Validate wantlist conversions across common types."""
    value = value_factory()
    result = wantlist(value, want_list=want_list)
    if unordered:
        assert isinstance(expected, Iterable)
        assert isinstance(result, Iterable)
        assert set(result) == set(expected)
    else:
        assert result == expected


def test_wantlist_custom_object() -> None:
    """Non-iterable custom objects should round-trip correctly."""

    class CustomObject:
        def __init__(self, value: str) -> None:
            self.value = value

    obj = CustomObject("value")
    assert wantlist(obj, want_list=True) == [obj]
    assert wantlist(obj, want_list=False) is obj


def test_wantlist_dict_views_share_reference() -> None:
    """Dict view iterables should become concrete lists when needed."""
    mapping = {"a": 1, "b": 2}
    keys_result = wantlist(mapping.keys(), want_list=True)
    assert keys_result == ["a", "b"]
    values_result = wantlist(mapping.values(), want_list=True)
    assert values_result == [1, 2]
