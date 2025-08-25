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

import re
from typing import Dict, Union


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
options:
  _input:
    description:
      - String value with SI or IEC prefix and unit
      - 'Examples: "1000MHz", "32GB", "4GiB"'
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

    # Known base units - normalizes common computing units
    # Maps abbreviated forms to canonical lowercase keys
    BASE_UNITS = {
        # Storage/Memory
        "b": "bits",
        "B": "bytes",
        # Frequency
        "Hz": "hertz",
        "hz": "hertz",
        # Data transfer rates
        "T/s": "transfers/s",
        "t/s": "transfers/s",
        "bps": "bits/s",
        "b/s": "bits/s",
        "bit/s": "bits/s",
        "Bps": "bytes/s",
        "B/s": "bytes/s",
        "Byte/s": "bytes/s",
        "byte/s": "bytes/s",
        # Power
        "w": "watts",
        "W": "watts",
    }

    # SI (decimal) multipliers - kilo through quetta
    SI_MULTIPLIERS = {
        "": 1,
        "k": 1e3,  # kilo (lowercase)
        "K": 1e3,  # kilo (uppercase)
        "M": 1e6,  # mega
        "G": 1e9,  # giga
        "T": 1e12,  # tera
        "P": 1e15,  # peta
        "E": 1e18,  # exa
        "Z": 1e21,  # zetta
        "Y": 1e24,  # yotta
        "R": 1e27,  # ronna
        "Q": 1e30,  # quetta
    }

    # IEC binary prefixes as defined in IEC 60027-2:2000 Amendment 2
    # (1999). These are the standard binary prefixes for data sizes
    IEC_MULTIPLIERS = {
        "": 1,
        "Ki": 2**10,  # kibi = 1024
        "Mi": 2**20,  # mebi = 1048576
        "Gi": 2**30,  # gibi = 1073741824
        "Ti": 2**40,  # tebi = 1099511627776
        "Pi": 2**50,  # pebi = 1125899906842624
        "Ei": 2**60,  # exbi = 1152921504606846976
        "Zi": 2**70,  # zebi = 1180591620717411303424
        "Yi": 2**80,  # yobi = 1208925819614629174706176
    }

    def filters(self):
        """Return the filter functions.

        :returns: Dictionary mapping filter names to functions
        """
        return {
            "si": self.si,
        }

    def si(
        self,
        value_str: str,
        binary: bool = False,
        optimize: bool = True,
    ) -> Dict[str, Union[float, str]]:
        """Parse a value with SI or IEC units and extract the base unit.

        This function identifies SI prefixes (kilo through quetta) or
        IEC binary prefixes (kibi through yobi) and extracts the base
        unit that follows. For example:
        - "1000MHz" -> {"hz": 1000000000, "pretty": "1000 MHz"}
        - "2133MT/s" -> {"t/s": 2133000000, "pretty": "2133 MT/s"}
        - "32GB" -> {"b": 32000000000, "pretty": "32 GB"}
        - "32GB" with binary=True -> {"b": 34359738368,
            "pretty": "32 GiB"}
        - "4GiB" -> {"b": 4294967296, "pretty": "4 GiB"}

        Supports:
        - SI prefixes from kilo (10^3) to quetta (10^30)
        - IEC binary prefixes from kibi (2^10) to yobi (2^80)

        :param value_str: String with value and unit ("1000MHz", "32GB")
        :param binary: If True, treat SI prefixes as binary (GB -> GiB)
        :param optimize: If True, optimize pretty output; if False, keep
            original prefix
        :returns: Dictionary with base unit as key and value in base
            units
        """
        if not value_str or not isinstance(value_str, str):
            return {}

        # Clean up the input
        value_str = value_str.strip()

        # Pattern to match number followed by optional prefix and unit
        # Handles both SI (single letter) and IEC (two letter 'i')
        # Groups: (number) (whitespace) (SI/IEC prefix) (base unit)
        pattern = r"^([\d.]+)\s*([kKMGTPEZYRQ]i?|[kKMGTPEZY]?)([A-Za-z].*)$"
        match = re.match(pattern, value_str)

        if not match:
            return {}

        try:
            number = float(match.group(1))
            prefix = match.group(2)
            base_unit = match.group(3).strip()

            # Determine which multiplier to use and track if using IEC
            using_iec = False
            if prefix.endswith("i") and len(prefix) == 2:
                # Explicit IEC binary prefix (e.g., GiB)
                multiplier = FilterModule.IEC_MULTIPLIERS.get(prefix, 1)
                display_prefix = prefix
                using_iec = True
            elif binary and prefix and not prefix.endswith("i"):
                # Force binary interpretation of SI prefix
                # (e.g., GB -> GiB)
                iec_prefix = prefix + "i" if prefix else ""
                multiplier = FilterModule.IEC_MULTIPLIERS.get(iec_prefix, 1)
                display_prefix = iec_prefix
                using_iec = True
            else:
                # Standard SI decimal prefix
                multiplier = FilterModule.SI_MULTIPLIERS.get(prefix, 1)
                display_prefix = prefix

            base_value = number * multiplier

            if optimize:
                # Find the optimal prefix for pretty printing
                # Use IEC for binary units, SI for others
                if using_iec or (binary and base_unit.upper() == "B"):
                    # Use IEC multipliers for binary units
                    multipliers_to_use = FilterModule.IEC_MULTIPLIERS
                else:
                    # Use SI multipliers
                    multipliers_to_use = FilterModule.SI_MULTIPLIERS

                # Sort multipliers by value to find the best fit
                sorted_multipliers = sorted(
                    multipliers_to_use.items(), key=lambda x: x[1]
                )

                # Find the largest prefix where value >= 1
                best_prefix = ""
                best_multiplier = 1
                for pref, mult in sorted_multipliers:
                    if base_value >= mult:
                        best_prefix = pref
                        best_multiplier = mult

                # Calculate the display value with the best prefix
                display_value = base_value / best_multiplier

                # Normalize K to lowercase k
                display_best_prefix = best_prefix
                if best_prefix == "K":
                    display_best_prefix = "k"
            else:
                # Keep original prefix and value
                display_value = number
                display_best_prefix = display_prefix
                # Still normalize K to lowercase k
                if display_best_prefix == "K":
                    display_best_prefix = "k"

            # Format pretty string
            if display_best_prefix:
                pretty = f"{display_value:g} {display_best_prefix}{base_unit}"
            else:
                # Avoid scientific notation for large integers
                if display_value >= 1000 and display_value == int(
                    display_value
                ):
                    pretty = f"{int(display_value)} {base_unit}"
                else:
                    pretty = f"{display_value:g} {base_unit}"

            # Normalize base unit using our mapping
            canonical_unit = FilterModule.BASE_UNITS.get(
                base_unit, base_unit.lower()
            )

            return {canonical_unit: base_value, "pretty": pretty}

        except (ValueError, TypeError):
            return {}
