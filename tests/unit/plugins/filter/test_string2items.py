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

"""Tests for string2items filter."""

from __future__ import annotations

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.string2items import (
    FilterModule,
)


class TestString2Items:
    """Test string2items filter."""

    @pytest.fixture
    def filter_module(self):
        """Create FilterModule instance."""
        return FilterModule()

    @pytest.mark.parametrize(
        "value,delimiter,trim,expected",
        [
            # Basic comma-separated
            ("foo,bar,baz", ",", True, ["foo", "bar", "baz"]),
            # With spaces - trimmed
            ("foo, bar , baz", ",", True, ["foo", "bar", "baz"]),
            # With spaces - not trimmed
            ("foo, bar , baz", ",", False, ["foo", " bar ", " baz"]),
            # Empty items filtered when trim=True
            ("foo,,bar", ",", True, ["foo", "bar"]),
            # Empty items kept when trim=False
            ("foo,,bar", ",", False, ["foo", "", "bar"]),
            # Different delimiter
            ("foo|bar|baz", "|", True, ["foo", "bar", "baz"]),
            # Semicolon delimiter
            ("foo;bar;baz", ";", True, ["foo", "bar", "baz"]),
            # Space delimiter
            ("foo bar baz", " ", True, ["foo", "bar", "baz"]),
            # Leading/trailing delimiters with trim
            (",foo,bar,", ",", True, ["foo", "bar"]),
            # Leading/trailing delimiters without trim
            (",foo,bar,", ",", False, ["", "foo", "bar", ""]),
            # Single item
            ("foo", ",", True, ["foo"]),
            # Empty string
            ("", ",", True, []),
            ("", ",", False, [""]),
            # Only delimiters
            (",,,", ",", True, []),
            (",,,", ",", False, ["", "", "", ""]),
            # Spaces only with trim
            ("  ,  ,  ", ",", True, []),
            # Numbers get converted to string
            (123, ",", True, ["123"]),
            (42, "-", True, ["42"]),
            # Booleans get converted to string
            (True, ",", True, ["True"]),
            (False, ",", True, ["False"]),
        ],
    )
    def test_string2items_parametrized(
        self, filter_module, value, delimiter, trim, expected
    ):
        """Test string2items with various inputs."""
        result = filter_module.string2items(value, delimiter, trim)
        assert result == expected

    def test_default_parameters(self, filter_module):
        """Test default parameter values."""
        # Default delimiter is comma, default trim is True
        assert filter_module.string2items("a,b,c") == ["a", "b", "c"]
        assert filter_module.string2items("a, b, c") == ["a", "b", "c"]

    def test_multichar_delimiter(self, filter_module):
        """Test multi-character delimiters."""
        assert filter_module.string2items("foo::bar::baz", "::", True) == [
            "foo",
            "bar",
            "baz",
        ]
        assert filter_module.string2items("foo<->bar<->baz", "<->", True) == [
            "foo",
            "bar",
            "baz",
        ]

    def test_non_string_conversions(self, filter_module):
        """Test that various types get converted to strings."""
        # Lists get converted to string representation, then split by
        # comma. The string "['already', 'a', 'list']" contains commas
        result = filter_module.string2items(["already", "a", "list"])
        # It will be split on the commas in the string representation
        assert "['already'" in result[0]
        assert "'list']" in result[-1]

        # Dicts get converted to string representation
        # Use a dict without commas to avoid splitting issues
        result = filter_module.string2items({"key": "value"}, delimiter="|")
        assert result == ["{'key': 'value'}"]

        # Numbers get converted
        assert filter_module.string2items(123) == ["123"]
        assert filter_module.string2items(3.14) == ["3.14"]

        # Booleans get converted
        assert filter_module.string2items(True) == ["True"]
        assert filter_module.string2items(False) == ["False"]

    def test_uncastable_error(self, filter_module):
        """Test that uncastable objects raise errors."""

        # Create an object that raises an exception when str() is called
        class UnStringable:
            def __str__(self):
                raise ValueError("Cannot convert to string")

        with pytest.raises(
            AnsibleFilterError, match="string2items requires a string"
        ):
            filter_module.string2items(UnStringable())
