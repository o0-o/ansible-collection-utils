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

"""Error formatting utilities for Ansible action plugins.

Provides functions for formatting error collections into human-readable
messages suitable for Ansible result dictionaries.
"""

from __future__ import annotations

from typing import Iterable, Union

from ansible_collections.o0_o.utils.plugins.module_utils.typeguard_compat import (  # noqa: E501
    typechecked,
)


@typechecked
def format_error_message(
    errors: Iterable[Union[Exception, str]],
    max_display: int = 3,
) -> str:
    """Format a collection of errors into a human-readable message.

    Generates a message string that communicates the scope and nature of
    errors encountered. For single errors, provides the error type and
    message. For multiple errors, lists them with numbering up to a
    limit, then summarizes any remaining errors.

    :param Iterable[Union[Exception, str]] errors: Collection of
        errors to format. Can be Exception instances or strings.
    :param int max_display: Maximum number of individual errors to
        display before summarizing. Defaults to 3.
    :returns str: Formatted error message string
    :raises ValueError: If errors is empty or max_display < 1

    Examples::

        >>> format_error_message([ValueError("bad input")])
        '1 error encountered: ValueError: bad input'

        >>> format_error_message([ValueError("a"), TypeError("b")])
        '2 errors encountered: (1) ValueError: a (2) TypeError: b'
    """
    if max_display < 1:
        raise ValueError("max_display must be at least 1")

    error_list = list(errors)

    if not error_list:
        raise ValueError("errors iterable is empty")

    total = len(error_list)

    def format_single(err: Union[Exception, str]) -> str:
        """Format a single error with type name if applicable."""
        if isinstance(err, Exception):
            return f"{type(err).__name__}: {err}"
        return str(err)

    # Single error - simple format
    if total == 1:
        return f"1 error encountered: {format_single(error_list[0])}"

    # Multiple errors
    parts = [f"{total} errors encountered:"]

    # Add numbered errors up to the limit
    display_count = min(total, max_display)
    for i, err in enumerate(error_list[:display_count], start=1):
        parts.append(f"({i}) {format_single(err)}")

    # Add summary of remaining errors if any
    remaining = total - display_count
    if remaining > 0:
        if remaining == 1:
            parts.append("... and 1 other error")
        else:
            parts.append(f"... and {remaining} other errors")

    return " ".join(parts)
