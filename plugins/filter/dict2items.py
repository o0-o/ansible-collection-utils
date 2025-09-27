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

"""Filter converting dicts into lists with collision control."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from ansible.errors import AnsibleFilterError

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
             key_name='name',
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


VALID_COLLISIONS = {"fail", "list", "combine"}


class FilterModule:
    """Ansible filter plugin implementing dict2items."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters."""
        return {"dict2items": self.dict2items_filter}

    def dict2items_filter(
        self,
        mapping: Dict[Any, Any],
        key_name: str = "key",
        value_name: Optional[str] = "value",
        collision: str = "fail",
    ) -> List[Dict[str, Any]]:
        """Convert dictionaries into list representations.

        :param Dict[Any, Any] mapping: Mapping to convert.
        :param str key_name: Field name for each item's key value.
        :param Optional[str] value_name: Field name for the value, or
            C(None) to inline mapping values.
        :param str collision: Strategy for aggregated values.
        :returns List[Dict[str, Any]]: List of item dictionaries.
        :raises AnsibleFilterError: On invalid input or configuration.
        """
        if not isinstance(mapping, dict):
            raise AnsibleFilterError("dict2items requires a dictionary input")
        if not isinstance(key_name, str) or not key_name:
            raise AnsibleFilterError(
                "dict2items requires a non-empty string key_name"
            )
        if value_name is not None and not isinstance(value_name, str):
            raise AnsibleFilterError(
                "dict2items 'value_name' parameter must be a string or None"
            )

        collision_mode = (collision or "").lower()
        if collision_mode not in VALID_COLLISIONS:
            raise AnsibleFilterError(
                "dict2items collision must be one of "
                "'fail', 'list', or 'combine'"
            )

        items: List[Dict[str, Any]] = []
        for key, value in mapping.items():
            if collision_mode == "list":
                items.extend(
                    self._expand_list_value(key, value, key_name, value_name)
                )
                continue

            items.append(
                self._make_item(
                    key=key,
                    value=value,
                    key_name=key_name,
                    value_name=value_name,
                    require_mapping=value_name is None,
                )
            )

        return items

    @staticmethod
    def _make_item(
        key: Any,
        value: Any,
        *,
        key_name: str,
        value_name: Optional[str],
        require_mapping: bool,
    ) -> Dict[str, Any]:
        """Construct a single output item."""
        if value_name is None:
            if not isinstance(value, dict):
                raise AnsibleFilterError(
                    "dict2items requires dict values when value_name is None"
                )
            item = value.copy()
            if key_name in item:
                raise AnsibleFilterError(
                    f"dict2items value already contains '{key_name}' field"
                )
            item[key_name] = key
            return item

        return {key_name: key, value_name: value}

    def _expand_list_value(
        self,
        key: Any,
        value: Any,
        key_name: str,
        value_name: Optional[str],
    ) -> Iterable[Dict[str, Any]]:
        """Expand list values into multiple items."""
        if not isinstance(value, list):
            raise AnsibleFilterError(
                "dict2items collision='list' expects list values"
            )

        expanded: List[Dict[str, Any]] = []
        for index, element in enumerate(value):
            try:
                item = self._make_item(
                    key=key,
                    value=element,
                    key_name=key_name,
                    value_name=value_name,
                    require_mapping=value_name is None,
                )
            except AnsibleFilterError as exc:
                raise AnsibleFilterError(
                    f"dict2items list element {index}: {exc}"
                ) from exc
            expanded.append(item)
        return expanded
