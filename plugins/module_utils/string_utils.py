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

import codecs

from typing import Any, Iterable, List, Sequence, Union

try:
    from pyparsing import (
        MatchFirst,
        ParserElement,
        QuotedString,
        cStyleComment,
        cppStyleComment,
        dblSlashComment,
        pythonStyleComment,
    )

    HAS_PYPARSING = True
    PYPARSING_IMPORT_ERROR = None
except ImportError:
    HAS_PYPARSING = False
    PYPARSING_IMPORT_ERROR = (
        "pyparsing is required for strip_comments. "
        "Install with: pip install pyparsing"
    )

CommentStyle = Union[
    str,
    "ParserElement",
    Sequence[Union[str, "ParserElement"]],
]

_COMMENT_STYLES = {
    "python": pythonStyleComment if HAS_PYPARSING else None,
    "hash": pythonStyleComment if HAS_PYPARSING else None,
    "shell": pythonStyleComment if HAS_PYPARSING else None,
    "c": cStyleComment if HAS_PYPARSING else None,
    "cpp": cppStyleComment if HAS_PYPARSING else None,
    "c++": cppStyleComment if HAS_PYPARSING else None,
    "slash": dblSlashComment if HAS_PYPARSING else None,
    "double_slash": dblSlashComment if HAS_PYPARSING else None,
}

_DEFAULT_QUOTES: Iterable[Any] = (
    (
        QuotedString('"', esc_char="\\"),
        QuotedString("'", esc_char="\\"),
        QuotedString('"""', esc_char="\\", multiline=True),
        QuotedString("'''", esc_char="\\", multiline=True),
    )
    if HAS_PYPARSING
    else ()
)


def _ensure_parser_elements(
    style: CommentStyle,
) -> List[Any]:
    """Normalize comment style input to parser elements.

    Note: @typechecked is omitted here because typeguard cannot resolve
    the CommentStyle type alias containing pyparsing's ParserElement.
    """
    if not HAS_PYPARSING:
        raise ImportError(PYPARSING_IMPORT_ERROR)

    if isinstance(style, ParserElement):
        return [style]

    if isinstance(style, str):
        key = style.lower()
        parser = _COMMENT_STYLES.get(key)
        if parser is None:
            raise ValueError(f"Unsupported comment style '{style}'")
        return [parser]

    if isinstance(style, Sequence):
        elements: List[Any] = []
        for item in style:
            elements.extend(_ensure_parser_elements(item))
        if not elements:
            raise ValueError("Comment style sequence must not be empty")
        return elements

    raise TypeError(
        "comment_style must be a string, ParserElement, or sequence of either"
    )


def strip_comments(
    text: str,
    comment_style: CommentStyle = "python",
    strip_blank_lines: bool = True,
) -> str:
    """Strip comments from multiline text using pyparsing.

    Respects quoted strings so inline comment markers inside C('"..."')
    are preserved. Supports common comment syntaxes via C(comment_style)
    or accepts custom pyparsing expressions.

    :param str text: Multiline input to clean.
    :param CommentStyle comment_style: Comment syntax to remove. Accepts
        named styles (C('python'), C('c'), C('cpp'), C('slash')) or
        custom pyparsing parser elements / sequences thereof.
    :param bool strip_blank_lines: When ``True`` remove empty lines that
        remain after comment removal.
    :returns str: Text with comments stripped.
    :raises ImportError: If pyparsing is not installed.
    :raises ValueError: If an unknown comment style is requested.
    :raises TypeError: If C(comment_style) is of an unsupported type.
    """
    if not text:
        return ""

    if not HAS_PYPARSING:
        raise ImportError(PYPARSING_IMPORT_ERROR)

    comment_elements = _ensure_parser_elements(comment_style)

    combined = MatchFirst(
        [element.copy() for element in comment_elements]
    ).suppress()

    for quote in _DEFAULT_QUOTES:
        combined = combined.ignore(quote)

    cleaned = combined.transform_string(text)

    lines = cleaned.splitlines()
    processed: List[str] = []
    for line in lines:
        stripped = line.rstrip()
        if strip_blank_lines:
            if stripped:
                processed.append(stripped)
        else:
            processed.append(stripped)

    if not processed:
        return ""

    return "\n".join(processed)


def validate_encoding(encoding: str) -> str:
    """Validate encoding name and return normalized lowercase form.

    :param str encoding: Encoding name to validate (e.g., 'UTF-8')
    :returns str: Normalized lowercase encoding name
    :raises ValueError: If encoding is not recognized by Python's
        codec system
    """
    encoding = encoding.lower()
    try:
        codecs.lookup(encoding)
    except LookupError as e:
        raise ValueError(f"Invalid encoding: {e}") from e
    return encoding


__all__ = ["strip_comments", "validate_encoding"]
