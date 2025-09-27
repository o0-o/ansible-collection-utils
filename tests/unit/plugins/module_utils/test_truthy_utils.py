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

"""Unit tests for truthy or integer conversion utilities."""

from __future__ import annotations

from typing import Any

import pytest

from ansible_collections.o0_o.utils.plugins.module_utils import (
    truthy_or_integer,
)


@pytest.mark.parametrize(
    "value,zero_is_false,only_positive,expected",
    [
        (0, False, False, 0),
        ("0", False, False, 0),
        ("+0", False, False, 0),
        (" 5 ", False, False, 5),
        (5, False, False, 5),
        (-2, False, False, -2),
        ("-2", False, False, -2),
        ("+4", False, True, 4),
        (0, True, False, False),
        ("0", True, False, False),
        (0, True, True, False),
    ],
)
def test_integer_preference(
    value: Any, zero_is_false: bool, only_positive: bool, expected: Any
) -> None:
    """Integers and integer-like strings should return integers."""
    result = truthy_or_integer(
        value,
        zero_is_false=zero_is_false,
        only_positive=only_positive,
    )
    assert result == expected


@pytest.mark.parametrize(
    "value",
    [True, False, "yes", "no", "True", "FALSE", "invalid", object(), 3.14],
)
def test_boolean_fallback(value: Any) -> None:
    """Boolean-like values should round-trip via the boolean helper."""
    result = truthy_or_integer(value)
    assert isinstance(result, bool)
    assert result is bool(result)


def test_only_positive_rejects_negative() -> None:
    """Reject negatives when only_positive is set."""
    with pytest.raises(ValueError, match="positive integer"):
        truthy_or_integer(-1, only_positive=True)


def test_only_positive_rejects_zero_without_override() -> None:
    """Zero fails when only_positive is true without zero_is_false."""
    with pytest.raises(ValueError, match="received 0"):
        truthy_or_integer(0, only_positive=True)
