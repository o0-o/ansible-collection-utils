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

"""Smoke tests for the hostname filter wrapper."""

from __future__ import annotations

from typing import Any

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.hostname import FilterModule
from ansible_collections.o0_o.utils.plugins.module_utils import parse_hostname


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter instance per test."""
    return FilterModule()


@pytest.mark.parametrize(
    "value",
    ["www.example.com", {"hostname": "server.local"}],
)
def test_hostname_delegates_to_helper(
    filter_module: FilterModule, value: Any
) -> None:
    """Wrapper should mirror helper output."""
    expected = parse_hostname(value)
    assert filter_module.hostname_filter(value) == expected


def test_hostname_filter_registration(filter_module: FilterModule) -> None:
    """Ensure the filter table exposes the hostname callable."""
    filters = filter_module.filters()
    assert set(filters) == {"hostname"}
    assert filters["hostname"].__func__ is FilterModule.hostname_filter


def test_hostname_error_wrapped(
    monkeypatch: pytest.MonkeyPatch, filter_module: FilterModule
) -> None:
    """Helper failures should surface as AnsibleFilterError."""

    def boom(*args: Any, **kwargs: Any) -> None:
        raise ValueError("boom")

    monkeypatch.setattr(
        (
            "ansible_collections.o0_o.utils.plugins.filter.hostname."
            "parse_hostname"
        ),
        boom,
    )
    with pytest.raises(AnsibleFilterError, match="ValueError"):
        filter_module.hostname_filter("example.com")
