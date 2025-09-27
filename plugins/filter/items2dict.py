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

"""Filter providing a flexible items2dict implementation."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native

try:
    from ansible.plugins.filter.core import combine
except ImportError as exc:  # pragma: no cover - defensive guard
    raise AnsibleFilterError(
        "items2dict requires the core combine filter: " f"{to_native(exc)}"
    )

from ansible_collections.o0_o.utils.plugins.module_utils import wantlist


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

- name: Use an alternate key field and keep whole records as values
  vars:
    items: [
      {'name': 'foo', 'description': 'bar'},
      {'name': 'baz', 'description': ''},
    ]
  ansible.builtin.debug:
    msg: >-
      {{ items
         | o0_o.utils.items2dict(
             key_name='name',
             value_name=None
         ) }}
  # -> {'foo': {'description': 'bar'}, 'baz': {'description': ''}}

- name: Collect duplicates into a list
  ansible.builtin.debug:
    msg: |
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

- name: Merge duplicates with combine options
  ansible.builtin.debug:
    msg: |
      {{ [
           {'name': 'foo', 'options': {'a': 1}},
           {'name': 'foo', 'options': {'b': 2}}
         ]
         | o0_o.utils.items2dict(
             key_name='name',
             value_name='options',
        collision='combine',
        combine_args={'recursive': True}
         ) }}
  # -> {'foo': {'a': 1, 'b': 2}}
"""

RETURN = r"""
_value:
  description: Resulting dictionary keyed by the specified field.
  type: dict
  returned: always
"""


VALID_COLLISIONS = {"fail", "list", "combine"}


class FilterModule:
    """Ansible filter plugin implementing items2dict."""

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
        """Convert list of dictionaries into a dictionary.

        :param Iterable[Dict[str, Any]] items: Items to convert.
        :param Any key_name: Field providing each resulting dictionary
            key.
        :param Optional[str] value_name: Field providing values or
            C(None) to use the full mapping minus the key field.
        :param str collision: Strategy for duplicate keys.
        :param bool reverse_combine_order: Reverse order for merge
            strategy.
        :param Optional[Dict[str, Any]] combine_args: Arguments
            forwarded to the combine filter when merging duplicates.
        :param Any default_value: Fallback value when value field is
            missing or empty.
        :param bool allow_empty: Whether empty dictionaries are treated
            as valid values.
        :param bool skip_missing_key: Skip items missing key fields if
            true, otherwise raise an error.
        :returns Dict[Any, Any]: Constructed dictionary.
        :raises AnsibleFilterError: On invalid input or collisions.
        """
        key_candidates = wantlist(key_name, want_list=True)
        if not key_candidates:
            raise AnsibleFilterError(
                "items2dict requires at least one key_name candidate"
            )
        for candidate in key_candidates:
            if not isinstance(candidate, str) or not candidate:
                raise AnsibleFilterError(
                    "items2dict key_name entries must be non-empty strings"
                )
        if value_name is not None and not isinstance(value_name, str):
            raise AnsibleFilterError(
                "items2dict 'value_name' parameter must be a string or None"
            )

        collision_mode = (collision or "").lower()
        if collision_mode not in VALID_COLLISIONS:
            raise AnsibleFilterError(
                "items2dict collision must be one of 'fail', 'list', "
                "or 'combine'"
            )
        if reverse_combine_order and collision_mode != "combine":
            raise AnsibleFilterError(
                "items2dict reverse_combine_order is only valid when "
                "collision='combine'"
            )

        combine_kwargs = dict(combine_args or {})

        result: Dict[Any, Any] = {}
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise AnsibleFilterError(
                    "items2dict expects dictionaries; "
                    f"item {index} is {type(item).__name__}"
                )
            key_field = None
            for candidate in key_candidates:
                if candidate in item:
                    key_field = candidate
                    break
            if key_field is None:
                if skip_missing_key:
                    continue
                candidates_display = ", ".join(key_candidates)
                raise AnsibleFilterError(
                    f"items2dict element {index} missing key candidates: "
                    f"{candidates_display}"
                )
            key_value = item[key_field]

            if value_name is None:
                value_payload = {
                    field: value
                    for field, value in item.items()
                    if field != key_field
                }
                if (
                    not allow_empty
                    and isinstance(value_payload, dict)
                    and not value_payload
                ):
                    value_payload = default_value
                if value_payload is None and default_value is not None:
                    value_payload = default_value
                if (
                    isinstance(value_payload, dict)
                    and value_payload is default_value
                ):
                    value_payload = value_payload.copy()
            else:
                value_missing = value_name not in item
                if not value_missing:
                    candidate_value = item[value_name]
                    if (
                        not allow_empty
                        and isinstance(candidate_value, dict)
                        and not candidate_value
                    ):
                        value_missing = True
                value_payload = (
                    default_value if value_missing else item[value_name]
                )
                if (
                    isinstance(value_payload, dict)
                    and value_payload is default_value
                ):
                    value_payload = value_payload.copy()

            if collision_mode == "fail":
                if key_value in result:
                    raise AnsibleFilterError(
                        f"items2dict duplicate key '{key_value}' encountered"
                    )
                result[key_value] = value_payload
                continue

            if collision_mode == "list":
                existing_list = result.setdefault(key_value, [])
                if not isinstance(existing_list, list):
                    result[key_value] = existing_list = [existing_list]
                existing_list.append(value_payload)
                continue

            # combine path
            if not isinstance(value_payload, dict):
                raise AnsibleFilterError(
                    "items2dict requires dict values when collision='combine'"
                )
            if key_value not in result:
                result[key_value] = value_payload
                continue

            existing_value = result[key_value]
            if not isinstance(existing_value, dict):
                raise AnsibleFilterError(
                    "items2dict existing value is not a dict; cannot merge"
                )
            if reverse_combine_order:
                merged = combine(
                    value_payload, existing_value, **combine_kwargs
                )
            else:
                merged = combine(
                    existing_value, value_payload, **combine_kwargs
                )
            result[key_value] = merged

        return result
