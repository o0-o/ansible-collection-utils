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

"""Smoke tests for the truthy_or_integer filter wrapper."""

from __future__ import annotations

from typing import Any

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.truthy_or_integer import (
    FilterModule,
)
from ansible_collections.o0_o.utils.plugins.module_utils import (
    truthy_or_integer as helper,
)


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a fresh filter instance for each test."""
    return FilterModule()


@pytest.mark.parametrize(
    "value,zero_is_false,only_positive",
    [
        ("yes", False, False),
        ("0", True, False),
        (3, False, False),
        (-1, False, False),
        (" 7 ", False, True),
    ],
)
def test_filter_matches_helper(
    filter_module: FilterModule,
    value: Any,
    zero_is_false: bool,
    only_positive: bool,
) -> None:
    """Filter output should match the helper implementation."""
    expected = helper(
        value,
        zero_is_false=zero_is_false,
        only_positive=only_positive,
    )
    result = filter_module.truthy_or_integer_filter(
        value,
        zero_is_false=zero_is_false,
        only_positive=only_positive,
    )
    assert result == expected


def test_filter_registration(filter_module: FilterModule) -> None:
    """Ensure the filter is registered under the expected name."""
    filters = filter_module.filters()
    assert set(filters) == {"truthy_or_integer"}
    assert (
        filters["truthy_or_integer"].__func__
        is FilterModule.truthy_or_integer_filter
    )


def test_filter_wraps_errors(filter_module: FilterModule) -> None:
    """Unexpected helper failures should raise AnsibleFilterError."""
    with pytest.raises(AnsibleFilterError, match="ValueError"):
        filter_module.truthy_or_integer_filter(
            -1,
            only_positive=True,
        )
