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

from collections.abc import Iterable
from typing import Any


class FilterModule:
    """Ansible filter plugin."""

    def filters(self):
        """Return filter functions."""
        return {
            'wantlist': self.wantlist,
        }

    def wantlist(self, value: Any, want_list: bool = True) -> Any:
        """Ensure value is a list or return single value based on want_list parameter.

        When want_list=True (default), converts various types to a list:
        - None -> []
        - str -> [str]
        - Iterable (list, tuple, set, etc.) -> list(iterable)
        - Any other type -> [value]

        When want_list=False, prefers single values (calls notwantlist)

        :param value: The value to process
        :param want_list: If True, always return a list. If False, prefer single values
        :returns: The processed value
        """
        # If want_list is False, delegate to notwantlist
        if not want_list:
            return self._notwantlist(value)

        # Handle None - return empty list
        if value is None:
            return []

        # Handle strings - wrap in list (don't iterate over chars)
        if isinstance(value, str):
            return [value]

        # Handle dicts - wrap in list (don't iterate over keys)
        if isinstance(value, dict):
            return [value]

        # Handle iterables - convert to list
        if isinstance(value, Iterable):
            return list(value)

        # Any other type - wrap in list
        return [value]

    def _notwantlist(self, value: Any) -> Any:
        """Prefer single values over lists where possible.

        Converts values to simplest form:
        - None -> None
        - Single item list -> item
        - Empty list -> None
        - str -> str
        - Other iterables with multiple items -> list(iterable)
        - Any other type -> value

        :param value: The value to process
        :returns: The processed value in simplest form
        """
        # Handle None - return as-is
        if value is None:
            return None

        # Handle strings - return as-is
        if isinstance(value, str):
            return value

        # Handle dicts - return as-is (don't iterate over keys)
        if isinstance(value, dict):
            return value

        # Handle iterables
        if isinstance(value, Iterable):
            items = list(value)
            # Empty iterable (list, set, tuple, etc.) -> None
            if items == []:
                return None
            # Single item -> return the item
            elif len(items) == 1:
                return items[0]
            # Multiple items -> return as list
            else:
                return items

        # Any other type - return as-is
        return value
