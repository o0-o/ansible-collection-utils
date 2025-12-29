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

"""Filter exposing the unflatten helper."""

from __future__ import annotations

from typing import Any, Dict, List, Union

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.o0_o.utils.plugins.module_utils.typeguard_compat import (  # noqa: E501
    typechecked,
)

from ansible_collections.o0_o.utils.plugins.module_utils import (
    unflatten as unflatten_helper,
)

DOCUMENTATION = r"""
---
name: unflatten
short_description: Convert flat dictionary with delimited keys to nested dict
version_added: "1.6.0"
description:
  - >-
    Transforms flat dictionaries with delimited keys into nested dictionary
    structures.
  - >-
    Useful for parsing extended attributes (xattrs) where keys use dot
    notation (e.g., C(user.comment)) or macOS Spotlight metadata which uses
    both dots and colons (e.g., C(com.apple.metadata:kMDItemWhereFroms)).
options:
  _input:
    description:
      - Flat dictionary with delimited keys.
    type: dict
    required: true
  separators:
    description:
      - >-
        Delimiter character(s) to split keys on. Can be a single string or
        list of strings.
      - >-
        Default is C(.) for standard dot notation. Use C([\".\", \":\"]) for
        xattr-style keys where macOS Spotlight uses colons.
    type: raw
    default: "."
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
# Convert dot-notation keys to nested dict
- name: Unflatten user attributes
  ansible.builtin.debug:
    msg: "{{ flat_attrs | o0_o.utils.unflatten }}"
  vars:
    flat_attrs:
      user.comment: "hello"
      user.mime_type: "text/plain"
      security.selinux: "unconfined_u:object_r:user_home_t:s0"
  # Result:
  # {
  #   "user": {"comment": "hello", "mime_type": "text/plain"},
  #   "security": {"selinux": "unconfined_u:object_r:user_home_t:s0"}
  # }

# Handle macOS xattrs with both . and : delimiters
- name: Unflatten macOS extended attributes
  ansible.builtin.debug:
    msg: "{{ macos_xattrs | o0_o.utils.unflatten(separators=['.', ':']) }}"
  vars:
    macos_xattrs:
      com.apple.quarantine: "0081;..."
      com.apple.metadata:kMDItemWhereFroms: "https://example.com"
  # Result:
  # {
  #   "com": {
  #     "apple": {
  #       "quarantine": "0081;...",
  #       "metadata": {"kMDItemWhereFroms": "https://example.com"}
  #     }
  #   }
  # }
"""

RETURN = r"""
_value:
  description: Nested dictionary structure.
  type: dict
  returned: always
"""


class FilterModule:
    """Ansible filter exposing unflatten."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters."""
        return {"unflatten": self.unflatten_filter}

    @typechecked
    def unflatten_filter(
        self,
        flat: Dict[str, Any],
        separators: Union[str, List[str]] = ".",
    ) -> Dict[str, Any]:
        """Delegate to the shared unflatten helper."""
        try:
            return unflatten_helper(flat, separators=separators)
        except AnsibleFilterError:
            raise
        except Exception as e:
            raise AnsibleFilterError(
                f"unflatten failed: {e.__class__.__name__}: {to_native(e)}"
            ) from e
