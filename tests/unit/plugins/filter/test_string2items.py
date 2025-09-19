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

"""Smoke tests for the string2items filter wrapper."""

from __future__ import annotations

from typing import Any, List

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.string2items import (
    FilterModule,
)
from ansible_collections.o0_o.utils.plugins.module_utils import string2items


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter instance per test."""
    return FilterModule()


@pytest.mark.parametrize(
    "value,delimiter,trim",
    [
        ("foo,bar", ",", True),
        ("foo, bar , baz", ",", True),
        ("foo, bar , baz", ",", False),
        ("foo|bar|baz", "|", True),
        (123, ",", True),
    ],
)
def test_string2items_matches_helper(
    filter_module: FilterModule,
    value: Any,
    delimiter: str,
    trim: bool,
) -> None:
    """Wrapper should match helper output."""
    expected: List[str] = string2items(value, delimiter=delimiter, trim=trim)
    result = filter_module.string2items_filter(
        value, delimiter=delimiter, trim=trim
    )
    assert result == expected


def test_string2items_filter_registration(filter_module: FilterModule) -> None:
    """Ensure the filter table exposes the string2items callable."""
    filters = filter_module.filters()
    assert set(filters) == {"string2items"}
    assert filters["string2items"].__func__ is FilterModule.string2items_filter


def test_string2items_error_wrapped(
    monkeypatch: pytest.MonkeyPatch, filter_module: FilterModule
) -> None:
    """Helper exceptions should surface as AnsibleFilterError."""

    def boom(
        *args: Any, **kwargs: Any
    ) -> None:  # pragma: no cover - forced path
        raise TypeError("bad value")

    monkeypatch.setattr(
        (
            "ansible_collections.o0_o.utils.plugins.filter.string2items."
            "string2items"
        ),
        boom,
    )
    with pytest.raises(AnsibleFilterError, match="TypeError"):
        filter_module.string2items_filter(object())
