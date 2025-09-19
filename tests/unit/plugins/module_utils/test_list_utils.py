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

from typing import Any, Callable, Iterable, List

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


@pytest.mark.parametrize(
    "value_factory,want_list,expected,unordered",
    [
        (lambda: None, True, [], False),
        (lambda: "foo", True, ["foo"], False),
        (lambda: "", True, [""], False),
        (lambda: ["foo", "bar"], True, ["foo", "bar"], False),
        (lambda: ("foo", "bar"), True, ["foo", "bar"], False),
        (lambda: tuple(), True, [], False),
        (lambda: range(3), True, [0, 1, 2], False),
        (lambda: (x for x in range(3)), True, [0, 1, 2], False),
        (lambda: {1, 2, 3}, True, {1, 2, 3}, True),
        (lambda: set(), True, [], False),
        (lambda: {"key": "value"}, True, [{"key": "value"}], False),
        (lambda: {"a": 1, "b": 2}.items(), True, [("a", 1), ("b", 2)], False),
        (lambda: b"ab", True, [97, 98], False),
        (lambda: None, False, None, False),
        (lambda: "foo", False, "foo", False),
        (lambda: "", False, "", False),
        (lambda: [], False, None, False),
        (lambda: ["foo"], False, "foo", False),
        (lambda: [1, 2], False, [1, 2], False),
        (lambda: (), False, None, False),
        (lambda: ("foo",), False, "foo", False),
        (lambda: ("foo", "bar"), False, ["foo", "bar"], False),
        (lambda: set(), False, None, False),
        (lambda: {42}, False, 42, False),
        (lambda: {1, 2}, False, {1, 2}, True),
        (lambda: range(0), False, None, False),
        (lambda: range(1), False, 0, False),
        (lambda: range(3), False, [0, 1, 2], False),
        (lambda: (x for x in range(1)), False, 0, False),
        (lambda: (x for x in range(3)), False, [0, 1, 2], False),
        (lambda: {"key": "value"}, False, {"key": "value"}, False),
        (lambda: {"a": 1, "b": 2}.items(), False, [("a", 1), ("b", 2)], False),
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
