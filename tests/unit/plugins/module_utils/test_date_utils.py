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

"""Unit tests for date parsing helpers."""

from __future__ import annotations

from ansible_collections.o0_o.utils.plugins.module_utils import (
    parse_datetime,
    parse_date_to_epoch,
)


class TestParseDatetime:
    """Test parse_datetime utility function."""

    def test_date_only_formats(self) -> None:
        """Test parsing date-only inputs."""
        # MM/DD/YYYY format
        result = parse_datetime("01/15/2025")
        assert result is not None
        assert "seconds" in result
        assert result["iso8601"] == "2025-01-15"
        assert "January 15, 2025" in result["pretty"]
        assert "offset" not in result  # No timezone

        # YYYY-MM-DD format
        result = parse_datetime("2025-01-15")
        assert result is not None
        assert "seconds" in result
        assert result["iso8601"] == "2025-01-15"

    def test_datetime_without_seconds(self) -> None:
        """Test parsing datetime without seconds."""
        result = parse_datetime("2025-01-15 14:30")
        assert result is not None
        assert "seconds" in result
        assert result["iso8601"] == "2025-01-15T14:30"
        assert "2:30 p.m." in result["pretty"]

    def test_datetime_with_seconds(self) -> None:
        """Test parsing datetime with seconds precision."""
        result = parse_datetime("2025-01-15 14:30:45")
        assert result is not None
        assert "seconds" in result
        assert result["iso8601"] == "2025-01-15T14:30:45"
        assert "2:30:45 p.m." in result["pretty"]

    def test_time_only_formats(self) -> None:
        """Test parsing time-only inputs."""
        # 24-hour format
        result = parse_datetime("14:30")
        assert result is not None
        assert "seconds" in result
        # Should be seconds since midnight: 14*3600 + 30*60 = 52200
        assert result["seconds"] == 52200
        assert result["iso8601"] == "14:30"
        assert "2:30 p.m." in result["pretty"]

        # 12-hour format with PM
        result = parse_datetime("2:45 PM")
        assert result is not None
        # Should be seconds since midnight: 14*3600 + 45*60 = 53100
        assert result["seconds"] == 53100
        assert "2:45 p.m." in result["pretty"]

        # 12-hour format with AM
        result = parse_datetime("10:15 AM")
        assert result is not None
        # Should be seconds since midnight: 10*3600 + 15*60 = 36900
        assert result["seconds"] == 36900
        assert "10:15 a.m." in result["pretty"]

    def test_time_with_seconds(self) -> None:
        """Test parsing time with seconds precision."""
        result = parse_datetime("14:30:45")
        assert result is not None
        # Should be seconds since midnight: 14*3600 + 30*60 + 45 = 52245
        assert result["seconds"] == 52245
        assert result["iso8601"] == "14:30:45"
        assert "2:30:45 p.m." in result["pretty"]

    def test_datetime_with_timezone(self) -> None:
        """Test parsing datetime with timezone info."""
        # Offset is returned as integer seconds
        # -05:00 = -5 hours * 3600 seconds/hour = -18000 seconds
        result = parse_datetime("2025-01-15T14:30:00-05:00")
        assert result is not None
        assert "seconds" in result
        assert "offset" in result
        assert result["offset"] == -18000

    def test_pretty_format_date_only(self) -> None:
        """Test CMOS formatting for date-only."""
        result = parse_datetime("10/11/2025")
        assert result is not None
        pretty = result["pretty"]
        # Should contain day of week, month name, day, year
        assert "October" in pretty
        assert "11" in pretty
        assert "2025" in pretty
        # Should NOT contain time
        assert "a.m." not in pretty
        assert "p.m." not in pretty

    def test_pretty_format_with_time(self) -> None:
        """Test CMOS formatting for datetime."""
        result = parse_datetime("10/11/2025 1:45 PM")
        assert result is not None
        pretty = result["pretty"]
        # Should contain date and time
        assert "October" in pretty
        assert "2025" in pretty
        assert "1:45 p.m." in pretty

    def test_pretty_format_time_only(self) -> None:
        """Test CMOS formatting for time-only."""
        result = parse_datetime("2:45 PM")
        assert result is not None
        pretty = result["pretty"]
        # Should only contain time
        assert "2:45 p.m." in pretty
        # Should NOT contain date elements
        assert "2025" not in pretty

    def test_invalid_input(self) -> None:
        """Test handling of invalid date strings."""
        result = parse_datetime("not a date")
        assert result is None

        result = parse_datetime("")
        assert result is None

        result = parse_datetime("99/99/9999")
        assert result is None

    def test_midnight_edge_case(self) -> None:
        """Test handling of midnight time."""
        result = parse_datetime("00:00")
        assert result is not None
        assert result["seconds"] == 0
        assert "12:00 a.m." in result["pretty"]

        result = parse_datetime("12:00 AM")
        assert result is not None
        assert result["seconds"] == 0
        assert "12:00 a.m." in result["pretty"]

    def test_noon_edge_case(self) -> None:
        """Test handling of noon time."""
        result = parse_datetime("12:00 PM")
        assert result is not None
        # Noon is 12*3600 = 43200 seconds since midnight
        assert result["seconds"] == 43200
        assert "12:00 p.m." in result["pretty"]


class TestParseDateToEpoch:
    """Test parse_date_to_epoch legacy function."""

    def test_legacy_function_returns_seconds(self) -> None:
        """Test that legacy function returns seconds value."""
        result = parse_date_to_epoch("2025-01-15")
        assert result is not None
        assert isinstance(result, int)

    def test_legacy_function_with_invalid_input(self) -> None:
        """Test legacy function with invalid input."""
        result = parse_date_to_epoch("not a date")
        assert result is None

        result = parse_date_to_epoch("")
        assert result is None
