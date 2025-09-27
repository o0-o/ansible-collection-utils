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
from ansible_collections.o0_o.utils.plugins.module_utils import wantlist

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
        key_name: Any = "key",
        value_name: Optional[str] = "value",
        collision: str = "fail",
        default_value: Any = None,
        allow_empty: bool = True,
        skip_missing_key: bool = False,
    ) -> List[Dict[str, Any]]:
        """Convert dictionaries into list representations.

        :param Dict[Any, Any] mapping: Mapping to convert.
        :param Any key_name: Field name(s) for each item's key value.
        :param Optional[str] value_name: Field name for the value, or
            C(None) to inline mapping values.
        :param str collision: Strategy for aggregated values.
        :param Any default_value: Fallback when mapping values are
            missing or empty.
        :param bool allow_empty: Whether empty dictionaries are treated
            as valid values.
        :param bool skip_missing_key: Skip entries lacking key fields if
            true.
        :returns List[Dict[str, Any]]: List of item dictionaries.
        :raises AnsibleFilterError: On invalid input or configuration.
        """
        if not isinstance(mapping, dict):
            raise AnsibleFilterError("dict2items requires a dictionary input")

        key_candidates = wantlist(key_name, want_list=True)
        if not key_candidates:
            raise AnsibleFilterError(
                "dict2items requires at least one key_name candidate"
            )
        for candidate in key_candidates:
            if not isinstance(candidate, str) or not candidate:
                raise AnsibleFilterError(
                    "dict2items key_name entries must be non-empty strings"
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
                    self._expand_list_value(
                        key,
                        value,
                        key_candidates,
                        value_name,
                        default_value,
                        allow_empty,
                        skip_missing_key,
                    )
                )
                continue

            item = self._build_single_item(
                key=key,
                value=value,
                key_candidates=key_candidates,
                value_name=value_name,
                default_value=default_value,
                allow_empty=allow_empty,
                skip_missing_key=skip_missing_key,
            )
            if item is not None:
                items.append(item)

        return items

    @staticmethod
    def _is_empty_mapping(value: Any) -> bool:
        return isinstance(value, dict) and not value

    def _build_single_item(
        self,
        *,
        key: Any,
        value: Any,
        key_candidates: List[str],
        value_name: Optional[str],
        default_value: Any,
        allow_empty: bool,
        skip_missing_key: bool,
    ) -> Optional[Dict[str, Any]]:
        """Construct a single output item or return None to skip."""
        if value_name is None:
            processed_value = value
            if processed_value is None or (
                self._is_empty_mapping(processed_value) and not allow_empty
            ):
                processed_value = default_value
            if processed_value is None:
                if skip_missing_key:
                    return None
            if processed_value is None or not isinstance(
                processed_value, dict
            ):
                if skip_missing_key:
                    return None
                raise AnsibleFilterError(
                    "dict2items requires dict values when value_name is None"
                )

            value_dict = processed_value.copy()
            key_field = self._select_output_key_field(
                key_candidates, value_dict, key, skip_missing_key
            )
            if key_field is None:
                return None
            existing = value_dict.get(key_field)
            if existing not in (None, key):
                if skip_missing_key:
                    return None
                raise AnsibleFilterError(
                    f"dict2items cannot assign key '{key_field}'="
                    f"{key!r}; existing value {existing!r} conflicts"
                )
            value_dict[key_field] = key
            return value_dict

        processed_value = value
        if processed_value is None or (
            self._is_empty_mapping(processed_value) and not allow_empty
        ):
            processed_value = default_value
        if (
            isinstance(processed_value, dict)
            and processed_value is default_value
        ):
            processed_value = processed_value.copy()

        key_field = key_candidates[0]
        return {key_field: key, value_name: processed_value}

    def _expand_list_value(
        self,
        key: Any,
        value: Any,
        key_candidates: List[str],
        value_name: Optional[str],
        default_value: Any,
        allow_empty: bool,
        skip_missing_key: bool,
    ) -> Iterable[Dict[str, Any]]:
        """Expand list values into multiple items."""
        if not isinstance(value, list):
            if skip_missing_key:
                return []
            raise AnsibleFilterError(
                "dict2items collision='list' expects list values"
            )

        expanded: List[Dict[str, Any]] = []
        for index, element in enumerate(value):
            try:
                item = self._build_single_item(
                    key=key,
                    value=element,
                    key_candidates=key_candidates,
                    value_name=value_name,
                    default_value=default_value,
                    allow_empty=allow_empty,
                    skip_missing_key=skip_missing_key,
                )
            except AnsibleFilterError as exc:
                raise AnsibleFilterError(
                    f"dict2items list element {index}: {exc}"
                ) from exc
            if item is not None:
                expanded.append(item)
        return expanded

    @staticmethod
    def _select_output_key_field(
        key_candidates: List[str],
        value_dict: Optional[Dict[str, Any]],
        key: Any,
        skip_missing_key: bool,
    ) -> Optional[str]:
        """Choose the field used to store the key in output items."""
        if value_dict is None:
            return key_candidates[0]

        for candidate in key_candidates:
            if candidate not in value_dict:
                return candidate
        for candidate in key_candidates:
            if value_dict.get(candidate) == key:
                return candidate

        if skip_missing_key:
            return None

        candidates_display = ", ".join(key_candidates)
        raise AnsibleFilterError(
            "dict2items could not determine output key field; "
            f"checked: {candidates_display}"
        )
