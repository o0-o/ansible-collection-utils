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

"""Filter exposing the dict2items helper."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.o0_o.utils.plugins.module_utils import (
    dict2items as dict2items_helper,
)

DOCUMENTATION = r"""
---
name: dict2items
short_description: Convert dictionary to list of item mappings
version_added: "1.5.0"
description:
  - Inverse operation of C(o0_o.utils.items2dict) that supports the same
    field customisation and collision handling semantics.
  - Produces a list of dictionaries using the configured key/value field
    names so that applying C(items2dict) with matching options restores
    the original mapping.
options:
  _input:
    description:
      - Dictionary to convert.
    type: dict
    required: true
  key_name:
    description:
      - Field name assigned the dictionary key in each resulting item.
      - Accepts a list of field names; the first available entry will be
        used.
    type: str
    default: key
  value_name:
    description:
      - Field name assigned the dictionary value in each resulting item.
      - Set to C(null) to merge the value mapping into each item while
        preserving the configured key field.
    type: str
    default: value
  collision:
    description:
      - Behaviour for dictionary entries that represent aggregated
        values produced by C(items2dict).
      - C(fail) treats each mapping entry as a single item (default).
      - C(list) expands list values into multiple items for the same key.
      - C(combine) produces a single item (suitable for values created by
        C(collision=combine)).
    type: str
    default: fail
    choices: [fail, list, combine]
  default_value:
    description:
      - Value to use when a mapping value is missing or considered empty
        (subject to C(allow_empty)).
    type: raw
    default: null
  allow_empty:
    description:
      - When C(false), treat empty dictionaries as missing values and
        use C(default_value) instead.
    type: bool
    default: true
  skip_missing_key:
    description:
      - When C(true), skip entries that cannot be assigned to any of the
        key candidates instead of raising an error.
    type: bool
    default: false
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
- name: Convert dictionary to default key/value items
  ansible.builtin.debug:
    msg: "{{ {'foo': 1, 'bar': 2} | o0_o.utils.dict2items }}"
  # -> [{'key': 'foo', 'value': 1}, {'key': 'bar', 'value': 2}]

- name: Reconstruct entries created with value_name=None
  vars:
    mapping: {
      foo: {description: 'bar'},
      baz: {description: ''}
    }
  ansible.builtin.debug:
    msg: >-
      {{ mapping
         | o0_o.utils.dict2items(
             key_name=['name', 'identifier'],
             value_name=None
         ) }}
  # -> [{'name': 'foo', 'description': 'bar'},
  #     {'name': 'baz', 'description': ''}]

- name: Expand list collisions back into individual items
  vars:
    mapping: {
      foo: [
        {description: 'bar'},
        {description: 'baz'}
      ]
    }
  ansible.builtin.debug:
    msg: >-
      {{ mapping
         | o0_o.utils.dict2items(
             key_name='name',
             value_name=None,
             collision='list'
         ) }}
  # -> [{'name': 'foo', 'description': 'bar'},
  #     {'name': 'foo', 'description': 'baz'}]
"""

RETURN = r"""
_value:
  description: List of items compatible with o0_o.utils.items2dict.
  type: list
  elements: dict
  returned: always
"""


class FilterModule:
    """Ansible filter exposing the dict2items helper."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters."""
        return {"dict2items": self.dict2items_filter}

    def dict2items_filter(
        self,
        mapping: Dict[Any, Any],
        key_name: Any = "key",
        value_name: Optional[str] = "value",
        collision: str = "fail",
        default_value: Any = None,
        allow_empty: bool = True,
        skip_missing_key: bool = False,
    ) -> List[Dict[str, Any]]:
        """Delegate to the shared helper with error wrapping."""
        try:
            return dict2items_helper(
                mapping,
                key_name=key_name,
                value_name=value_name,
                collision=collision,
                default_value=default_value,
                allow_empty=allow_empty,
                skip_missing_key=skip_missing_key,
            )
        except AnsibleFilterError:
            raise
        except Exception as exc:  # pragma: no cover - defensive guard
            raise AnsibleFilterError(
                "dict2items failed: "
                f"{exc.__class__.__name__}: {to_native(exc)}"
            ) from exc
