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

"""Unit tests for the strip_comments filter."""

from __future__ import annotations

import pytest
from ansible.errors import AnsibleFilterError
import importlib.util
from pathlib import Path

pytest.importorskip("pyparsing")

MODULE_PATH = (
    Path(__file__).parents[4] / "plugins" / "filter" / "strip_comments.py"
)

spec = importlib.util.spec_from_file_location(
    "strip_comments_filter", MODULE_PATH
)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

FilterModule = module.FilterModule


@pytest.fixture
def filter_module() -> FilterModule:
    """Provide a filter module instance."""
    return FilterModule()


def test_strip_comments_basic(filter_module: FilterModule) -> None:
    """Strips python-style comments and blank lines."""
    text = """
# comment
/bin/bash  # trailing
/bin/zsh
"""
    result = filter_module.strip_comments_filter(text)
    assert result == "/bin/bash\n/bin/zsh"


def test_strip_comments_preserve_blanks(filter_module: FilterModule) -> None:
    """Preserving blank lines returns empty separators."""
    text = """/bin/bash
# comment

/bin/fish"""
    result = filter_module.strip_comments_filter(text, strip_blank_lines=False)
    # Comment removal leaves blank line, plus original blank line = 2 blanks
    assert result.splitlines() == ["/bin/bash", "", "", "/bin/fish"]


def test_strip_comments_invalid_input(filter_module: FilterModule) -> None:
    """Non-string values raise AnsibleFilterError."""
    with pytest.raises(AnsibleFilterError):
        filter_module.strip_comments_filter(123)
