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

from typing import Any, List

from ansible.errors import AnsibleFilterError


class FilterModule:
    """Ansible filter plugin."""

    def filters(self):
        """Return filter functions."""
        return {
            'string2items': self.string2items,
        }

    def string2items(self, value: Any, delimiter: str = ',', trim: bool = True) -> List[str]:
        """Convert delimited string to list of items.


        :param value: The string to split
        :param delimiter: The delimiter to split on (default: comma)
        :param trim: Whether to strip whitespace from items (default: True)
        :returns: List of items
        :raises AnsibleFilterError: If value cannot be converted to string
        """
        if not isinstance(value, str):
            # Try to convert to string
            try:
                value = str(value)
            except (TypeError, ValueError) as e:
                raise AnsibleFilterError(
                    f"string2items requires a string or string-castable input, got {type(value).__name__}"
                ) from e

        # Split on delimiter
        items = value.split(delimiter)

        if trim:
            # Strip whitespace and filter out empty items
            items = [item.strip() for item in items if item.strip()]
        else:
            # Keep all items as-is (including empty ones)
            items = list(items)

        return items
