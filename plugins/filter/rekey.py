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

"""Filter exposing the rekey helper."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.o0_o.utils.plugins.module_utils.typeguard_compat import (  # noqa: E501
    typechecked,
)

from ansible_collections.o0_o.utils.plugins.module_utils import (
    rekey as rekey_helper,
)

DOCUMENTATION = r"""
---
name: rekey
short_description: Change dictionary keys to values of nested fields
version_added: "1.5.0"
description:
  - >-
    Convenience wrapper around C(dict2items) followed by C(items2dict)
    allowing dictionaries to be re-keyed without manual intermediate
    conversions.
options:
  _input:
    description:
      - Dictionary whose keys should be replaced.
    type: dict
    required: true
  key_name:
    description:
      - Field name used to determine the new key.
      - >-
        Accepts a list of field names; the first available entry will be
        used.
    type: str
    required: true
  store_key_as:
    description:
      - >-
        Optional field name (or list of field names) to store the
        original key inside each value.
    type: str
  collision:
    description:
      - Behaviour when duplicate keys are encountered.
      - >-
        Matches the behaviour of C(items2dict): C(fail), C(list), or
        C(combine).
    type: str
    default: fail
    choices: [fail, list, combine]
  reverse_combine_order:
    description:
      - >-
        When C(collision=combine), merge newer entries before earlier
        ones.
    type: bool
    default: false
  combine_args:
    description:
      - >-
        Additional keyword arguments forwarded to the underlying
        C(combine) filter when C(collision=combine).
    type: dict
    default: {}
  default_value:
    description:
      - >-
        Value to use when the selected value field is missing or empty
        (subject to C(allow_empty)).
    type: raw
    default: null
  allow_empty:
    description:
      - >-
        When C(false), treat empty dictionaries as missing values and
        substitute C(default_value).
    type: bool
    default: true
  skip_missing_key:
    description:
      - >-
        When C(true), skip entries that cannot determine a new key
        instead of raising an error.
    type: bool
    default: false
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
# Given this data structure:
# users:
#   '1000':
#     name: o0-o
#     home: /home/o0-o
#   '1001':
#     name: foo
#     home: /home/foo

- name: Re-key users by their name
  ansible.builtin.set_fact:
    users_by_name: >-
      {{ users
         | o0_o.utils.rekey(
             key_name='name',
             store_key_as='id'
         ) }}
  # Result:
  # {'o0-o': {'home': '/home/o0-o', 'id': '1000'},
  #  'foo': {'home': '/home/foo', 'id': '1001'}}
"""

RETURN = r"""
_value:
  description: Re-keyed dictionary.
  type: dict
  returned: always
"""


class FilterModule:
    """Ansible filter exposing rekey."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters."""
        return {"rekey": self.rekey_filter}

    @typechecked
    def rekey_filter(
        self,
        mapping: Dict[Any, Any],
        key_name: Any,
        store_key_as: Optional[Any] = None,
        collision: str = "fail",
        reverse_combine_order: bool = False,
        combine_args: Optional[Dict[str, Any]] = None,
        default_value: Any = None,
        allow_empty: bool = True,
        skip_missing_key: bool = False,
    ) -> Dict[str, Any]:
        """Delegate to the shared rekey helper."""
        try:
            return rekey_helper(
                mapping,
                key_name=key_name,
                store_key_as=store_key_as,
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
                "rekey failed: " f"{exc.__class__.__name__}: {to_native(exc)}"
            ) from exc
