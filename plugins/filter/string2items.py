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

"""Convert delimited string to list filter."""

from __future__ import annotations

from typing import Any, Dict, List

from ansible.errors import AnsibleFilterError
from ansible_collections.o0_o.utils.plugins.module_utils.list_utils import (
    string2items as _string2items,
)


DOCUMENTATION = r"""
---
name: string2items
short_description: Convert a delimited string into a list of items
version_added: "1.3.0"
description:
  - Splits input into a list using a delimiter.
  - Can optionally trim whitespace and drop empty items.
  - Non-string inputs are cast to strings when possible.
options:
  _input:
    description:
      - The value to split into items.
    type: raw
    required: true
  delimiter:
    description:
      - Delimiter to split on.
    type: str
    default: ','
  trim:
    description:
      - If true, strip whitespace and drop empty items.
    type: bool
    default: true
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
- name: Parse comma-separated string
  ansible.builtin.debug:
    msg: "{{ 'foo,bar,baz' | o0_o.utils.string2items }}"

- name: Custom delimiter and keep whitespace
  ansible.builtin.debug:
    msg: >-
      {{ 'foo, bar , baz' | o0_o.utils.string2items(',', false) }}

- name: Non-string input gets cast to string
  ansible.builtin.debug:
    msg: "{{ 42 | o0_o.utils.string2items }}"
"""

RETURN = r"""
_value:
  description: List of parsed items
  type: list
  returned: always
  sample: [foo, bar, baz]
"""


class FilterModule:
    """Ansible filter plugin."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters for this plugin.

        :returns Dict[str, Any]: Mapping of filter names to callables
        """
        return {"string2items": self.string2items}

    def string2items(
        self, value: Any, delimiter: str = ",", trim: bool = True
    ) -> List[str]:
        """Split a delimited string into a list of items.

        :param value: Input value; will be cast to ``str`` when possible
        :param delimiter: Delimiter to split on (default: ",")
        :param trim: Strip whitespace; drop empty items when True
        :returns List[str]: List of items
        :raises AnsibleFilterError: When input is not string-castable
        """
        try:
            return _string2items(value, delimiter=delimiter, trim=trim)
        except Exception as e:
            raise AnsibleFilterError(str(e))
