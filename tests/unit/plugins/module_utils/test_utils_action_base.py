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

"""Unit tests for UtilsActionBase."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from ansible_collections.o0_o.utils.plugins.module_utils.utils_action_base import (  # noqa: E501
    UtilsActionBase,
)


@pytest.fixture
def action_base() -> UtilsActionBase:
    """Create a UtilsActionBase instance for testing."""
    return UtilsActionBase()


@pytest.fixture
def mock_constants():
    """Create a mock ansible.constants module."""
    return SimpleNamespace(MODULE_STRICT_UTF8_RESPONSE=True)


class TestBinarySafeExecution:
    """Tests for _binary_safe_execution context manager."""

    def test_raises_without_constants_imported(self) -> None:
        """Test that RuntimeError is raised when ansible.constants not imported."""
        base = UtilsActionBase()

        # Ensure ansible.constants is not in sys.modules
        with patch.dict(sys.modules, {"ansible.constants": None}, clear=False):
            # Remove it to simulate it not being imported
            saved = sys.modules.pop("ansible.constants", None)
            try:
                with pytest.raises(RuntimeError, match="ansible.constants"):
                    with base._binary_safe_execution():
                        pass
            finally:
                if saved is not None:
                    sys.modules["ansible.constants"] = saved

    def test_disables_strict_utf8_inside_context(
        self, action_base: UtilsActionBase, mock_constants: SimpleNamespace
    ) -> None:
        """Test that strict UTF-8 response is disabled inside."""
        with patch.dict(
            sys.modules, {"ansible.constants": mock_constants}, clear=False
        ):
            with action_base._binary_safe_execution():
                assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is False

    def test_restores_original_value_after_context(
        self, action_base: UtilsActionBase, mock_constants: SimpleNamespace
    ) -> None:
        """Test that original value is restored after context exits."""
        mock_constants.MODULE_STRICT_UTF8_RESPONSE = True

        with patch.dict(
            sys.modules, {"ansible.constants": mock_constants}, clear=False
        ):
            with action_base._binary_safe_execution():
                pass

            assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is True

    def test_restores_original_false_value(
        self, action_base: UtilsActionBase, mock_constants: SimpleNamespace
    ) -> None:
        """Test that False value is preserved if originally False."""
        mock_constants.MODULE_STRICT_UTF8_RESPONSE = False

        with patch.dict(
            sys.modules, {"ansible.constants": mock_constants}, clear=False
        ):
            with action_base._binary_safe_execution():
                assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is False

            assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is False

    def test_restores_value_on_exception(
        self, action_base: UtilsActionBase, mock_constants: SimpleNamespace
    ) -> None:
        """Test that original value is restored on exception."""
        mock_constants.MODULE_STRICT_UTF8_RESPONSE = True

        with patch.dict(
            sys.modules, {"ansible.constants": mock_constants}, clear=False
        ):
            with pytest.raises(ValueError, match="test exception"):
                with action_base._binary_safe_execution():
                    assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is False
                    raise ValueError("test exception")

            assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is True

    def test_nested_contexts(
        self, action_base: UtilsActionBase, mock_constants: SimpleNamespace
    ) -> None:
        """Test that nested contexts restore correctly."""
        mock_constants.MODULE_STRICT_UTF8_RESPONSE = True

        with patch.dict(
            sys.modules, {"ansible.constants": mock_constants}, clear=False
        ):
            with action_base._binary_safe_execution():
                assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is False

                with action_base._binary_safe_execution():
                    assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is False

                # Inner restores to False (what outer set it to)
                assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is False

            # Outer context restores to original True
            assert mock_constants.MODULE_STRICT_UTF8_RESPONSE is True
