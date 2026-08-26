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

"""Unit tests for error_utils module."""

from __future__ import annotations

import pytest

from ansible_collections.o0_o.utils.plugins.module_utils.error_utils import (
    format_error_message,
)


class TestFormatErrorMessage:
    """Tests for format_error_message function."""

    def test_single_exception(self) -> None:
        """Test formatting a single exception."""
        result = format_error_message([ValueError("bad input")])
        assert result == "1 error encountered: ValueError: bad input"

    def test_single_string(self) -> None:
        """Test formatting a single string error."""
        result = format_error_message(["something went wrong"])
        assert result == "1 error encountered: something went wrong"

    def test_two_errors(self) -> None:
        """Test formatting two errors."""
        errors = [ValueError("first"), TypeError("second")]
        result = format_error_message(errors)
        assert result == (
            "2 errors encountered: (1) ValueError: first (2) TypeError: second"
        )

    def test_three_errors_at_limit(self) -> None:
        """Test formatting three errors at default limit."""
        errors = [ValueError("a"), TypeError("b"), KeyError("c")]
        result = format_error_message(errors)
        assert result == (
            "3 errors encountered: "
            "(1) ValueError: a "
            "(2) TypeError: b "
            "(3) KeyError: 'c'"
        )

    def test_exceeds_default_limit(self) -> None:
        """Test formatting more errors than default limit."""
        errors = [ValueError(f"error {i}") for i in range(5)]
        result = format_error_message(errors)
        assert "5 errors encountered:" in result
        assert "(1) ValueError: error 0" in result
        assert "(2) ValueError: error 1" in result
        assert "(3) ValueError: error 2" in result
        assert "... and 2 other errors" in result
        assert "(4)" not in result

    def test_one_remaining_error(self) -> None:
        """Test singular 'other error' when only one remains."""
        errors = [ValueError(f"e{i}") for i in range(4)]
        result = format_error_message(errors)
        assert "... and 1 other error" in result

    def test_custom_max_display(self) -> None:
        """Test custom max_display limit."""
        errors = [ValueError(f"e{i}") for i in range(10)]
        result = format_error_message(errors, max_display=5)
        assert "10 errors encountered:" in result
        assert "(5) ValueError: e4" in result
        assert "... and 5 other errors" in result
        assert "(6)" not in result

    def test_max_display_one(self) -> None:
        """Test max_display of 1."""
        errors = [ValueError("a"), TypeError("b"), KeyError("c")]
        result = format_error_message(errors, max_display=1)
        assert result == (
            "3 errors encountered: (1) ValueError: a ... and 2 other errors"
        )

    def test_mixed_exceptions_and_strings(self) -> None:
        """Test formatting mixed exception types and strings."""
        errors = [ValueError("exc"), "plain string", RuntimeError("runtime")]
        result = format_error_message(errors)
        assert "(1) ValueError: exc" in result
        assert "(2) plain string" in result
        assert "(3) RuntimeError: runtime" in result

    def test_empty_errors_raises(self) -> None:
        """Test ValueError raised for empty errors."""
        with pytest.raises(ValueError, match="empty"):
            format_error_message([])

    def test_max_display_zero_raises(self) -> None:
        """Test ValueError raised for max_display < 1."""
        with pytest.raises(ValueError, match="max_display"):
            format_error_message([ValueError("test")], max_display=0)

    def test_max_display_negative_raises(self) -> None:
        """Test ValueError raised for negative max_display."""
        with pytest.raises(ValueError, match="max_display"):
            format_error_message([ValueError("test")], max_display=-1)

    def test_generator_input(self) -> None:
        """Test that generator inputs are handled correctly."""

        def error_gen():
            yield ValueError("first")
            yield TypeError("second")

        result = format_error_message(error_gen())
        assert "2 errors encountered:" in result
        assert "(1) ValueError: first" in result

    @pytest.mark.parametrize(
        "count,expected_remaining",
        [
            (4, "1 other error"),
            (5, "2 other errors"),
            (10, "7 other errors"),
        ],
    )
    def test_remaining_count(
        self, count: int, expected_remaining: str
    ) -> None:
        """Test remaining error count with various totals."""
        errors = [ValueError(f"e{i}") for i in range(count)]
        result = format_error_message(errors)
        assert f"... and {expected_remaining}" in result

    def test_error_count_at_start(self) -> None:
        """Test that error count appears at start of message."""
        errors = [ValueError("test")] * 5
        result = format_error_message(errors)
        assert result.startswith("5 errors encountered:")

    def test_preserves_error_message(self) -> None:
        """Test that original error messages are preserved."""
        msg = "detailed error: file not found at /path/to/file"
        result = format_error_message([FileNotFoundError(msg)])
        assert msg in result
