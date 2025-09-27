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

"""Unit tests for the dict2items filter."""

from __future__ import annotations

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.filter.dict2items import (
    FilterModule,
)


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter module instance per test."""
    return FilterModule()


def test_dict2items_defaults(filter_module: FilterModule) -> None:
    """Default conversion should mirror ansible.builtin.dict2items."""
    mapping = {"foo": 1, "bar": 2}
    result = filter_module.dict2items_filter(mapping)
    assert result == [
        {"key": "foo", "value": 1},
        {"key": "bar", "value": 2},
    ]


def test_dict2items_value_name_none(filter_module: FilterModule) -> None:
    """When value_name is None merge mapping values into items."""
    mapping = {
        "foo": {"description": "bar"},
        "baz": {"description": ""},
    }
    result = filter_module.dict2items_filter(
        mapping, key_name="name", value_name=None
    )
    assert result == [
        {"name": "foo", "description": "bar"},
        {"name": "baz", "description": ""},
    ]


def test_dict2items_key_name_candidates(filter_module: FilterModule) -> None:
    """Key candidates should select the first applicable entry."""
    mapping = {"foo": {"description": "bar"}}
    result = filter_module.dict2items_filter(
        mapping,
        key_name=["name", "identifier"],
        value_name=None,
    )
    assert result == [{"name": "foo", "description": "bar"}]


def test_dict2items_collision_list(filter_module: FilterModule) -> None:
    """List collision should expand list values into multiple items."""
    mapping = {
        "foo": [
            {"description": "bar"},
            {"description": "baz"},
        ]
    }
    result = filter_module.dict2items_filter(
        mapping,
        key_name="name",
        value_name=None,
        collision="list",
    )
    assert result == [
        {"name": "foo", "description": "bar"},
        {"name": "foo", "description": "baz"},
    ]


def test_dict2items_collision_list_value_field(
    filter_module: FilterModule,
) -> None:
    """List collision should work when value_name is provided."""
    mapping = {"foo": [1, 2, 3]}
    result = filter_module.dict2items_filter(
        mapping,
        key_name="name",
        value_name="number",
        collision="list",
    )
    assert result == [
        {"name": "foo", "number": 1},
        {"name": "foo", "number": 2},
        {"name": "foo", "number": 3},
    ]


def test_dict2items_invalid_list_value(filter_module: FilterModule) -> None:
    """List collision requires list values."""
    mapping = {"foo": "not-a-list"}
    with pytest.raises(AnsibleFilterError, match="collision='list'"):
        filter_module.dict2items_filter(mapping, collision="list")


def test_dict2items_value_name_none_requires_dict(
    filter_module: FilterModule,
) -> None:
    """value_name None requires mapping values to be dictionaries."""
    mapping = {"foo": "bar"}
    with pytest.raises(AnsibleFilterError, match="dict values"):
        filter_module.dict2items_filter(mapping, value_name=None)


def test_dict2items_skip_missing_key(filter_module: FilterModule) -> None:
    """Entries with invalid structures can be skipped."""
    mapping = {
        "foo": "bar",
        "baz": {"description": "ok"},
    }
    result = filter_module.dict2items_filter(
        mapping,
        value_name=None,
        skip_missing_key=True,
    )
    assert result == [{"key": "baz", "description": "ok"}]


def test_dict2items_default_value(filter_module: FilterModule) -> None:
    """Default value should apply when values are missing."""
    mapping = {"foo": None}
    result = filter_module.dict2items_filter(
        mapping,
        default_value="fallback",
    )
    assert result == [{"key": "foo", "value": "fallback"}]


def test_dict2items_default_value_allow_empty(
    filter_module: FilterModule,
) -> None:
    """Empty dicts honour allow_empty toggle."""
    mapping = {"foo": {}}
    result = filter_module.dict2items_filter(
        mapping,
        value_name=None,
        allow_empty=False,
        default_value={"description": "default"},
    )
    assert result == [{"key": "foo", "description": "default"}]


def test_dict2items_round_trip_list_collision(
    filter_module: FilterModule,
) -> None:
    """Round-trip list collision results through items2dict."""
    mapping = {
        "foo": [
            {"description": "bar"},
            {"description": "baz"},
        ]
    }
    list_result = filter_module.dict2items_filter(
        mapping,
        key_name="name",
        value_name=None,
        collision="list",
    )
    from ansible_collections.o0_o.utils.plugins.filter.items2dict import (
        FilterModule as Items2Dict,
    )

    items_filter = Items2Dict()
    rebuilt = items_filter.items2dict_filter(
        list_result,
        key_name="name",
        value_name=None,
        collision="list",
    )
    assert rebuilt == mapping
