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

"""Unit tests for the rekey filter."""

from __future__ import annotations

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.rekey import FilterModule


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter instance per test."""
    return FilterModule()


def test_rekey_basic(filter_module: FilterModule) -> None:
    """Re-key mapping by name while storing original id."""
    users = {
        "1000": {"name": "o0-o", "home": "/home/o0-o"},
        "1001": {"name": "foo", "home": "/home/foo"},
    }
    result = filter_module.rekey_filter(
        users,
        key_name="name",
        store_key_as="id",
    )
    assert result == {
        "o0-o": {"home": "/home/o0-o", "id": "1000"},
        "foo": {"home": "/home/foo", "id": "1001"},
    }


def test_rekey_key_candidates(filter_module: FilterModule) -> None:
    """Key candidates should fall back gracefully."""
    users = {
        "1000": {"name": "o0-o", "home": "/home/o0-o"},
        "1001": {"identifier": "foo", "home": "/home/foo"},
    }
    result = filter_module.rekey_filter(
        users,
        key_name=["name", "identifier"],
        store_key_as="id",
    )
    assert result == {
        "o0-o": {"home": "/home/o0-o", "id": "1000"},
        "foo": {"home": "/home/foo", "id": "1001"},
    }


def test_rekey_skip_missing(filter_module: FilterModule) -> None:
    """Entries without a key candidate can be skipped."""
    users = {
        "1000": {"home": "/home/o0-o"},
        "1001": {"name": "foo", "home": "/home/foo"},
    }
    result = filter_module.rekey_filter(
        users,
        key_name="name",
        store_key_as="id",
        skip_missing_key=True,
    )
    assert result == {"foo": {"home": "/home/foo", "id": "1001"}}


def test_rekey_missing_key_error(filter_module: FilterModule) -> None:
    """Missing key candidates should raise when skipping is disabled."""
    with pytest.raises(AnsibleFilterError):
        filter_module.rekey_filter(
            {"1000": {"home": "/home"}}, key_name="name"
        )


def test_rekey_default_value(filter_module: FilterModule) -> None:
    """Default values should be inserted when requested."""
    users = {
        "1000": {"name": "o0-o", "meta": {}},
        "1001": {"name": "foo", "meta": None},
    }
    result = filter_module.rekey_filter(
        users,
        key_name="name",
        store_key_as="id",
        default_value={"source": "default"},
        allow_empty=False,
    )
    assert result == {
        "o0-o": {"id": "1000", "meta": {"source": "default"}},
        "foo": {"id": "1001", "meta": {"source": "default"}},
    }
