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

"""Unit tests for the lines2items filter."""

from __future__ import annotations

from typing import Any

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.lines2items import (
    FilterModule,
)


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter instance for each test."""
    return FilterModule()


@pytest.mark.parametrize(
    "value,keepends,expected",
    [
        ("a\nb", False, ["a", "b"]),
        ("a\n\nb", False, ["a", "", "b"]),
        ("a\r\n", True, ["a\r\n"]),
        ("single", False, ["single"]),
    ],
)
def test_lines2items_splits_expectedly(
    filter_module: FilterModule,
    value: str,
    keepends: bool,
    expected: Any,
) -> None:
    """Verify splitlines behaviour matches Python's implementation."""
    result = filter_module.lines2items_filter(value, keepends=keepends)
    assert result == expected


def test_lines2items_registration(filter_module: FilterModule) -> None:
    """Ensure the filter is registered under its public names."""
    filters = filter_module.filters()
    assert set(filters) == {"lines2items", "splitlines"}
    for name in ("lines2items", "splitlines"):
        assert filters[name].__func__ is FilterModule.lines2items_filter


def test_splitlines_alias_behaves_like_primary(
    filter_module: FilterModule,
) -> None:
    """Alias should mirror the primary implementation."""
    filters = filter_module.filters()
    primary = filters["lines2items"]
    alias = filters["splitlines"]
    text = "first\nsecond"
    assert alias(text) == primary(text)


def test_lines2items_decoding_error(filter_module: FilterModule) -> None:
    """Invalid bytes should raise a wrapped AnsibleFilterError."""
    with pytest.raises(AnsibleFilterError, match="UnicodeDecodeError"):
        filter_module.lines2items_filter(b"\xff", keepends=False)
