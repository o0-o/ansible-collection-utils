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

"""Unit tests for merge_hash function.

Test cases adapted from Ansible core test suite:
https://github.com/ansible/ansible/blob/devel/test/units/utils/test_vars.py

Original tests copyright:
    (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
    (c) 2015, Toshio Kuraotmi <tkuratomi@ansible.com>
    GNU General Public License v3.0+
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import pytest

from ansible_collections.o0_o.utils.plugins.module_utils.dict_utils import (
    merge_hash,
)


# Test data adapted from Ansible's TestVariableUtils
COMBINE_VARS_MERGE_DATA = (
    {
        "a": {"a": 1},
        "b": {"b": 2},
        "result": {"a": 1, "b": 2},
    },
    {
        "a": {"a": 1, "c": {"foo": "bar"}},
        "b": {"b": 2, "c": {"baz": "bam"}},
        "result": {"a": 1, "b": 2, "c": {"foo": "bar", "baz": "bam"}},
    },
    {
        "a": defaultdict(None, {"a": 1, "c": defaultdict(None, {"foo": "bar"})}),
        "b": {"b": 2, "c": {"baz": "bam"}},
        "result": defaultdict(
            None, {"a": 1, "b": 2, "c": defaultdict(None, {"foo": "bar", "baz": "bam"})}
        ),
    },
)

MERGE_HASH_DATA: dict[str, Any] = {
    "low_prio": {
        "a": {"a'": {"x": "low_value", "y": "low_value", "list": ["low_value"]}},
        "b": [1, 1, 2, 3],
    },
    "high_prio": {
        "a": {"a'": {"y": "high_value", "z": "high_value", "list": ["high_value"]}},
        "b": [3, 4, 4, {"5": "value"}],
    },
}


@pytest.mark.parametrize("test_data", COMBINE_VARS_MERGE_DATA)
def test_merge_hash_basic(test_data: dict[str, Any]) -> None:
    """Test basic merge_hash behavior matches combine_vars merge mode."""
    assert merge_hash(test_data["a"], test_data["b"]) == test_data["result"]


def test_merge_hash_simple() -> None:
    """Test merge_hash with nested structures."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {
        "a": {
            "a'": {
                "x": "low_value",
                "y": "high_value",
                "z": "high_value",
                "list": ["high_value"],
            }
        },
        "b": high["b"],
    }
    assert merge_hash(low, high) == expected


def test_merge_hash_non_recursive_list_replace() -> None:
    """Test non-recursive merge with list_merge='replace'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = high
    assert merge_hash(low, high, recursive=False, list_merge="replace") == expected


def test_merge_hash_non_recursive_list_keep() -> None:
    """Test non-recursive merge with list_merge='keep'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {"a": high["a"], "b": low["b"]}
    assert merge_hash(low, high, recursive=False, list_merge="keep") == expected


def test_merge_hash_non_recursive_list_append() -> None:
    """Test non-recursive merge with list_merge='append'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {"a": high["a"], "b": low["b"] + high["b"]}
    assert merge_hash(low, high, recursive=False, list_merge="append") == expected


def test_merge_hash_non_recursive_list_prepend() -> None:
    """Test non-recursive merge with list_merge='prepend'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {"a": high["a"], "b": high["b"] + low["b"]}
    assert merge_hash(low, high, recursive=False, list_merge="prepend") == expected


def test_merge_hash_non_recursive_list_append_rp() -> None:
    """Test non-recursive merge with list_merge='append_rp'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {"a": high["a"], "b": [1, 1, 2] + high["b"]}
    assert merge_hash(low, high, recursive=False, list_merge="append_rp") == expected


def test_merge_hash_non_recursive_list_prepend_rp() -> None:
    """Test non-recursive merge with list_merge='prepend_rp'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {"a": high["a"], "b": high["b"] + [1, 1, 2]}
    assert merge_hash(low, high, recursive=False, list_merge="prepend_rp") == expected


