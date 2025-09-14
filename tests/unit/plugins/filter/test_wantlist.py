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

"""Tests for wantlist filter."""

from __future__ import annotations

import pytest

from ansible_collections.o0_o.utils.plugins.filter.wantlist import (
    FilterModule,
)


class TestWantList:
    """Test wantlist filter."""

    @pytest.fixture
    def filter_module(self):
        """Create FilterModule instance."""
        return FilterModule()

    @pytest.mark.parametrize(
        "value,want_list,expected",
        [
            # wantlist=True (default) cases
            # None -> []
            (None, True, []),
            # String -> [string]
            ("foo", True, ["foo"]),
            ("", True, [""]),
            # List -> list
            (["foo", "bar"], True, ["foo", "bar"]),
            ([1, 2, 3], True, [1, 2, 3]),
            ([], True, []),
            # Tuple -> list
            (("foo", "bar"), True, ["foo", "bar"]),
            ((), True, []),
            # Set -> list (order may vary)
            ({1, 2, 3}, True, [1, 2, 3]),
            (set(), True, []),
            # Single item list -> still a list
            (["foo"], True, ["foo"]),
            # Number -> [number]
            (42, True, [42]),
            (3.14, True, [3.14]),
            # Boolean -> [boolean]
            (True, True, [True]),
            (False, True, [False]),
            # Dict -> [dict]
            ({"key": "value"}, True, [{"key": "value"}]),
            # Range -> list
            (range(3), True, [0, 1, 2]),
            # wantlist=False cases
            # None -> None
            (None, False, None),
            # String -> string
            ("foo", False, "foo"),
            ("", False, ""),
            # Empty list -> None
            ([], False, None),
            # Single item list -> item
            (["foo"], False, "foo"),
            ([42], False, 42),
            # Multiple item list -> list
            (["foo", "bar"], False, ["foo", "bar"]),
            ([1, 2, 3], False, [1, 2, 3]),
            # Empty tuple -> None
            ((), False, None),
            # Single item tuple -> item
            (("foo",), False, "foo"),
            # Multiple item tuple -> list
            (("foo", "bar"), False, ["foo", "bar"]),
            # Empty set -> None
            (set(), False, None),
            # Single item set -> item
            ({42}, False, 42),
            # Multiple item set -> list (order may vary)
            ({1, 2}, False, [1, 2]),
            # Number -> number
            (42, False, 42),
            (3.14, False, 3.14),
            # Boolean -> boolean
            (True, False, True),
            (False, False, False),
            # Dict -> dict
            ({"key": "value"}, False, {"key": "value"}),
            # Range with no items -> None
            (range(0), False, None),
            # Range with one item -> item
            (range(1), False, 0),
            # Range with multiple items -> list
            (range(3), False, [0, 1, 2]),
        ],
    )
    def test_wantlist_parametrized(
        self, filter_module, value, want_list, expected
    ):
        """Test wantlist with various inputs and want_list settings."""
        result = filter_module.wantlist(value, want_list)
        # Handle set comparison (order doesn't matter)
        if isinstance(value, set) and want_list and len(value) > 1:
            assert set(result) == set(expected)
        elif isinstance(value, set) and not want_list and len(value) > 1:
            assert set(result) == set(expected)
        else:
            assert result == expected

    def test_default_parameter(self, filter_module):
        """Test default want_list=True."""
        # Default behavior is want_list=True
        assert filter_module.wantlist("foo") == ["foo"]
        assert filter_module.wantlist(None) == []
        assert filter_module.wantlist([1, 2]) == [1, 2]

    def test_notwantlist_behaviour_via_public_api(self, filter_module):
        """Exercise notwantlist semantics via wantlist(False)."""
        # None -> None
        assert filter_module.wantlist(None, False) is None
        # String -> string
        assert filter_module.wantlist("foo", False) == "foo"
        # Empty list -> None
        assert filter_module.wantlist([], False) is None
        # Single item list -> item
        assert filter_module.wantlist(["bar"], False) == "bar"
        # Multiple items -> list
        assert filter_module.wantlist([1, 2, 3], False) == [1, 2, 3]

    def test_nested_lists(self, filter_module):
        """Test handling of nested lists."""
        # Nested list with want_list=True
        nested = [["a", "b"], ["c", "d"]]
        assert filter_module.wantlist(nested, True) == [["a", "b"], ["c", "d"]]

        # Nested list with single inner list and want_list=False
        single_nested = [["a", "b"]]
        assert filter_module.wantlist(single_nested, False) == ["a", "b"]

    def test_generator_handling(self, filter_module):
        """Test handling of generator expressions."""
        gen = (x for x in range(3))
        result = filter_module.wantlist(gen, True)
        assert result == [0, 1, 2]

        # Single item generator with want_list=False
        gen_single = (x for x in range(1))
        assert filter_module.wantlist(gen_single, False) == 0

        # Empty generator with want_list=False
        gen_empty = (x for x in range(0))
        assert filter_module.wantlist(gen_empty, False) is None

    def test_dict_items_handling(self, filter_module):
        """Test handling of dict items/keys/values."""
        test_dict = {"a": 1, "b": 2}

        # dict.items() with want_list=True
        items_result = filter_module.wantlist(test_dict.items(), True)
        assert len(items_result) == 2
        assert ("a", 1) in items_result
        assert ("b", 2) in items_result

        # dict.keys() with want_list=True
        keys_result = filter_module.wantlist(test_dict.keys(), True)
        assert set(keys_result) == {"a", "b"}

        # dict.values() with want_list=True
        values_result = filter_module.wantlist(test_dict.values(), True)
        assert set(values_result) == {1, 2}

    def test_custom_object(self, filter_module):
        """Test handling of custom objects."""

        class CustomObj:
            def __init__(self, value):
                self.value = value

        obj = CustomObj("test")
        # Non-iterable object with want_list=True -> [object]
        assert filter_module.wantlist(obj, True) == [obj]
        # Non-iterable object with want_list=False -> object
        assert filter_module.wantlist(obj, False) == obj

    def test_bytes_handling(self, filter_module):
        """Test handling of bytes objects."""
        # bytes are iterable but should be treated as single item
        b = b"hello"
        # With want_list=True, bytes wrapped in list
        result_true = filter_module.wantlist(b, True)
        # bytes are iterable, so they get converted to list of integers
        assert result_true == list(b)

        # With want_list=False, bytes should return as list of integers
        result_false = filter_module.wantlist(b, False)
        assert result_false == list(b)

    def test_filter_registration(self, filter_module):
        """Test that filter is properly registered."""
        filters = filter_module.filters()
        assert "wantlist" in filters
        assert filters["wantlist"] == filter_module.wantlist
