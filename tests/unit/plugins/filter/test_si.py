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

"""Unit tests for si filter plugin."""

from __future__ import annotations

from ansible_collections.o0_o.utils.plugins.filter.si import FilterModule


class TestSiFilter:
    """Test si filter function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.filter_module = FilterModule()
        self.si = self.filter_module.si

    def test_parse_empty_input(self):
        """Test parsing empty input."""
        assert self.si("") == {}
        assert self.si(None) == {}

    def test_parse_cpu_speed(self):
        """Test parsing CPU frequency values."""
        result = self.si("2400MHz")
        assert result["hertz"] == 2400000000
        assert result["pretty"] == "2.4 GHz"  # Optimized to GHz

        result = self.si("3.6GHz")
        assert result["hertz"] == 3600000000
        assert result["pretty"] == "3.6 GHz"

    def test_parse_memory_speed(self):
        """Test parsing memory transfer rates."""
        result = self.si("2133MT/s")
        assert result["transfers/s"] == 2133000000
        assert result["pretty"] == "2.133 GT/s"  # Optimized to GT/s

    def test_parse_memory_size_si(self):
        """Test parsing memory sizes with SI prefixes."""
        result = self.si("32GB")
        assert result["bytes"] == 32000000000
        assert result["pretty"] == "32 GB"

        result = self.si("16MB")
        assert result["bytes"] == 16000000
        assert result["pretty"] == "16 MB"

    def test_parse_memory_size_iec(self):
        """Test parsing memory sizes with IEC binary prefixes."""
        result = self.si("32GiB")
        assert result["bytes"] == 34359738368  # 32 * 2^30
        assert result["pretty"] == "32 GiB"

        result = self.si("16MiB")
        assert result["bytes"] == 16777216  # 16 * 2^20
        assert result["pretty"] == "16 MiB"

    def test_binary_parameter(self):
        """Test binary parameter forces IEC interpretation."""
        # Without binary flag - SI interpretation
        result = self.si("32GB", binary=False)
        assert result["bytes"] == 32000000000
        assert result["pretty"] == "32 GB"

        # With binary flag - IEC interpretation
        result = self.si("32GB", binary=True)
        assert result["bytes"] == 34359738368  # 32 * 2^30
        assert result["pretty"] == "32 GiB"

    def test_no_prefix(self):
        """Test values without prefixes."""
        result = self.si("1600W")
        assert result["watts"] == 1600
        assert result["pretty"] == "1.6 kW"  # Optimized to kW with lowercase k

        result = self.si("5V")
        assert result["v"] == 5
        assert result["pretty"] == "5 V"

    def test_canonical_units(self):
        """Test that base units are normalized to canonical forms."""
        result = self.si("100MHz")
        assert "hertz" in result
        assert "hz" not in result
        assert "Hz" not in result

        result = self.si("10GB")
        assert "bytes" in result
        assert "b" not in result
        assert "B" not in result

    def test_bytes_vs_bits(self):
        """Test case sensitivity for B (bytes) vs b (bits)."""
        # Uppercase B = bytes
        result = self.si("10GB")
        assert result["bytes"] == 10000000000
        assert result["pretty"] == "10 GB"

        # Lowercase b = bits
        result = self.si("10Gb")
        assert result["bits"] == 10000000000
        assert result["pretty"] == "10 Gb"

    def test_kilo_variants(self):
        """Test both lowercase and uppercase kilo prefixes."""
        result = self.si("1kHz")
        assert result["hertz"] == 1000
        assert result["pretty"] == "1 kHz"

        # Uppercase K is accepted but normalized to lowercase k
        result = self.si("1KHz")
        assert result["hertz"] == 1000
        assert result["pretty"] == "1 kHz"  # Normalized to lowercase k

    def test_large_prefixes(self):
        """Test larger SI prefixes."""
        result = self.si("1PB")
        assert result["bytes"] == 1e15
        assert result["pretty"] == "1 PB"

        result = self.si("1EB")
        assert result["bytes"] == 1e18
        assert result["pretty"] == "1 EB"

        result = self.si("1ZB")
        assert result["bytes"] == 1e21
        assert result["pretty"] == "1 ZB"

        result = self.si("1YB")
        assert result["bytes"] == 1e24
        assert result["pretty"] == "1 YB"

        result = self.si("1RB")
        assert result["bytes"] == 1e27
        assert result["pretty"] == "1 RB"

        result = self.si("1QB")
        assert result["bytes"] == 1e30
        assert result["pretty"] == "1 QB"

    def test_large_iec_prefixes(self):
        """Test larger IEC binary prefixes."""
        result = self.si("1PiB")
        assert result["bytes"] == 2**50
        assert result["pretty"] == "1 PiB"

        result = self.si("1EiB")
        assert result["bytes"] == 2**60
        assert result["pretty"] == "1 EiB"

        result = self.si("1ZiB")
        assert result["bytes"] == 2**70
        assert result["pretty"] == "1 ZiB"

        result = self.si("1YiB")
        assert result["bytes"] == 2**80
        assert result["pretty"] == "1 YiB"

    def test_decimal_values(self):
        """Test parsing decimal values."""
        result = self.si("1.5GB")
        assert result["bytes"] == 1500000000
        assert result["pretty"] == "1.5 GB"

        result = self.si("2.4GHz")
        assert result["hertz"] == 2400000000
        assert result["pretty"] == "2.4 GHz"

    def test_spacing_variations(self):
        """Test values with spaces between number and unit."""
        result = self.si("32 GB")
        assert result["bytes"] == 32000000000
        assert result["pretty"] == "32 GB"

        result = self.si("2.4 GHz")
        assert result["hertz"] == 2400000000
        assert result["pretty"] == "2.4 GHz"

    def test_complex_units(self):
        """Test parsing units with special characters."""
        result = self.si("100Mbit/s")
        assert result["bits/s"] == 100000000
        assert result["pretty"] == "100 Mbit/s"

    def test_invalid_input(self):
        """Test invalid input returns empty dict."""
        assert self.si("not a number") == {}
        assert self.si("GB32") == {}
        assert self.si("32") == {}  # No unit

    def test_pretty_optimization(self):
        """Test that pretty field uses optimal prefix."""
        # 1000 Hz should become 1 kHz
        result = self.si("1000Hz")
        assert result["hertz"] == 1000
        assert result["pretty"] == "1 kHz"

        # 1000000 Hz should become 1 MHz
        result = self.si("1000000Hz")
        assert result["hertz"] == 1000000
        assert result["pretty"] == "1 MHz"

        # 500 Hz should stay as Hz (no smaller unit)
        result = self.si("500Hz")
        assert result["hertz"] == 500
        assert result["pretty"] == "500 Hz"

        # 1024 B with binary=True should become 1 KiB
        result = self.si("1024B", binary=True)
        assert result["bytes"] == 1024
        assert result["pretty"] == "1 KiB"

        # 1048576 B with binary=True should become 1 MiB
        result = self.si("1048576B", binary=True)
        assert result["bytes"] == 1048576
        assert result["pretty"] == "1 MiB"

    def test_optimize_parameter(self):
        """Test the optimize parameter to preserve original prefix."""
        # With optimize=True (default), should optimize
        result = self.si("2400MHz", optimize=True)
        assert result["hertz"] == 2400000000
        assert result["pretty"] == "2.4 GHz"

        # With optimize=False, should preserve original prefix
        result = self.si("2400MHz", optimize=False)
        assert result["hertz"] == 2400000000
        assert result["pretty"] == "2400 MHz"

        # Another example with memory
        result = self.si("1024KB", optimize=False)
        assert result["bytes"] == 1024000
        assert (
            result["pretty"] == "1024 kB"
        )  # Preserves value, normalizes K to k

        result = self.si("1024KB", optimize=True)
        assert result["bytes"] == 1024000
        assert result["pretty"] == "1.024 MB"  # Optimizes to MB
