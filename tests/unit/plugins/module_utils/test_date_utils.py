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

from datetime import timezone, timedelta

from ansible_collections.o0_o.utils.plugins.module_utils import (
    format_elapsed_seconds,
    format_epoch_timestamp,
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
        assert "January 15, 2025" in result["pretty"]
        assert "offset" not in result  # No timezone
        assert "iso8601" not in result

        # YYYY-MM-DD format
        result = parse_datetime("2025-01-15")
        assert result is not None
        assert "seconds" in result

    def test_datetime_without_seconds(self) -> None:
        """Test parsing datetime without seconds."""
        result = parse_datetime("2025-01-15 14:30")
        assert result is not None
        assert "seconds" in result
        assert "2:30 p.m." in result["pretty"]

    def test_datetime_with_seconds(self) -> None:
        """Test parsing datetime with seconds precision."""
        result = parse_datetime("2025-01-15 14:30:45")
        assert result is not None
        assert "seconds" in result
        assert "2:30:45 p.m." in result["pretty"]

    def test_time_only_formats(self) -> None:
        """Test parsing time-only inputs."""
        # 24-hour format
        result = parse_datetime("14:30")
        assert result is not None
        assert "seconds" in result
        # Should be seconds since midnight: 14*3600 + 30*60 = 52200
        assert result["seconds"] == 52200
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
        assert "2:30:45 p.m." in result["pretty"]

    def test_datetime_with_timezone(self) -> None:
        """Test parsing datetime with timezone info."""
        result = parse_datetime("2025-01-15T14:30:00-05:00")
        assert result is not None
        assert "seconds" in result
        assert "offset" not in result  # Offset field removed

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


class TestFormatEpochTimestamp:
    """Test format_epoch_timestamp utility function."""

    def test_format_timestamp_utc_default(self) -> None:
        """Test formatting timestamp with default UTC timezone."""
        # 2025-01-15 15:10:45 UTC
        timestamp = 1736953845.0
        result = format_epoch_timestamp(timestamp)

        assert result["seconds"] == 1736953845
        assert "iso8601" not in result  # Field removed
        assert "offset" not in result  # Field removed
        assert "January 15, 2025" in result["pretty"]
        assert "3:10:45 p.m." in result["pretty"]

    def test_format_timestamp_with_timezone(self) -> None:
        """Test formatting timestamp with custom timezone."""
        # 2025-01-15 15:10:45 UTC = 10:10:45 EST (UTC-5)
        timestamp = 1736953845.0
        est = timezone(timedelta(hours=-5))
        result = format_epoch_timestamp(timestamp, tz=est)

        assert result["seconds"] == 1736953845
        assert "iso8601" not in result  # Field removed
        assert "offset" not in result  # Field removed
        assert "January 15, 2025" in result["pretty"]
        assert "10:10:45 a.m." in result["pretty"]

    def test_format_timestamp_positive_offset(self) -> None:
        """Test formatting timestamp with positive UTC offset."""
        # 2025-01-15 15:10:45 UTC = 02:10:45+11 AEDT (UTC+11)
        timestamp = 1736953845.0
        aedt = timezone(timedelta(hours=11))
        result = format_epoch_timestamp(timestamp, tz=aedt)

        assert result["seconds"] == 1736953845
        assert "iso8601" not in result  # Field removed
        assert "offset" not in result  # Field removed
        assert "January 16, 2025" in result["pretty"]
        assert "2:10:45 a.m." in result["pretty"]

    def test_format_timestamp_with_microseconds(self) -> None:
        """Test formatting timestamp with microseconds."""
        timestamp = 1736953845.123456
        result = format_epoch_timestamp(timestamp, include_microseconds=True)

        assert result["seconds"] == 1736953845
        assert result["microseconds"] == 123456
        assert "pretty" in result

    def test_format_timestamp_without_microseconds(self) -> None:
        """Test that microseconds are not included by default."""
        timestamp = 1736953845.123456
        result = format_epoch_timestamp(timestamp)

        assert result["seconds"] == 1736953845
        assert "microseconds" not in result

    def test_format_timestamp_invalid(self) -> None:
        """Test handling of invalid timestamp."""
        # Very large timestamp that might cause issues
        result = format_epoch_timestamp(9999999999999.0)

        # Should still return seconds even if formatting fails
        assert "seconds" in result


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


class TestFormatElapsedSeconds:
    """Test format_elapsed_seconds utility function."""

    def test_seconds_only(self) -> None:
        """Test formatting seconds-only durations."""
        result = format_elapsed_seconds(45)
        assert result["seconds"] == 45
        assert result["pretty"] == "45 seconds"

    def test_singular_second(self) -> None:
        """Test singular form for 1 second."""
        result = format_elapsed_seconds(1)
        assert result["pretty"] == "1 second"

    def test_minutes_and_seconds(self) -> None:
        """Test formatting minutes and seconds."""
        result = format_elapsed_seconds(2730)  # 45:30
        assert result["seconds"] == 2730
        assert result["pretty"] == "45 minutes, 30 seconds"

    def test_singular_minute(self) -> None:
        """Test singular form for 1 minute."""
        result = format_elapsed_seconds(60)
        assert result["pretty"] == "1 minute"

    def test_hours_minutes_seconds(self) -> None:
        """Test formatting hours, minutes, and seconds."""
        result = format_elapsed_seconds(5025)  # 1:23:45
        assert result["seconds"] == 5025
        assert result["pretty"] == "1 hour, 23 minutes, 45 seconds"

    def test_singular_hour(self) -> None:
        """Test singular form for 1 hour."""
        result = format_elapsed_seconds(3600)
        assert result["pretty"] == "1 hour"

    def test_days_hours_minutes_seconds(self) -> None:
        """Test formatting days, hours, minutes, and seconds."""
        result = format_elapsed_seconds(186312)  # 2-03:45:12
        assert result["seconds"] == 186312
        assert result["pretty"] == "2 days, 3 hours, 45 minutes, 12 seconds"

    def test_singular_day(self) -> None:
        """Test singular form for 1 day."""
        result = format_elapsed_seconds(86400)
        assert result["pretty"] == "1 day"

    def test_zero_seconds(self) -> None:
        """Test formatting zero seconds."""
        result = format_elapsed_seconds(0)
        assert result["seconds"] == 0
        assert result["pretty"] == "0 seconds"

    def test_exact_hour(self) -> None:
        """Test formatting an exact hour with no minutes or seconds."""
        result = format_elapsed_seconds(7200)  # 2 hours
        assert result["pretty"] == "2 hours"

    def test_exact_day(self) -> None:
        """Test formatting an exact day with no other components."""
        result = format_elapsed_seconds(172800)  # 2 days
        assert result["pretty"] == "2 days"

    def test_day_and_seconds_only(self) -> None:
        """Test formatting days and seconds without hours/minutes."""
        result = format_elapsed_seconds(86430)  # 1 day + 30 seconds
        assert result["pretty"] == "1 day, 30 seconds"

    def test_roundtrip_with_parse_elapsed_time(self) -> None:
        """Test format_elapsed_seconds inverts parse_elapsed_time."""
        from ansible_collections.o0_o.utils.plugins.module_utils.date_utils import (  # noqa: E501
            parse_elapsed_time,
        )

        # Test various input strings
        test_cases = ["45:30", "1:23:45", "2-03:45:12", "0:00:01"]
        for elapsed_str in test_cases:
            parsed = parse_elapsed_time(elapsed_str)
            assert parsed is not None
            formatted = format_elapsed_seconds(parsed["seconds"])
            assert formatted["seconds"] == parsed["seconds"]
            assert formatted["pretty"] == parsed["pretty"]
