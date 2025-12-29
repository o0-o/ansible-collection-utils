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

"""Filter exposing the strip_comments helper."""

from __future__ import annotations

from typing import Any, Dict

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.o0_o.utils.plugins.module_utils import strip_comments

DOCUMENTATION = r"""
---
name: strip_comments
short_description: Remove comments from multiline text
version_added: "1.5.0"
description:
  - Wraps the C(o0_o.utils.strip_comments) helper to make it available as
    an Ansible Jinja2 filter.
  - Strips comments while respecting quoted strings and configurable
    comment styles.
options:
  _input:
    description:
      - Multiline text to process.
    type: str
    required: true
  comment_style:
    description:
      - Comment syntax to remove. Accepts predefined styles such as
        C(python), C(c), C(cpp), and C(slash), or custom pyparsing
        expressions.
    type: raw
    default: python
  strip_blank_lines:
    description:
      - When C(true), remove empty lines remaining after comment removal.
    type: bool
    default: true
notes:
  - Requires the C(pyparsing) Python package.
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
- name: Strip Python style comments
  ansible.builtin.set_fact:
    cleaned: "{{ text | o0_o.utils.strip_comments }}"

- name: Preserve blank lines
  ansible.builtin.set_fact:
    cleaned: >-
      {{ text | o0_o.utils.strip_comments(strip_blank_lines=false) }}

- name: Remove C++ style comments
  ansible.builtin.set_fact:
    cleaned: >-
      {{ text | o0_o.utils.strip_comments(comment_style='cpp') }}
"""

RETURN = r"""
_value:
  description: Text with comments removed.
  type: str
  returned: always
"""


class FilterModule:
    """Expose comment stripping as an Ansible filter.

    Note: @typechecked is omitted because the underlying strip_comments
    helper uses pyparsing types that typeguard cannot resolve.
    """

    def filters(self) -> Dict[str, Any]:
        return {"strip_comments": self.strip_comments_filter}

    def strip_comments_filter(
        self,
        value: Any,
        comment_style: Any = "python",
        strip_blank_lines: bool = True,
    ) -> str:
        """Apply the shared helper with error handling."""
        try:
            if not isinstance(value, str):
                raise ValueError(
                    "strip_comments expects a string, got "
                    f"{type(value).__name__}"
                )

            return strip_comments(
                value,
                comment_style=comment_style,
                strip_blank_lines=strip_blank_lines,
            )
        except Exception as exc:  # pragma: no cover - defensive
            error = (
                f"strip_comments failed: {type(exc).__name__}: "
                f"{to_native(exc)}"
            )
            raise AnsibleFilterError(error) from exc
