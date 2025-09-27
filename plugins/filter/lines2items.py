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

"""Filter wrapping Python splitlines for Ansible usage."""

from __future__ import annotations

from typing import Any, Dict, List

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native, to_text

DOCUMENTATION = r"""
---
name: lines2items
short_description: Split string input into a list of lines
version_added: "1.5.0"
description:
  - Wraps Python's C(str.splitlines) for use within Ansible playbooks.
  - Uses UTF-8 decoding by default and raises on decoding errors.
options:
  _input:
    description:
      - Text to split into lines.
    type: raw
    required: true
  keepends:
    description:
      - Preserve line endings when splitting.
      - Mirrors the C(keepends) parameter of C(str.splitlines()).
    type: bool
    default: false
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
- name: Split multiline string into list
  ansible.builtin.debug:
    msg: "{{ 'a\\nb' | o0_o.utils.lines2items }}"  # -> ['a', 'b']

- name: Preserve newline characters
  ansible.builtin.debug:
    msg: "{{ 'a\\r\n' | o0_o.utils.lines2items(true) }}"  # -> ['a\r\n']
"""

RETURN = r"""
_value:
  description: List of lines derived from the input string.
  type: list
  elements: str
  returned: always
"""


class FilterModule:
    """Ansible filter exposing splitlines."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters."""
        return {"lines2items": self.lines2items_filter}

    def lines2items_filter(
        self, value: Any, keepends: bool = False
    ) -> List[str]:
        """Split text into lines via str.splitlines().

        :param Any value: Value to split into lines.
        :param bool keepends: Preserve newline characters in results.
        :returns List[str]: List of split lines.
        :raises AnsibleFilterError: If the value cannot be converted
            to text.
        """
        try:
            text_value = to_text(value, errors="strict")
        except Exception as exc:  # pragma: no cover - exercised via tests
            raise AnsibleFilterError(
                "lines2items failed: "
                f"{exc.__class__.__name__}: {to_native(exc)}"
            ) from exc
        return text_value.splitlines(keepends)
