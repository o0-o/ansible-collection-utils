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

"""Tests for string_utils helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("pyparsing")

MODULE_PATH = (
    Path(__file__).parents[4] / "plugins" / "module_utils" / "string_utils.py"
)

spec = importlib.util.spec_from_file_location("string_utils", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

strip_comments = module.strip_comments


def test_strip_comments_default_python() -> None:
    """Test stripping python-style comments and blank lines."""

    content = """
# header comment
/bin/bash  # default shell
/bin/zsh

# trailing comment
"""

    result = strip_comments(content)
    assert result.splitlines() == ["/bin/bash", "/bin/zsh"]


def test_strip_comments_preserve_blank_lines() -> None:
    """Test preserving blank lines when requested."""

    content = """/bin/bash
# comment

/bin/fish"""

    result = strip_comments(content, strip_blank_lines=False)
    # Comment removal leaves blank line, plus original blank line = 2 blanks
    assert result.splitlines() == ["/bin/bash", "", "", "/bin/fish"]


def test_strip_comments_custom_style() -> None:
    """Test removing double-slash comments when style provided."""

    content = "value // inline"
    assert strip_comments(content, comment_style="slash") == "value"


def test_strip_comments_unknown_style() -> None:
    """Test error raised for unsupported comment style."""

    with pytest.raises(ValueError):
        strip_comments("value", comment_style="unknown")
