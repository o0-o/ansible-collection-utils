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

"""Unit tests for hostname parsing utilities."""

from __future__ import annotations

from typing import Any, Dict, Iterable

import pytest

pytest.importorskip("dns.name")
pytest.importorskip("idna")
pytest.importorskip("tldextract")

from ansible_collections.o0_o.utils.plugins.module_utils import (  # noqa: E402
    hostname_utils as host_utils,
)

pytestmark = pytest.mark.skipif(
    host_utils._TLD_EXTRACTOR is None,
    reason="tldextract extractor unavailable",
)

parse_hostname = host_utils.parse_hostname
generate_random_hostname = host_utils.generate_random_hostname


@pytest.mark.parametrize(
    "value,expected,absent,compliant",
    [
        (
            "localhost",
            {"short": "localhost", "labels": ["localhost"]},
            ["long", "domain", "tld", "fqdn", "etld", "registered", "ascii"],
            True,
        ),
        (
            "server.local",
            {
                "short": "server",
                "long": "server.local",
                "domain": "local",
                "tld": "local",
                "labels": ["server", "local"],
            },
            ["fqdn", "ascii"],
            True,
        ),
        (
            "www.example.com",
            {
                "short": "www",
                "long": "www.example.com",
                "domain": "example.com",
                "tld": "com",
                "fqdn": "www.example.com",
                "etld": "com",
                "registered": "example.com",
                "labels": ["www", "example", "com"],
            },
            ["ascii"],
            True,
        ),
        (
            "www.example.com.",
            {
                "long": "www.example.com",
                "fqdn": "www.example.com",
                "labels": ["www", "example", "com"],
            },
            [],
            True,
        ),
        (
            "пример.рф",
            {
                "short": "пример",
                "long": "пример.рф",
                "domain": "рф",
                "ascii": "xn--e1afmkfd.xn--p1ai",
                "tld": "xn--p1ai",
                "etld": "рф",
                "registered": "пример.рф",
                "labels": ["xn--e1afmkfd", "xn--p1ai"],
            },
            [],
            True,
        ),
        (
            "xn--e1afmkfd.xn--p1ai",
            {
                "long": "пример.рф",
                "ascii": "xn--e1afmkfd.xn--p1ai",
                "labels": ["xn--e1afmkfd", "xn--p1ai"],
            },
            [],
            True,
        ),
    ],
)
def test_parse_hostname_success(
    value: str,
    expected: Dict[str, Any],
    absent: Iterable[str],
    compliant: bool,
) -> None:
    """Verify hostname parsing populates expected fields."""
    result = parse_hostname(value)
    assert result
    for key, val in expected.items():
        assert result.get(key) == val
    for missing in absent:
        assert missing not in result
    assert result["compliance"]["rfc5891"] is compliant


@pytest.mark.parametrize(
    "input_value,expected_short",
    [
        ({"hostname": "server.example.com"}, "server"),
        ({"fqdn": "mail.google.com"}, "mail"),
        ({"long": "www.test.org"}, "www"),
        ({"short": "localhost"}, "localhost"),
    ],
)
def test_parse_hostname_dict_inputs(
    input_value: Dict[str, str], expected_short: str
) -> None:
    """Dict inputs should resolve the first hostname field found."""
    result = parse_hostname(input_value)
    assert result["short"] == expected_short


def test_parse_hostname_pretty_passthrough() -> None:
    """Pretty key should pass through when present in dict input."""
    result = parse_hostname(
        {"hostname": "server.example.com", "pretty": "Main Server"}
    )
    assert result["pretty"] == "Main Server"
    assert "pretty" not in parse_hostname("server.example.com")


@pytest.mark.parametrize("invalid", [123, ["bad"], None])
def test_parse_hostname_invalid_types(invalid: Any) -> None:
    """Unsupported types should raise TypeError from coercion helper."""
    with pytest.raises(TypeError):
        parse_hostname(invalid)


def test_parse_hostname_empty_string() -> None:
    """Empty string inputs should return an empty mapping."""
    assert parse_hostname("") == {}


@pytest.mark.parametrize(
    "hostname,expected_fields",
    [
        (
            "sjc20-bb710_b2b45946-6f13-4bea-9a2a-a9523efe7d5c-"
            "d220b7fdbdbd.local",
            {
                "short": "sjc20-bb710_b2b45946-6f13-4bea-9a2a-"
                "a9523efe7d5c-d220b7fdbdbd",
                "domain": "local",
                "tld": "local",
            },
        ),
        (
            "server_example.com",
            {
                "short": "server_example",
                "domain": "com",
                "tld": "com",
            },
        ),
    ],
)
def test_parse_hostname_non_compliant(
    hostname: str, expected_fields: Dict[str, str]
) -> None:
    """Invalid characters should mark hostnames as non-compliant."""
    result = parse_hostname(hostname)
    for key, val in expected_fields.items():
        assert result[key] == val
    assert result["compliance"]["rfc5891"] is False


@pytest.mark.parametrize(
    "flag,error_snippet",
    [
        ("HAS_DNS", "dnspython is required"),
        ("HAS_IDNA", "idna is required"),
        ("HAS_TLDEXTRACT", "tldextract is required"),
    ],
)
def test_parse_hostname_missing_dependencies(
    monkeypatch: pytest.MonkeyPatch, flag: str, error_snippet: str
) -> None:
    """Missing optional deps should raise clear ImportError messages."""
    for attr in ("HAS_DNS", "HAS_IDNA", "HAS_TLDEXTRACT"):
        monkeypatch.setattr(host_utils, attr, True)
    monkeypatch.setattr(host_utils, flag, False)
    with pytest.raises(ImportError, match=error_snippet):
        parse_hostname("example.com")


def test_generate_random_hostname_default_length() -> None:
    """Test hostname generation with default length."""
    hostname = generate_random_hostname()
    assert len(hostname) == 16
    assert hostname.islower()
    assert hostname.isalpha()


@pytest.mark.parametrize("length", [1, 5, 8, 16, 32, 64])
def test_generate_random_hostname_custom_length(length: int) -> None:
    """Test hostname generation with various custom lengths."""
    hostname = generate_random_hostname(length)
    assert len(hostname) == length
    assert hostname.islower()
    assert hostname.isalpha()


def test_generate_random_hostname_only_lowercase_letters() -> None:
    """Test that generated hostname contains only lowercase letters."""
    hostname = generate_random_hostname(100)
    # Check each character is lowercase letter
    for char in hostname:
        assert char in "abcdefghijklmnopqrstuvwxyz"


def test_generate_random_hostname_uniqueness() -> None:
    """Test that multiple generated hostnames are unique."""
    # Generate 100 hostnames and verify they're all different
    hostnames = [generate_random_hostname() for i in range(100)]
    # Should be highly unlikely to get duplicates with 16-char
    assert len(set(hostnames)) == 100


def test_generate_random_hostname_rfc_compliant() -> None:
    """Test that generated hostnames are RFC-compliant."""
    hostname = generate_random_hostname()
    # RFC requires hostnames start with letter (not digit)
    assert hostname[0].isalpha()
    # No digits, hyphens, or other characters
    assert hostname.isalpha()
    # All lowercase for consistency
    assert hostname.islower()


def test_generate_random_hostname_invalid_length() -> None:
    """Test that invalid length raises ValueError."""
    with pytest.raises(ValueError, match="length must be at least 1"):
        generate_random_hostname(0)
    with pytest.raises(ValueError, match="length must be at least 1"):
        generate_random_hostname(-1)
