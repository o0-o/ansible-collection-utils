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

"""String manipulation utilities."""

from __future__ import annotations


def to_pascal_case(text: str) -> str:
    """Convert text to PascalCase.

    Handles various input formats:
    - snake_case → PascalCase
    - kebab-case → PascalCase
    - lowercase → PascalCase (with word boundary detection)
    - camelCase → PascalCase (preserved)

    For compound words without separators, uses common word boundaries.

    Examples:
        >>> to_pascal_case("password_authentication")
        'PasswordAuthentication'
        >>> to_pascal_case("no-port-forwarding")
        'NoPortForwarding'
        >>> to_pascal_case("forwardagent")
        'ForwardAgent'
        >>> to_pascal_case("x11forwarding")
        'X11Forwarding'

    :param str text: Input text in any case format
    :returns str: Text converted to PascalCase
    """
    if not text:
        return text

    # Common word boundaries for compound word splitting
    # These are checked in order (longest first for greedy matching)
    word_boundaries = [
        "authentication",
        "forwarding",
        "algorithm",
        "password",
        "address",
        "interval",
        "certificate",
        "command",
        "counter",
        "maximum",
        "minimum",
        "environment",
        "pubkey",
        "host",
        "user",
        "client",
        "server",
        "forward",
        "agent",
        "port",
        "key",
        "file",
        "max",
        "min",
        "count",
        "alive",
        "permit",
        "allow",
        "deny",
        "accept",
        "send",
        "gateway",
        "tcp",
        "x11",
        "pty",
    ]

    # Replace common separators with spaces
    text = text.replace("_", " ").replace("-", " ")

    # If already has spaces or capitals, just capitalize parts
    if " " in text or any(c.isupper() for c in text):
        parts = []
        current = []

        for i, char in enumerate(text):
            if char == " ":
                if current:
                    parts.append("".join(current))
                    current = []
            elif char.isupper() and i > 0 and current and current[-1].islower():
                # CamelCase boundary
                parts.append("".join(current))
                current = [char]
            else:
                current.append(char)

        if current:
            parts.append("".join(current))

        return "".join(part.capitalize() for part in parts if part)

    # For lowercase compound words, try to split on word boundaries
    lower_text = text.lower()
    parts = []
    pos = 0

    while pos < len(lower_text):
        # Try to match a word boundary
        matched = False
        for boundary in word_boundaries:
            if lower_text[pos:].startswith(boundary):
                parts.append(boundary)
                pos += len(boundary)
                matched = True
                break

        if not matched:
            # Take next character
            if parts and len(parts[-1]) < 10:
                # Append to last part if it's short
                parts[-1] += lower_text[pos]
            else:
                # Start new part
                parts.append(lower_text[pos])
            pos += 1

    # Capitalize each part
    return "".join(part.capitalize() for part in parts if part)


__all__ = ["to_pascal_case"]
