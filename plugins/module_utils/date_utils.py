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

"""Utilities for parsing and converting date strings."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

try:
    from dateutil import parser as dateutil_parser, tz
    from dateutil.parser import _parser as dateutil_internal_parser

    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False


def parse_datetime(date_str: str) -> Optional[Dict[str, Any]]:
    """Parse a date or time string and report precision details."""
    if not date_str:
        return None

    parsed = _parse_with_dateutil(date_str)
    if parsed is None:
        return None

    dt, raw = parsed

    result: Dict[str, Any] = {}

    if raw.microsecond not in (None, 0):
        result["microseconds"] = raw.microsecond

    iso8601 = _format_iso8601(dt, raw)
    if iso8601 is not None:
        result["iso8601"] = iso8601

    if raw.year is not None:
        result["seconds"] = int(dt.timestamp())
    elif raw.month is not None:
        result["seconds"] = (
            dt
            - dt.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
        ).total_seconds()
    elif raw.day is not None:
        result["seconds"] = (
            dt - dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds()
    else:
        result["seconds"] = (
            dt - dt.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds()

    offset_seconds = _calc_offset_seconds(dt, raw)
    if offset_seconds is not None:
        result["offset"] = offset_seconds

    cmos = _format_cmos(dt, raw)
    if cmos:
        result["pretty"] = cmos

    return result


def _parse_with_dateutil(date_str: str) -> Optional[Tuple[datetime, Any]]:
    """Parse string with python-dateutil and expose raw precision data."""
    if not HAS_DATEUTIL:
        raise ImportError(
            "python-dateutil is required for date parsing. "
            "Install with: pip install python-dateutil"
        )
    raw_parser = dateutil_internal_parser.parser()

    try:
        raw, skipped = raw_parser._parse(date_str)
    except Exception:
        return None

    if raw is None:
        return None

    try:
        dt = dateutil_parser.parse(date_str, fuzzy=False)
    except Exception:
        return None

    # Default to UTC if parser did not detect a timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.UTC)

    return dt, raw


def _calc_offset_seconds(dt: datetime, raw: Any) -> Optional[int]:
    """Determine timezone offset in seconds, if available."""
    if raw.tzoffset is None and raw.tzname is None:
        return None

    if raw.tzoffset is not None:
        return int(raw.tzoffset)

    offset = dt.utcoffset()
    if offset is not None:
        return int(offset.total_seconds())

    return None


def _timezone_suffix(dt: datetime, raw: Any) -> str:
    """Return ISO suffix for timezone offset."""
    offset_seconds = _calc_offset_seconds(dt, raw)
    if offset_seconds is None:
        return None
    if offset_seconds == 0:
        return "Z"
    return _format_offset_value(offset_seconds)


def _format_offset_value(offset_seconds: int) -> str:
    """Convert an offset in seconds to ±HH:MM format."""
    sign = "+" if offset_seconds >= 0 else "-"
    total = abs(offset_seconds)
    hours, remainder = divmod(total, 3600)
    minutes = remainder // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


def _format_tz_name(dt: datetime, raw: Any) -> str:
    """Format timezone name for pretty output."""
    if raw.tzname:
        return raw.tzname

    if dt.tzinfo is not None:
        name = dt.tzname()
        if name:
            return name

    if raw.tzoffset is None:
        return ""

    if raw.tzoffset == 0:
        return "UTC"

    return f"UTC{_format_offset_value(int(raw.tzoffset))}"


def _format_iso8601(dt: datetime, raw: any) -> Optional[str]:
    """Construct ISO representation with the observed precision."""
    date_part: Optional[str] = None

    if raw.year is not None:
        if raw.month is not None:
            if raw.day is not None:
                date_part = f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
            else:
                date_part = f"{dt.year:04d}-{dt.month:02d}"
        else:
            date_part = f"{dt.year:04d}"
    elif raw.month is not None:
        if raw.day is not None:
            date_part = f"--{dt.month:02d}-{dt.day:02d}"
        else:
            date_part = f"--{dt.month:02d}"

    time_part: Optional[str] = None
    if raw.hour is not None and raw.minute is not None:
        if raw.second is not None or raw.microsecond is not None:
            if raw.microsecond is not None:
                time_part = dt.strftime("%H:%M:%S.%f").rstrip("0").rstrip(".")
            else:
                time_part = dt.strftime("%H:%M:%S")
        else:
            time_part = dt.strftime("%H:%M")
        tz_suffix = _timezone_suffix(dt, raw)
        if tz_suffix is not None:
            time_part = f"{time_part}{tz_suffix}"

    if date_part and time_part:
        return f"{date_part}T{time_part}"
    if time_part:
        return time_part
    if date_part:
        return date_part
    return None


def _format_cmos(dt: datetime, raw: Any) -> str:
    """Format datetime in a Chicago Manual of Style inspired form."""
    parts: list[str] = []

    has_year = raw.year is not None
    has_month = raw.month is not None
    has_day = raw.day is not None
    has_weekday = raw.month is not None and raw.day is not None

    has_hour = raw.hour is not None
    has_minute = raw.minute is not None
    has_microsecond = raw.microsecond not in [None, 0]
    has_seconds = raw.second is not None or has_microsecond

    if has_weekday and has_month and has_day and has_year:
        parts.append(
            f"{dt.strftime('%A')}, {dt.strftime('%B')} {dt.day}, {dt.year}"
        )
    else:
        if has_weekday:
            parts.append(dt.strftime("%A"))
        if has_month and has_day:
            if has_year:
                parts.append(f"{dt.strftime('%B')} {dt.day}, {dt.year}")
            else:
                parts.append(f"{dt.strftime('%B')} {dt.day}")
        elif has_month:
            if has_year:
                parts.append(f"{dt.strftime('%B')} {dt.year}")
            else:
                parts.append(dt.strftime("%B"))
        elif has_year and not parts:
            parts.append(str(dt.year))
        elif has_day and not parts:
            parts.append(str(dt.day))

    if has_hour or has_minute or has_seconds:
        hour_24 = dt.hour
        if hour_24 == 0:
            hour_12 = 12
            period = "a.m."
        elif hour_24 < 12:
            hour_12 = hour_24
            period = "a.m."
        elif hour_24 == 12:
            hour_12 = 12
            period = "p.m."
        else:
            hour_12 = hour_24 - 12
            period = "p.m."

        minute_value = dt.minute if (has_minute or has_seconds) else 0

        if has_seconds:
            if has_microsecond:
                second_component = (
                    f"{dt.second:02d}.{raw.microsecond:06d}".rstrip(
                        "0"
                    ).rstrip(".")
                )
            else:
                second_component = f"{dt.second:02d}"
            time_str = (
                f"{hour_12}:{minute_value:02d}:{second_component} {period}"
            )
        elif has_minute:
            time_str = f"{hour_12}:{minute_value:02d} {period}"
        else:
            time_str = f"{hour_12} {period}"

        parts.append(time_str)

    if raw.tzoffset is not None or raw.tzname is not None:
        tz_name = _format_tz_name(dt, raw)
        if tz_name:
            if parts:
                parts[-1] = f"{parts[-1]} {tz_name}"
            else:
                parts.append(tz_name)

    return ", ".join(parts)


def parse_date_to_epoch(date_str: str) -> Optional[int]:
    """Parse date string to Unix epoch timestamp.

    Legacy function maintained for backward compatibility. Use
    parse_datetime() for more comprehensive output.

    :param str date_str: Date string to parse
    :returns Optional[int]: Unix epoch timestamp or None if parsing fails
    :raises ImportError: If python-dateutil is not available
    """
    result = parse_datetime(date_str)
    return result["seconds"] if result else None


def format_epoch_timestamp(
    timestamp: float,
    include_microseconds: bool = False,
    tz: Optional[timezone] = None,
) -> Dict[str, Any]:
    """Format Unix epoch timestamp into structured time dictionary.

    Converts a Unix timestamp (seconds since epoch) into a dictionary
    with the same structure as parse_datetime() returns.

    :param float timestamp: Unix timestamp (seconds since epoch)
    :param bool include_microseconds: Include microseconds in output
    :param Optional[timezone] tz: Timezone for conversion (defaults to
        UTC)
    :returns Dict[str, Any]: Dictionary with 'seconds', 'iso8601',
        'pretty', and 'offset' keys
    """
    result: Dict[str, Any] = {"seconds": int(timestamp)}

    if tz is None:
        tz = timezone.utc

    try:
        dt = datetime.fromtimestamp(timestamp, tz=tz)

        # Calculate offset in seconds from UTC
        utc_offset = dt.utcoffset()
        offset_seconds = int(utc_offset.total_seconds()) if utc_offset else 0

        # Create a mock raw object for formatting functions
        class RawTimestamp:
            def __init__(
                self, dt: datetime, include_micro: bool, offset_sec: int
            ):
                self.year = dt.year
                self.month = dt.month
                self.day = dt.day
                self.hour = dt.hour
                self.minute = dt.minute
                self.second = dt.second
                self.microsecond = dt.microsecond if include_micro else 0
                self.tzoffset = offset_sec
                self.tzname = dt.tzname() or "UTC"

        raw = RawTimestamp(dt, include_microseconds, offset_seconds)

        # Use existing formatting functions
        iso8601 = _format_iso8601(dt, raw)
        if iso8601:
            result["iso8601"] = iso8601

        pretty = _format_cmos(dt, raw)
        if pretty:
            result["pretty"] = pretty

        result["offset"] = offset_seconds

        if include_microseconds and dt.microsecond > 0:
            result["microseconds"] = dt.microsecond

    except (ValueError, OSError):
        # Timestamp out of range or other error - just return seconds
        pass

    return result


def parse_elapsed_time(elapsed_str: str) -> Optional[Dict[str, Any]]:
    """Parse elapsed time string from ps etime format.

    The ps etime format is: [[DD-]HH:]MM:SS

    Examples:
        >>> parse_elapsed_time("45:30")
        {'seconds': 2730, 'pretty': '45 minutes, 30 seconds',
         'iso8601': 'PT45M30S'}
        >>> parse_elapsed_time("1:23:45")
        {'seconds': 5025, 'pretty': '1 hour, 23 minutes, 45 seconds', ...}
        >>> parse_elapsed_time("2-03:45:12")
        {'seconds': 186312, 'pretty': '2 days, 3 hours, 45 minutes, ...}

    :param str elapsed_str: Elapsed time string in ps etime format
    :returns Optional[Dict[str, Any]]: Dict with 'seconds' (int), 'pretty'
        (str), and 'iso8601' (str) keys, or None if parsing fails
    """
    if not elapsed_str:
        return None

    elapsed_str = elapsed_str.strip()
    if not elapsed_str:
        return None

    try:
        days = 0
        hours = 0
        minutes = 0
        seconds = 0

        # Check for days component (DD-HH:MM:SS)
        if "-" in elapsed_str:
            day_part, time_part = elapsed_str.split("-", 1)
            days = int(day_part)
            elapsed_str = time_part

        # Split time components by colon
        time_parts = elapsed_str.split(":")

        if len(time_parts) == 3:
            # HH:MM:SS format
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = int(time_parts[2])
        elif len(time_parts) == 2:
            # MM:SS format
            minutes = int(time_parts[0])
            seconds = int(time_parts[1])
        else:
            # Invalid format
            return None

        # Calculate total seconds
        total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds

        # Build pretty format
        pretty_parts = []
        if days > 0:
            pretty_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            pretty_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            pretty_parts.append(
                f"{minutes} minute{'s' if minutes != 1 else ''}"
            )
        if seconds > 0 or not pretty_parts:
            pretty_parts.append(
                f"{seconds} second{'s' if seconds != 1 else ''}"
            )
        pretty = ", ".join(pretty_parts)

        # Build ISO 8601 duration format (P[n]DT[n]H[n]M[n]S)
        iso_parts = []
        if days > 0:
            iso_parts.append(f"{days}D")

        time_parts_iso = []
        if hours > 0:
            time_parts_iso.append(f"{hours}H")
        if minutes > 0:
            time_parts_iso.append(f"{minutes}M")
        if seconds > 0 or (days == 0 and hours == 0 and minutes == 0):
            time_parts_iso.append(f"{seconds}S")

        if iso_parts or time_parts_iso:
            iso = "P"
            if iso_parts:
                iso += "".join(iso_parts)
            if time_parts_iso:
                iso += "T" + "".join(time_parts_iso)
        else:
            iso = "PT0S"

        return {
            "seconds": total_seconds,
            "pretty": pretty,
            "iso8601": iso,
        }

    except (ValueError, AttributeError):
        return None
