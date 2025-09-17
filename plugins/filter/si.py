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

"""Filter plugin for SI unit parsing and formatting."""

from __future__ import annotations

from typing import Any, Dict, Union
from ansible_collections.o0_o.utils.plugins.module_utils import parse_si


DOCUMENTATION = r"""
---
name: si
short_description: Parse values with SI or IEC unit prefixes
version_added: "1.1.0"
description:
  - Parse values with SI (decimal) or IEC (binary) prefixes to base units
  - Extracts base unit from prefixed values
  - Supports SI prefixes from kilo (10^3) to quetta (10^30)
  - Supports IEC binary prefixes from kibi (2^10) to yobi (2^80)
  - Bare SI/IEC prefixes (e.g., "20G", "5M") are treated as bytes
options:
  _input:
    description:
      - String value with SI or IEC prefix and unit
      - 'Examples: "1000MHz", "32GB", "4GiB", "20G", "5M"'
      - Bare prefixes like "20G" are treated as "20GB"
    type: str
    required: true
  binary:
    description:
      - If True, interpret SI prefixes as binary (e.g., GB becomes GiB)
      - Useful for correcting tools that report binary sizes with SI notation
    type: bool
    default: false
  optimize:
    description:
      - If True, optimize pretty output to use the best prefix
      - 'Example: 2400 MHz -> 2.4 GHz'
      - If False, preserve the original prefix
      - 'Example: 2400 MHz -> 2400 MHz'
    type: bool
    default: true
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
# Parse CPU speed (automatically optimized to GHz)
- name: Parse CPU speed
  ansible.builtin.debug:
    msg: "{{ '2400MHz' | o0_o.utils.si }}"
  # Output: {"hertz": 2400000000, "pretty": "2.4 GHz"}

# Parse memory speed (automatically optimized to GT/s)
- name: Parse memory speed
  ansible.builtin.debug:
    msg: "{{ '2133MT/s' | o0_o.utils.si }}"
  # Output: {"transfers/s": 2133000000, "pretty": "2.133 GT/s"}

# Parse memory size with SI prefix
- name: Parse memory size
  ansible.builtin.debug:
    msg: "{{ '32GB' | o0_o.utils.si }}"
  # Output: {"bytes": 32000000000, "pretty": "32 GB"}

# Parse memory size with IEC binary prefix
- name: Parse binary memory size
  ansible.builtin.debug:
    msg: "{{ '32GiB' | o0_o.utils.si }}"
  # Output: {"bytes": 34359738368, "pretty": "32 GiB"}

# Parse bare SI prefixes (common in df, du output)
- name: Parse size with bare SI prefix
  ansible.builtin.debug:
    msg: "{{ '20G' | o0_o.utils.si }}"
  # Output: {"bytes": 20000000000, "pretty": "20 GB"}

- name: Parse size with bare SI prefix (binary mode)
  ansible.builtin.debug:
    msg: "{{ '20G' | o0_o.utils.si(binary=true) }}"
  # Output: {"bytes": 21474836480, "pretty": "20 GiB"}

# Force binary interpretation of SI prefix (useful for dmidecode output)
- name: Parse memory size as binary
  ansible.builtin.debug:
    msg: "{{ '32GB' | o0_o.utils.si(binary=true) }}"
  # Output: {"bytes": 34359738368, "pretty": "32 GiB"}

# Parse power consumption
- name: Parse power
  ansible.builtin.debug:
    msg: "{{ '1600W' | o0_o.utils.si }}"
  # Output: {"watts": 1600, "pretty": "1.6 kW"}

# Preserve original prefix (no optimization)
- name: Parse without optimization
  ansible.builtin.debug:
    msg: "{{ '2400MHz' | o0_o.utils.si(optimize=false) }}"
  # Output: {"hertz": 2400000000, "pretty": "2400 MHz"}
"""

RETURN = r"""
_value:
  description: Dictionary with base unit as key and parsed value
  type: dict
  returned: always
  sample: {"hertz": 2400000000, "pretty": "2400 MHz"}
"""


class FilterModule(object):
    """Ansible filter plugin for SI unit parsing."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters for this plugin.

        :returns Dict[str, Any]: Mapping of filter names to callables
        """
        return {"si": self.si}

    def si(
        self, value_str: str, binary: bool = False, optimize: bool = True
    ) -> Dict[str, Union[float, str]]:
        """Parse SI/IEC values to base units with pretty formatting.

        :param str value_str: Input like ``"2400MHz"`` or ``"32GiB"``
        :param bool binary: Interpret SI prefixes as IEC binary
        :param bool optimize: Choose a human-friendly prefix for output
        :returns Dict[str, Union[float, str]]: Parsed base units and
            ``pretty`` string
        """
        try:
            return parse_si(value_str, binary=binary, optimize=optimize)
        except Exception:
            return {}
