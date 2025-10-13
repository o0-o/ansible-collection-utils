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

"""Smoke tests for the datetime filter wrapper."""

from __future__ import annotations

from typing import Any

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.datetime import (
    FilterModule,
)
from ansible_collections.o0_o.utils.plugins.module_utils import parse_datetime


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter instance per test."""
    return FilterModule()


@pytest.mark.parametrize(
    "value",
    [
        "2025-01-15",
        "01/15/2025",
        "2025-01-15 14:30",
        "2:45 PM",
        "14:30:45",
    ],
)
def test_datetime_delegates_to_helper(
    filter_module: FilterModule, value: str
) -> None:
    """Wrapper should return helper output unchanged."""
    expected = parse_datetime(value)
    assert filter_module.datetime_filter(value) == expected


def test_datetime_filter_registration(filter_module: FilterModule) -> None:
    """Ensure the filter table exposes the datetime callable."""
    filters = filter_module.filters()
    assert set(filters) == {"datetime"}
    assert filters["datetime"].__func__ is FilterModule.datetime_filter


def test_datetime_returns_none_for_invalid(
    filter_module: FilterModule,
) -> None:
    """Invalid inputs should return None."""
    result = filter_module.datetime_filter("not a date")
    assert result is None


def test_datetime_handles_empty_string(filter_module: FilterModule) -> None:
    """Empty string should return None."""
    result = filter_module.datetime_filter("")
    assert result is None


def test_datetime_date_only_format(filter_module: FilterModule) -> None:
    """Test filter with date-only input."""
    result = filter_module.datetime_filter("2025-01-15")
    assert result is not None
    assert "seconds" in result
    assert result["iso8601"] == "2025-01-15"
    assert "2025" in result["pretty"]


def test_datetime_time_only_format(filter_module: FilterModule) -> None:
    """Test filter with time-only input."""
    result = filter_module.datetime_filter("14:30")
    assert result is not None
    assert "seconds" in result
    assert result["iso8601"] == "14:30"
    assert "2:30 p.m." in result["pretty"]


def test_datetime_full_datetime_format(filter_module: FilterModule) -> None:
    """Test filter with full datetime input."""
    result = filter_module.datetime_filter("2025-01-15 14:30:45")
    assert result is not None
    assert "seconds" in result
    assert result["iso8601"] == "2025-01-15T14:30:45"
    assert "2:30:45 p.m." in result["pretty"]


def test_datetime_raises_on_import_error(
    monkeypatch: pytest.MonkeyPatch, filter_module: FilterModule
) -> None:
    """Filter should raise AnsibleFilterError if libraries missing."""

    def boom(*args: Any, **kwargs: Any) -> None:
        raise ImportError("dateutil not available")

    monkeypatch.setattr(
        "ansible_collections.o0_o.utils.plugins.filter.datetime."
        "parse_datetime",
        boom,
    )

    with pytest.raises(AnsibleFilterError, match="not available"):
        filter_module.datetime_filter("2025-01-15")


def test_datetime_raises_on_unexpected_error(
    monkeypatch: pytest.MonkeyPatch, filter_module: FilterModule
) -> None:
    """Filter should raise AnsibleFilterError for unexpected failures."""

    def boom(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("unexpected error")

    monkeypatch.setattr(
        "ansible_collections.o0_o.utils.plugins.filter.datetime."
        "parse_datetime",
        boom,
    )

    with pytest.raises(AnsibleFilterError, match="Failed to parse"):
        filter_module.datetime_filter("2025-01-15")
