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

"""Ensure value is a list filter."""

from __future__ import annotations

from typing import Any, Dict

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.o0_o.utils.plugins.module_utils.typeguard_compat import (  # noqa: E501
    typechecked,
)

from ansible_collections.o0_o.utils.plugins.module_utils import wantlist


DOCUMENTATION = r"""
---
name: wantlist
short_description: Ensure value is a list or simplify lists
version_added: "1.3.0"
description:
  - When C(want_list=true), wrap values into a list consistently.
  - When C(want_list=false), reduce to the simplest single value.
  - Handles C(None), strings, dicts and generic iterables.
options:
  _input:
    description:
      - Value to convert or simplify.
    type: raw
    required: true
  want_list:
    description:
      - If true, always return a list. If false, prefer a single value.
    type: bool
    default: true
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
- name: Always return a list
  ansible.builtin.debug:
    msg: "{{ 'item' | o0_o.utils.wantlist }}"  # -> ['item']

- name: Prefer a single value
  ansible.builtin.debug:
    msg: "{{ ['item'] | o0_o.utils.wantlist(false) }}"  # -> 'item'

- name: None handling
  ansible.builtin.debug:
    msg: "{{ None | o0_o.utils.wantlist(false) }}"  # -> None
"""

RETURN = r"""
_value:
  description: Resulting value (list or simplified single value)
  type: raw
  returned: always
"""


class FilterModule:
    """Ansible filter plugin."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters for this plugin.

        Wraps the utility to surface errors as AnsibleFilterError for
        clear reporting in play output.

        :returns Dict[str, Any]: Mapping of filter names to callables
        """
        return {"wantlist": self.wantlist_filter}

    @typechecked
    def wantlist_filter(self, value: Any, want_list: bool = True) -> Any:
        """Proxy to module_utils.wantlist with Ansible error handling.

        :param value: Value to process
        :param bool want_list: If True, always return a list; else
            prefer single values
        :returns: Processed value
        :raises AnsibleFilterError: On unexpected errors
        """
        try:
            return wantlist(value, want_list=want_list)
        except Exception as e:
            raise AnsibleFilterError(
                f"wantlist failed: {e.__class__.__name__}: {to_native(e)}"
            ) from e
