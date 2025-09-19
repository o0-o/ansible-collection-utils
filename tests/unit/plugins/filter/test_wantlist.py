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

"""Smoke tests for the wantlist filter wrappers."""

from __future__ import annotations

from typing import Any

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.wantlist import FilterModule
from ansible_collections.o0_o.utils.plugins.module_utils import (
    wantlist as wantlist_helper,
)


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter instance per test."""
    return FilterModule()


@pytest.mark.parametrize(
    "value,want_list",
    [(["foo"], True), (["foo"], False), (None, True), (None, False)],
)
def test_wantlist_delegates_to_helper(
    filter_module: FilterModule, value: Any, want_list: bool
) -> None:
    """Filter should behave exactly like the helper implementation."""
    expected = wantlist_helper(value, want_list=want_list)
    assert (
        filter_module.wantlist_filter(value, want_list=want_list) == expected
    )


def test_wantlist_filter_registration(filter_module: FilterModule) -> None:
    """Ensure filter metadata exposes the wantlist callable."""
    filters = filter_module.filters()
    assert set(filters) == {"wantlist"}
    assert filters["wantlist"].__func__ is FilterModule.wantlist_filter


def test_wantlist_error_is_wrapped(
    monkeypatch: pytest.MonkeyPatch, filter_module: FilterModule
) -> None:
    """Unexpected helper errors should raise AnsibleFilterError."""

    def boom(*args: Any, **kwargs: Any) -> None:
        raise ValueError("boom")

    monkeypatch.setattr(
        "ansible_collections.o0_o.utils.plugins.filter.wantlist.wantlist",
        boom,
    )
    with pytest.raises(AnsibleFilterError, match="ValueError"):
        filter_module.wantlist_filter("value")
