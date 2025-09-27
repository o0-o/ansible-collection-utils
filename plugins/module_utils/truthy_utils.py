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

"""Utilities for interpreting integers or boolean-like values."""

from __future__ import annotations

from typing import Any, Optional, Union

try:
    from ansible.module_utils.common.boolean import boolean
except ImportError:  # pragma: no cover - fallback for older Ansible
    from ansible.module_utils.parsing.convert_bool import boolean


def _coerce_integer(value: Any) -> Optional[int]:
    """Attempt to convert a value into a base-10 integer.

    :param Any value: Candidate value to convert.
    :returns Optional[int]: Integer if value represents an integer,
        otherwise ``None``
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return int(stripped)
        except ValueError:
            return None
    return None


def truthy_or_integer(
    value: Any,
    *,
    zero_is_false: bool = False,
    only_positive: bool = False,
) -> Union[bool, int]:
    """Interpret value as an integer when possible, else use boolean().

    Prefer integers when the input is an integral literal or type.
    Fall back to Ansible's :func:`boolean` helper to process other
    truthy representations with ``strict=False`` semantics.

    :param Any value: Input to interpret as integer or boolean.
    :param bool zero_is_false: When true, return ``False`` for zero
        values instead of the integer ``0``.
    :param bool only_positive: When true, reject negative integers
        and zero (unless ``zero_is_false`` handles it).
    :returns Union[bool, int]: Integer or boolean representation.
    :raises ValueError: If value cannot be parsed as integer or boolean,
        or ``only_positive`` rejects a negative integer.
    """
    integer_candidate = _coerce_integer(value)
    if integer_candidate is not None:
        if integer_candidate == 0:
            if zero_is_false:
                return False
            if only_positive:
                raise ValueError(
                    "truthy_or_integer expected a positive integer but "
                    "received 0"
                )
            return 0
        if only_positive and integer_candidate < 0:
            raise ValueError(
                "truthy_or_integer expected a positive integer but "
                f"received {integer_candidate}"
            )
        return integer_candidate

    try:
        return boolean(value, strict=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Unable to interpret {value!r} as an integer or boolean"
        ) from exc