def test_merge_hash_recursive_list_replace() -> None:
    """Test recursive merge with list_merge='replace'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {
        "a": {
            "a'": {
                "x": "low_value",
                "y": "high_value",
                "z": "high_value",
                "list": ["high_value"],
            }
        },
        "b": high["b"],
    }
    assert merge_hash(low, high, recursive=True, list_merge="replace") == expected


def test_merge_hash_recursive_list_keep() -> None:
    """Test recursive merge with list_merge='keep'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {
        "a": {
            "a'": {
                "x": "low_value",
                "y": "high_value",
                "z": "high_value",
                "list": ["low_value"],
            }
        },
        "b": low["b"],
    }
    assert merge_hash(low, high, recursive=True, list_merge="keep") == expected


def test_merge_hash_recursive_list_append() -> None:
    """Test recursive merge with list_merge='append'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {
        "a": {
            "a'": {
                "x": "low_value",
                "y": "high_value",
                "z": "high_value",
                "list": ["low_value", "high_value"],
            }
        },
        "b": low["b"] + high["b"],
    }
    assert merge_hash(low, high, recursive=True, list_merge="append") == expected


def test_merge_hash_recursive_list_prepend() -> None:
    """Test recursive merge with list_merge='prepend'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {
        "a": {
            "a'": {
                "x": "low_value",
                "y": "high_value",
                "z": "high_value",
                "list": ["high_value", "low_value"],
            }
        },
        "b": high["b"] + low["b"],
    }
    assert merge_hash(low, high, recursive=True, list_merge="prepend") == expected


def test_merge_hash_recursive_list_append_rp() -> None:
    """Test recursive merge with list_merge='append_rp'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {
        "a": {
            "a'": {
                "x": "low_value",
                "y": "high_value",
                "z": "high_value",
                "list": ["low_value", "high_value"],
            }
        },
        "b": [1, 1, 2] + high["b"],
    }
    assert merge_hash(low, high, recursive=True, list_merge="append_rp") == expected


def test_merge_hash_recursive_list_prepend_rp() -> None:
    """Test recursive merge with list_merge='prepend_rp'."""
    low = MERGE_HASH_DATA["low_prio"]
    high = MERGE_HASH_DATA["high_prio"]
    expected = {
        "a": {
            "a'": {
                "x": "low_value",
                "y": "high_value",
                "z": "high_value",
                "list": ["high_value", "low_value"],
            }
        },
        "b": high["b"] + [1, 1, 2],
    }
    assert merge_hash(low, high, recursive=True, list_merge="prepend_rp") == expected


def test_merge_hash_invalid_list_merge() -> None:
    """Test that invalid list_merge raises ValueError."""
    with pytest.raises(ValueError, match="list_merge"):
        merge_hash({}, {}, list_merge="invalid")


def test_merge_hash_non_dict_raises_error() -> None:
    """Test that non-dict arguments raise an error.

    Note: When typeguard is installed, it raises TypeCheckError before
    our validation runs. When typeguard is not installed, our
    _validate_mutable_mappings raises TypeError.
    """
    with pytest.raises((TypeError, Exception)):
        merge_hash([1, 2, 3], {"a": 1})  # type: ignore[arg-type]
    with pytest.raises((TypeError, Exception)):
        merge_hash({"a": 1}, [1, 2, 3])  # type: ignore[arg-type]


def test_merge_hash_empty_dicts() -> None:
    """Test merge_hash fast paths with empty dicts."""
    assert merge_hash({}, {"a": 1}) == {"a": 1}
    assert merge_hash({"a": 1}, {}) == {"a": 1}
    assert merge_hash({}, {}) == {}


def test_merge_hash_does_not_modify_inputs() -> None:
    """Test that merge_hash does not modify input dictionaries."""
    x = {"a": {"b": 1}}
    y = {"a": {"c": 2}}
    x_copy = {"a": {"b": 1}}
    y_copy = {"a": {"c": 2}}

    merge_hash(x, y)

    assert x == x_copy
    assert y == y_copy
