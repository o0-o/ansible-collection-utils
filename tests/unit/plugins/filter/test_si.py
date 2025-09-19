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

"""Smoke tests for the si filter wrapper."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from ansible_collections.o0_o.utils.plugins.filter.si import FilterModule
from ansible_collections.o0_o.utils.plugins.module_utils import parse_si


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter instance per test."""
    return FilterModule()


@pytest.mark.parametrize(
    "value,kwargs",
    [
        ("2400MHz", {}),
        ("32GB", {}),
        ("20G", {"binary": True}),
        ("1024KB", {"optimize": False}),
    ],
)
def test_si_delegates_to_helper(
    filter_module: FilterModule, value: str, kwargs: Dict[str, Any]
) -> None:
    """Wrapper should return helper output unchanged."""
    expected = parse_si(value, **kwargs)
    assert filter_module.si_filter(value, **kwargs) == expected


def test_si_filter_registration(filter_module: FilterModule) -> None:
    """Ensure the filter table exposes the si callable."""
    filters = filter_module.filters()
    assert set(filters) == {"si"}
    assert filters["si"].__func__ is FilterModule.si_filter


def test_si_swallows_helper_errors(
    monkeypatch: pytest.MonkeyPatch, filter_module: FilterModule
) -> None:
    """Helper failures should return an empty mapping."""

    def boom(*args: Any, **kwargs: Any) -> None:
        raise ValueError("broken")

    monkeypatch.setattr(
        "ansible_collections.o0_o.utils.plugins.filter.si.parse_si",
        boom,
    )
    assert filter_module.si_filter("value") == {}
