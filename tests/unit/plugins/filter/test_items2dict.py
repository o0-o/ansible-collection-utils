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

"""Unit tests for the items2dict filter."""

from __future__ import annotations

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.items2dict import (
    FilterModule,
)


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter module per test."""
    return FilterModule()


def test_items2dict_defaults(filter_module: FilterModule) -> None:
    """Default behaviour should mirror ansible.builtin.items2dict."""
    items = [{"key": "foo", "value": 1}, {"key": "bar", "value": 2}]
    assert filter_module.items2dict_filter(items) == {"foo": 1, "bar": 2}


def test_items2dict_value_none(filter_module: FilterModule) -> None:
    """When value is None the remaining mapping should be retained."""
    items = [
        {"name": "foo", "description": "bar"},
        {"name": "baz", "description": ""},
    ]
    result = filter_module.items2dict_filter(
        items, key_name="name", value_name=None
    )
    assert result == {
        "foo": {"description": "bar"},
        "baz": {"description": ""},
    }


def test_items2dict_key_name_list(filter_module: FilterModule) -> None:
    """Key candidates should fall back to later entries as needed."""
    items = [
        {"identifier": "foo", "description": "bar"},
        {"name": "baz", "description": "baz-desc"},
    ]
    result = filter_module.items2dict_filter(
        items,
        key_name=["name", "identifier"],
        value_name=None,
    )
    assert result == {
        "foo": {"description": "bar"},
        "baz": {"description": "baz-desc"},
    }


def test_items2dict_collision_fail(filter_module: FilterModule) -> None:
    """Duplicate keys should error when collision='fail'."""
    items = [{"key": "foo", "value": 1}, {"key": "foo", "value": 2}]
    with pytest.raises(AnsibleFilterError, match="duplicate key"):
        filter_module.items2dict_filter(items)


def test_items2dict_collision_list(filter_module: FilterModule) -> None:
    """Duplicate keys should aggregate into a list when requested."""
    items = [
        {"name": "foo", "description": "bar"},
        {"name": "foo", "description": "baz"},
    ]
    result = filter_module.items2dict_filter(
        items,
        key_name="name",
        value_name=None,
        collision="list",
    )
    assert result == {
        "foo": [
            {"description": "bar"},
            {"description": "baz"},
        ]
    }


def test_items2dict_collision_combine(filter_module: FilterModule) -> None:
    """Combine collisions should deep merge dictionaries via combine."""
    items = [
        {"name": "foo", "options": {"a": 1, "nested": {"x": 1}}},
        {
            "name": "foo",
            "options": {"b": 2, "nested": {"y": 2}},
        },
    ]
    result = filter_module.items2dict_filter(
        items,
        key_name="name",
        value_name="options",
        collision="combine",
        combine_args={"recursive": True},
    )
    assert result == {"foo": {"a": 1, "b": 2, "nested": {"x": 1, "y": 2}}}


def test_items2dict_combine_default_order(filter_module: FilterModule) -> None:
    """Default combine order should let later entries win conflicts."""
    items = [
        {"name": "foo", "options": {"value": "late"}},
        {"name": "foo", "options": {"value": "early"}},
    ]
    result = filter_module.items2dict_filter(
        items,
        key_name="name",
        value_name="options",
        collision="combine",
    )
    assert result == {"foo": {"value": "early"}}


def test_items2dict_reverse_combine_order(filter_module: FilterModule) -> None:
    """Reverse combine order should allow earlier entries to win."""
    items = [
        {"name": "foo", "options": {"value": "late"}},
        {"name": "foo", "options": {"value": "early"}},
    ]
    result = filter_module.items2dict_filter(
        items,
        key_name="name",
        value_name="options",
        collision="combine",
        reverse_combine_order=True,
    )
    assert result == {"foo": {"value": "late"}}


def test_items2dict_skip_missing_key(filter_module: FilterModule) -> None:
    """Items without keys are skipped when enabled."""
    items = [
        {"description": "bar"},
        {"name": "ok", "description": "baz"},
    ]
    result = filter_module.items2dict_filter(
        items,
        key_name=["name", "identifier"],
        value_name=None,
        skip_missing_key=True,
    )
    assert result == {"ok": {"description": "baz"}}


def test_items2dict_default_value_used(filter_module: FilterModule) -> None:
    """Missing values should fall back to the provided default."""
    items = [{"key": "foo"}]
    result = filter_module.items2dict_filter(
        items,
        default_value="fallback",
    )
    assert result == {"foo": "fallback"}


def test_items2dict_default_value_for_empty_dict(
    filter_module: FilterModule,
) -> None:
    """Empty dictionaries trigger default when allow_empty is false."""
    items = [{"key": "foo", "value": {}}]
    result = filter_module.items2dict_filter(
        items,
        default_value={"from": "default"},
        allow_empty=False,
        collision="combine",
    )
    assert result == {"foo": {"from": "default"}}


def test_items2dict_missing_key_raises(filter_module: FilterModule) -> None:
    """Missing key candidates should raise an error."""
    with pytest.raises(AnsibleFilterError):
        filter_module.items2dict_filter(
            [{"value": 1}],
            key_name="key",
            value_name="value",
        )


def test_items2dict_combine_requires_dict_values(
    filter_module: FilterModule,
) -> None:
    """Combine strategy should ensure values are dictionaries."""
    items = [
        {"key": "foo", "value": 1},
        {"key": "foo", "value": 2},
    ]
    with pytest.raises(AnsibleFilterError, match="requires dict values"):
        filter_module.items2dict_filter(items, collision="combine")
