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

from __future__ import annotations

import re
from typing import Dict, Union

__all__ = ["parse_si", "SI_MULTIPLIERS", "IEC_MULTIPLIERS", "BASE_UNITS"]

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
    "": 1.0,
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

# IEC binary multipliers
IEC_MULTIPLIERS = {
    "": 1.0,
    "Ki": float(2**10),
    "Mi": float(2**20),
    "Gi": float(2**30),
    "Ti": float(2**40),
    "Pi": float(2**50),
    "Ei": float(2**60),
    "Zi": float(2**70),
    "Yi": float(2**80),
}


def parse_si(
    value_str: str, binary: bool = False, optimize: bool = True
) -> Dict[str, Union[int, str]]:
    """Parse a value with SI or IEC units to base units.

    Supports SI prefixes (k..Q) and IEC binary prefixes (Ki..Yi). When
    ``binary`` is True, SI prefixes are interpreted as binary (e.g.,
    ``GB`` -> ``GiB``). When ``optimize`` is True, the returned
    ``pretty`` value selects an appropriate prefix for readability.

    :param value_str: Input like ``"2400MHz"`` or ``"32GiB"``
    :param binary: Interpret SI prefixes as IEC binary
    :param optimize: Optimize the prefix for pretty display
    :returns: Dict with canonical base unit key and integer value plus
        ``pretty`` (e.g., ``{"bytes": 34359738368, "pretty": "32 GiB"}``)
    """
    if not value_str or not isinstance(value_str, str):
        return {}

    value_str = value_str.strip()
    pattern = r"^([\d.]+)\s*(.*)$"
    match = re.match(pattern, value_str)
    if not match:
        return {}

    try:
        number = float(match.group(1))
        suffix = match.group(2).strip()

        prefix = ""
        base_unit = suffix
        if suffix:
            if (
                len(suffix) >= 2
                and suffix[1] == "i"
                and suffix[0] in "kKMGTPEZYRQ"
            ):
                prefix = suffix[:2]
                base_unit = suffix[2:]
            elif suffix[0] in "kKMGTPEZYRQ":
                prefix = suffix[0]
                base_unit = suffix[1:]

        if prefix and not base_unit:
            base_unit = "B"
        if not prefix and not base_unit:
            return {}

        using_iec = False
        if prefix.endswith("i") and len(prefix) == 2:
            multiplier = IEC_MULTIPLIERS.get(prefix, 1.0)
            display_prefix = prefix
            using_iec = True
        elif binary and prefix and not prefix.endswith("i"):
            iec_prefix = prefix + "i" if prefix else ""
            multiplier = IEC_MULTIPLIERS.get(iec_prefix, 1.0)
            display_prefix = iec_prefix
            using_iec = True
        else:
            multiplier = SI_MULTIPLIERS.get(prefix, 1.0)
            display_prefix = prefix

        base_value = number * float(multiplier)

        if optimize:
            multipliers_to_use = (
                IEC_MULTIPLIERS
                if using_iec or (binary and base_unit.upper() == "B")
                else SI_MULTIPLIERS
            )
            sorted_multipliers = sorted(
                multipliers_to_use.items(), key=lambda x: x[1]
            )
            best_prefix = ""
            best_multiplier = 1.0
            for pref, mult in sorted_multipliers:
                if base_value >= mult:
                    best_prefix = pref
                    best_multiplier = mult
            display_value = base_value / best_multiplier
            display_best_prefix = "k" if best_prefix == "K" else best_prefix
        else:
            display_value = number
            display_best_prefix = (
                "k" if display_prefix == "K" else display_prefix
            )

        if abs(display_value - round(display_value)) < 0.01:
            display_str = str(int(round(display_value)))
        else:
            display_str = f"{display_value:.2f}".rstrip("0").rstrip(".")

        if display_best_prefix:
            pretty = f"{display_str} {display_best_prefix}{base_unit}"
        else:
            pretty = f"{display_str} {base_unit}"

        canonical_unit = BASE_UNITS.get(base_unit, base_unit.lower())
        return {canonical_unit: int(base_value), "pretty": pretty}
    except (ValueError, TypeError):
        return {}
