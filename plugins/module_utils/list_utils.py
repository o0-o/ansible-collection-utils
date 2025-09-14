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

from typing import Any, List

__all__ = ["string2items", "wantlist"]


def string2items(value: Any, delimiter: str = ",", trim: bool = True) -> List[str]:
    """Split a delimited string into a list of items.

    :param value: Input value; will be cast to ``str`` when possible
    :param delimiter: Delimiter to split on (default: ",")
    :param trim: Strip whitespace and drop empties when True
    :returns: List of items
    :raises TypeError: When the input cannot be cast to ``str``
    """
    if not isinstance(value, str):
        try:
            value = str(value)
        except Exception as e:  # pragma: no cover - error path
            raise TypeError(
                "string2items requires a string or string-castable input"
            ) from e

    items = value.split(delimiter)
    if trim:
        items = [item.strip() for item in items if item.strip()]
    else:
        items = list(items)
    return items


def wantlist(value: Any, want_list: bool = True) -> Any:
    """Ensure value is a list or reduce to simplest form.

    When ``want_list`` is True, convert inputs to a list in a
    predictable way. When False, reduce lists/iterables to their
    simplest representation.

    - None -> [] (or None when want_list is False)
    - str -> [str]
    - dict -> [dict]
    - iterable -> list(iterable)

    :param value: Value to process
    :param want_list: If True, always return a list; if False, prefer a
        single value
    :returns: Processed value
    """
    if not want_list:
        return _notwantlist(value)

    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [value]

    from collections.abc import Iterable

    if isinstance(value, Iterable):
        return list(value)
    return [value]


def _notwantlist(value: Any) -> Any:
    """Prefer single values over lists when possible (private helper).

    - None -> None
    - str -> str
    - dict -> dict
    - [] -> None
    - [x] -> x
    - [x, y, ...] or iterable -> list(iterable)
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value

    from collections.abc import Iterable

    if isinstance(value, Iterable):
        items = list(value)
        if items == []:
            return None
        if len(items) == 1:
            return items[0]
        return items
    return value
