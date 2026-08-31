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

"""Unit tests for SI parsing helpers."""

from __future__ import annotations

from typing import Dict

import pytest

from ansible_collections.o0_o.utils.plugins.module_utils import parse_si


@pytest.mark.parametrize(
    "value,kwargs,expected",
    [
        ("2400MHz", {}, {"hertz": 2400000000, "pretty": "2.4 GHz"}),
        ("3.6GHz", {}, {"hertz": 3600000000, "pretty": "3.6 GHz"}),
        ("2133MT/s", {}, {"transfers/s": 2133000000, "pretty": "2.13 GT/s"}),
        ("32GB", {}, {"bytes": 32000000000, "pretty": "32 GB"}),
        ("16MB", {}, {"bytes": 16000000, "pretty": "16 MB"}),
        ("32GiB", {}, {"bytes": 34359738368, "pretty": "32 GiB"}),
        ("16MiB", {}, {"bytes": 16777216, "pretty": "16 MiB"}),
        ("20G", {}, {"bytes": 20000000000, "pretty": "20 GB"}),
        (
            "20G",
            {"binary": True},
            {"bytes": 21474836480, "pretty": "20 GiB"},
        ),
        ("2Ti", {}, {"bytes": 2199023255552, "pretty": "2 TiB"}),
        ("1600W", {}, {"watts": 1600, "pretty": "1.6 kW"}),
        ("5V", {}, {"v": 5, "pretty": "5 V"}),
        ("10Gb", {}, {"bits": 10000000000, "pretty": "10 Gb"}),
    ],
)
def test_parse_si_success(
    value: str, kwargs: Dict[str, bool], expected: Dict[str, object]
) -> None:
    """Verify parse_si returns canonical values for typical inputs."""
    result = parse_si(value, **kwargs)
    assert result != {}
    for key, val in expected.items():
        assert result[key] == val


@pytest.mark.parametrize(
    "value,expected_pretty",
    [
        ("1000Hz", "1 kHz"),
        ("1000000Hz", "1 MHz"),
        ("500Hz", "500 Hz"),
        ("1024B", "1 KiB"),
        ("1048576B", "1 MiB"),
    ],
)
def test_parse_si_pretty_optimization(
    value: str, expected_pretty: str
) -> None:
    """Ensure the pretty field optimizes to sensible prefixes."""
    result = parse_si(value, binary=True if value.endswith("B") else False)
    assert result["pretty"] == expected_pretty


@pytest.mark.parametrize(
    "value,expected_pretty",
    [
        ("2400MHz", "2400 MHz"),
        ("1024KB", "1024 kB"),
    ],
)
def test_parse_si_optimize_false(value: str, expected_pretty: str) -> None:
    """Opt-out should preserve the original prefix in pretty output."""
    result = parse_si(value, optimize=False)
    assert result["pretty"] == expected_pretty


def test_parse_si_canonical_keys() -> None:
    """Units should normalize to canonical dictionary keys."""
    result = parse_si("100MHz")
    assert "hertz" in result
    assert "Hz" not in result
    assert "hz" not in result

    result = parse_si("10GB")
    assert "bytes" in result
    assert "B" not in result


@pytest.mark.parametrize(
    "value",
    ["", None, "not a number", "GB32", "32"],
)
def test_parse_si_invalid_inputs(value: str) -> None:
    """Invalid inputs should return an empty mapping."""
    assert parse_si(value) == {}


def test_parse_si_decimal_rounding() -> None:
    """Decimal values should round to human-friendly strings."""
    result = parse_si("1.5GB")
    assert result["bytes"] == 1500000000
    assert result["pretty"] == "1.5 GB"


def test_parse_si_binary_mode_for_si_prefix() -> None:
    """Binary flag should reinterpret SI prefixes as IEC numbers."""
    result = parse_si("32GB", binary=True)
    assert result["bytes"] == 34359738368
    assert result["pretty"] == "32 GiB"


def test_parse_si_fraction_survives_in_base_units() -> None:
    """A measurement keeps its fraction where the base unit is the
    unit it was printed in.

    "1.2 V" floored to 1 while pretty said 1.2 beside it - the fact
    contradicted itself. A value that lands whole is still an int.
    """
    result = parse_si("1.2 V")
    assert result["v"] == 1.2
    assert isinstance(result["v"], float)
    assert result["pretty"] == "1.2 V"

    whole = parse_si("2 V")
    assert whole["v"] == 2
    assert isinstance(whole["v"], int)


def test_parse_si_counts_stay_integers() -> None:
    """A fractional prefix form that lands whole in base units is a
    count, and a count is an int."""
    result = parse_si("1.5GB")
    assert result["bytes"] == 1500000000
    assert isinstance(result["bytes"], int)
