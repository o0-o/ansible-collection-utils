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

"""Filter exposing truthy or integer conversion helper."""

from __future__ import annotations

from typing import Any, Dict, Union

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.o0_o.utils.plugins.module_utils.typeguard_compat import (  # noqa: E501
    typechecked,
)

from ansible_collections.o0_o.utils.plugins.module_utils import (
    truthy_or_integer,
)

DOCUMENTATION = r"""
---
name: truthy_or_integer
short_description: Interpret input as integer or boolean
version_added: "1.5.0"
description:
  - Prefer integer output when the input represents an integer literal.
  - Fall back to Ansible's boolean helper with ``strict=false`` to
    process other truthy representations.
options:
  _input:
    description:
      - Value to interpret as integer or boolean.
    type: raw
    required: true
  zero_is_false:
    description:
      - Return ``false`` instead of ``0`` when the value is zero.
    type: bool
    default: false
  only_positive:
    description:
      - Reject negative integers and zero (unless ``zero_is_false``
        converts it to ``false``).
    type: bool
    default: false
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
- name: Convert string integers to native ints
  ansible.builtin.debug:
    msg: "{{ '2' | o0_o.utils.truthy_or_integer }}"  # -> 2

- name: Interpret classic boolean strings
  ansible.builtin.debug:
    msg: "{{ 'yes' | o0_o.utils.truthy_or_integer }}"  # -> True

- name: Treat zero as false when requested
  ansible.builtin.debug:
    msg: "{{ '0' | o0_o.utils.truthy_or_integer(zero_is_false=true) }}"
    # -> False

- name: Enforce positive integers only
  ansible.builtin.debug:
    msg: "{{ 3 | o0_o.utils.truthy_or_integer(only_positive=true) }}"  # -> 3
"""

RETURN = r"""
_value:
  description: Integer or boolean result after interpretation.
  type: raw
  returned: always
"""


class FilterModule:
    """Ansible filter plugin for truthy or integer conversion."""

    def filters(self) -> Dict[str, Any]:
        """Expose filter names for Ansible."""
        return {"truthy_or_integer": self.truthy_or_integer_filter}

    @typechecked
    def truthy_or_integer_filter(
        self,
        value: Any,
        zero_is_false: bool = False,
        only_positive: bool = False,
    ) -> Union[bool, int]:
        """Convert value to integer or boolean with helper semantics.

        :param Any value: Input to interpret.
        :param bool zero_is_false: Return ``False`` instead of ``0``
            when the value resolves to zero.
        :param bool only_positive: Reject negative integers when true.
        :returns Union[bool, int]: Normalised integer or boolean value.
        :raises AnsibleFilterError: If the value cannot be interpreted.
        """
        try:
            return truthy_or_integer(
                value,
                zero_is_false=zero_is_false,
                only_positive=only_positive,
            )
        except ValueError as exc:
            raise AnsibleFilterError(
                "truthy_or_integer failed: "
                f"{exc.__class__.__name__}: {to_native(exc)}"
            ) from exc
