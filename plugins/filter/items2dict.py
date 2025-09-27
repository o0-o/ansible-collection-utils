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

"""Filter exposing the items2dict helper."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.o0_o.utils.plugins.module_utils import (
    items2dict as items2dict_helper,
)

DOCUMENTATION = r"""
---
name: items2dict
short_description: Convert list of mapping entries to a dictionary
version_added: "1.5.0"
description:
  - Generalisation of C(ansible.builtin.items2dict) that allows custom
    key/value field names, full-record values, and collision strategies.
  - Supports optional deep merges via C(collision=combine) using the
    C(combine) filter with its standard arguments.
options:
  _input:
    description:
      - List of dictionaries to convert.
    type: list
    elements: dict
    required: true
  key_name:
    description:
      - Field name that provides the resulting dictionary key.
      - Accepts a list of field names; the first match found will be used.
    type: str
    default: key
  value_name:
    description:
      - Field name containing the resulting dictionary value.
      - Set to C(null) to keep the entire mapping (minus the C(key_name)
        field) as the value.
    type: str
    default: value
  collision:
    description:
      - Behaviour when duplicate keys are encountered.
      - C(fail) raises an error (default, matching
        C(ansible.builtin.items2dict)).
      - C(list) aggregates duplicate entries into a list.
      - C(combine) deep-merges duplicate dictionaries via the
        C(combine) filter.
    type: str
    default: fail
    choices: [fail, list, combine]
  reverse_combine_order:
    description:
      - When C(collision=combine), merge newer entries before earlier
        ones. Values from earlier entries win if conflicts arise.
    type: bool
    default: false
  combine_args:
    description:
      - Additional keyword arguments forwarded to the underlying
        C(combine) filter when C(collision=combine).
      - Keys mirror the arguments supported by C(combine) such as
        C(recursive) or C(list_merge).
    type: dict
    default: {}
  default_value:
    description:
      - Value to use when the selected value field is missing or empty
        (subject to C(allow_empty)).
    type: raw
    default: null
  allow_empty:
    description:
      - When C(false), treat empty dictionaries as missing values and
        substitute C(default_value).
    type: bool
    default: true
  skip_missing_key:
    description:
      - When C(true), skip items that lack all candidate key fields
        instead of raising an error.
    type: bool
    default: false
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
- name: Match ansible.builtin.items2dict semantics
  ansible.builtin.debug:
    msg: "{{ [{'key': 'foo', 'value': 1}] | o0_o.utils.items2dict }}"
  # -> {'foo': 1}

- name: Use alternate key candidates and keep whole records as values
  vars:
    items: [
      {'name': 'foo', 'description': 'bar'},
      {'identifier': 'baz', 'description': ''},
    ]
  ansible.builtin.debug:
    msg: >-
      {{ items
         | o0_o.utils.items2dict(
             key_name=['name', 'identifier'],
             value_name=None
         ) }}
  # -> {'foo': {'description': 'bar'}, 'baz': {'description': ''}}

- name: Collect duplicates into a list
  ansible.builtin.debug:
    msg: >-
      {{ [
           {'name': 'foo', 'description': 'bar'},
           {'name': 'foo', 'description': 'baz'}
         ]
         | o0_o.utils.items2dict(
             key_name='name',
             value_name=None,
             collision='list'
         ) }}
  # -> {'foo': [{'description': 'bar'}, {'description': 'baz'}]}
"""

RETURN = r"""
_value:
  description: Resulting dictionary keyed by the specified field.
  type: dict
  returned: always
"""


class FilterModule:
    """Ansible filter exposing the items2dict helper."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters."""
        return {"items2dict": self.items2dict_filter}

    def items2dict_filter(
        self,
        items: Iterable[Dict[str, Any]],
        key_name: Any = "key",
        value_name: Optional[str] = "value",
        collision: str = "fail",
        reverse_combine_order: bool = False,
        combine_args: Optional[Dict[str, Any]] = None,
        default_value: Any = None,
        allow_empty: bool = True,
        skip_missing_key: bool = False,
    ) -> Dict[Any, Any]:
        """Delegate to the shared helper with error wrapping."""
        try:
            return items2dict_helper(
                items,
                key_name=key_name,
                value_name=value_name,
                collision=collision,
                reverse_combine_order=reverse_combine_order,
                combine_args=combine_args,
                default_value=default_value,
                allow_empty=allow_empty,
                skip_missing_key=skip_missing_key,
            )
        except AnsibleFilterError:
            raise
        except Exception as exc:  # pragma: no cover - defensive guard
            raise AnsibleFilterError(
                "items2dict failed: "
                f"{exc.__class__.__name__}: {to_native(exc)}"
            ) from exc
