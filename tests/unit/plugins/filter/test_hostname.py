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

from __future__ import annotations

import pytest
from ansible.errors import AnsibleFilterError

from ansible_collections.o0_o.utils.plugins.module_utils import (
    hostname_utils as _host_utils,
)


@pytest.fixture
def parse_hostname():
    """Expose parse_hostname from module_utils for testing."""
    return _host_utils.parse_hostname


@pytest.fixture(autouse=True)
def _ensure_hostname_env(monkeypatch):
    """Ensure parse_hostname can run without external libs.

    Patches dependency flags to True and provides a minimal extractor
    that approximates eTLD behavior for these tests.
    """

    class _DummyExtractor:
        def __call__(self, name: str):
            parts = name.split(".") if name else []
            suffix = ""
            top = ""
            if len(parts) >= 2:
                if name.endswith(".co.uk") and len(parts) >= 3:
                    suffix = "co.uk"
                    top = ".".join(parts[-3:])
                else:
                    suffix = parts[-1]
                    top = ".".join(parts[-2:])

            return type(
                "Ext",
                (),
                {
                    "suffix": suffix,
                    "top_domain_under_public_suffix": top,
                },
            )()

    monkeypatch.setattr(_host_utils, "HAS_DNS", True)
    monkeypatch.setattr(_host_utils, "HAS_IDNA", True)
    monkeypatch.setattr(_host_utils, "HAS_TLDEXTRACT", True)
    monkeypatch.setattr(_host_utils, "_TLD_EXTRACTOR", _DummyExtractor())


def test_basic_parse_invocation(parse_hostname):
    """Sanity-check that callable parses a basic hostname."""
    assert parse_hostname("example.com")["long"] == "example.com"


@pytest.mark.parametrize(
    "hostname,expected",
    [
        # Single label
        (
            "localhost",
            {
                "short": "localhost",
                "labels": ["localhost"],
                "_absent": [
                    "long",
                    "fqdn",
                    "domain",
                    "tld",
                    "etld",
                    "registered",
                ],
            },
        ),
        # Two labels
        (
            "server.local",
            {
                "short": "server",
                "long": "server.local",
                "domain": "local",
                "tld": "local",
                "labels": ["server", "local"],
                "_absent": ["fqdn", "ascii"],  # No fqdn with only 2 labels
            },
        ),
        # Three labels (FQDN)
        (
            "www.example.com",
            {
                "short": "www",
                "long": "www.example.com",
                "domain": "example.com",
                "tld": "com",
                "fqdn": "www.example.com",
                "labels": ["www", "example", "com"],
                "etld": "com",
                "registered": "example.com",
                "_absent": ["ascii"],  # No ascii for ASCII-only hostnames
            },
        ),
        # Complex public suffix
        (
            "www.example.co.uk",
            {
                "short": "www",
                "long": "www.example.co.uk",
                "domain": "example.co.uk",
                "tld": "uk",
                "fqdn": "www.example.co.uk",
                "etld": "co.uk",
                "registered": "example.co.uk",
                "labels": ["www", "example", "co", "uk"],
            },
        ),
        # Unicode hostname
        (
            "пример.рф",
            {
                "short": "пример",
                "long": "пример.рф",
                "domain": "рф",
                "ascii": "xn--e1afmkfd.xn--p1ai",
                "labels": ["xn--e1afmkfd", "xn--p1ai"],  # ASCII labels
            },
        ),
        # Punycode input (converts to Unicode)
        (
            "xn--e1afmkfd.xn--p1ai",
            {"long": "пример.рф", "ascii": "xn--e1afmkfd.xn--p1ai"},
        ),
        # Trailing dot handling
        (
            "www.example.com.",
            {
                "long": "www.example.com",  # No trailing dot
                "fqdn": "www.example.com",  # No trailing dot
                "labels": ["www", "example", "com"],
            },
        ),
        # Empty input
        ("", {}),
    ],
)
def test_hostname_parsing(parse_hostname, hostname, expected):
    """Test hostname parsing with various inputs."""
    result = parse_hostname(hostname)

    # Check expected fields are present with correct values
    for key, value in expected.items():
        if key == "_absent":
            # Check these fields are NOT in result
            for field in value:
                assert field not in result, f"{field} should not be present"
        else:
            assert key in result, f"{key} missing from result"
            assert (
                result[key] == value
            ), f"{key}: expected {value}, got {result[key]}"

    # Ensure compliance dict is present for non-empty hostnames
    if hostname:  # Skip compliance check for empty input
        assert "compliance" in result, "compliance field missing"
        assert (
            "rfc5891" in result["compliance"]
        ), "rfc5891 compliance status missing"
        assert (
            result["compliance"]["rfc5891"] is True
        ), "Expected RFC5891 compliant"


@pytest.mark.parametrize(
    "input_dict,expected_short",
    [
        ({"hostname": "server.example.com"}, "server"),
        ({"fqdn": "mail.google.com"}, "mail"),
        ({"long": "www.test.org"}, "www"),
        ({"short": "localhost"}, "localhost"),
    ],
)
def test_dict_input(parse_hostname, input_dict, expected_short):
    """Test extracting hostname from dict input."""
    result = parse_hostname(input_dict)
    assert result["short"] == expected_short


def test_pretty_passthrough(parse_hostname):
    """Test that pretty field is passed through from input dict."""
    result = parse_hostname(
        {"hostname": "server.example.com", "pretty": "Main Server"}
    )
    assert result["pretty"] == "Main Server"

    # Pretty should not appear if not in input
    result = parse_hostname("server.example.com")
    assert "pretty" not in result


@pytest.mark.parametrize(
    "invalid_input",
    [
        123,  # Integer
        ["not", "valid"],  # List
        None,  # None
    ],
)
def test_invalid_input_types(parse_hostname, invalid_input):
    """Test that invalid input types raise errors."""
    with pytest.raises(TypeError, match="hostname input must be str or dict"):
        parse_hostname(invalid_input)


@pytest.mark.parametrize(
    "invalid_hostname",
    [
        "server name.com",  # Space not allowed - non-compliant
        "server@example.com",  # @ not allowed - non-compliant
        "-server.com",  # Can't start with hyphen - non-compliant
        "server-.com",  # Can't end with hyphen - non-compliant
    ],
)
def test_invalid_hostnames(parse_hostname, invalid_hostname):
    """Test that invalid hostnames are marked as non-compliant."""
    # All these hostnames are parseable but non-compliant with RFC5891
    result = parse_hostname(invalid_hostname)
    assert "compliance" in result
    assert result["compliance"]["rfc5891"] is False


@pytest.mark.parametrize(
    "non_compliant_hostname,expected",
    [
        # GitHub Actions runner hostname with underscores
        (
            "sjc20-bb710_b2b45946-6f13-4bea-9a2a-a9523efe7d5c-"
            "D220B7FDBDBD.local",
            {
                "short": "sjc20-bb710_b2b45946-6f13-4bea-9a2a-"
                "a9523efe7d5c-d220b7fdbdbd",
                "long": "sjc20-bb710_b2b45946-6f13-4bea-9a2a-"
                "a9523efe7d5c-d220b7fdbdbd.local",
                "domain": "local",
                "tld": "local",
                "compliance": {"rfc5891": False},
                "_absent": ["ascii", "fqdn"],
            },
        ),
        # Simple hostname with underscore
        (
            "server_example.com",
            {
                "short": "server_example",
                "long": "server_example.com",
                "domain": "com",
                "tld": "com",
                "etld": "com",
                "registered": "server_example.com",
                "compliance": {"rfc5891": False},
                "_absent": ["ascii", "fqdn"],
            },
        ),
    ],
)
def test_non_compliant_hostnames(parse_hostname, non_compliant_hostname, expected):
    """Test non-RFC5891-compliant hostnames are handled gracefully."""
    result = parse_hostname(non_compliant_hostname)

    # Check expected fields are present
    for key, value in expected.items():
        if key == "_absent":
            continue
        assert key in result, f"Missing key: {key}"
        assert (
            result[key] == value
        ), f"Key {key}: expected {value}, got {result[key]}"

    # Check expected absent fields
    if "_absent" in expected:
        for key in expected["_absent"]:
            assert key not in result, f"Key {key} should not be present"

    # Ensure compliance dict is always present
    assert "compliance" in result
    assert "rfc5891" in result["compliance"]
    assert result["compliance"]["rfc5891"] is False


@pytest.mark.parametrize(
    "missing_lib,error_pattern",
    [
        ("HAS_DNS", "dnspython is required"),
        ("HAS_IDNA", "idna is required"),
        ("HAS_TLDEXTRACT", "tldextract is required"),
    ],
)
def test_missing_dependencies(monkeypatch, missing_lib, error_pattern):
    """Test that missing dependencies raise appropriate errors."""
    # Keep all libs available except the one being tested
    monkeypatch.setattr(_host_utils, "HAS_DNS", True)
    monkeypatch.setattr(_host_utils, "HAS_IDNA", True)
    monkeypatch.setattr(_host_utils, "HAS_TLDEXTRACT", True)

    # Disable the specific library
    monkeypatch.setattr(_host_utils, missing_lib, False)

    with pytest.raises(ImportError, match=error_pattern):
        _host_utils.parse_hostname("example.com")


def test_compliant_hostname_with_compliance_field(parse_hostname):
    """Test compliant hostnames have compliance field set correctly."""
    result = parse_hostname("www.example.com")

    # Ensure compliance dict is present and correct
    assert "compliance" in result
    assert "rfc5891" in result["compliance"]
    assert result["compliance"]["rfc5891"] is True

    # Ensure other expected fields are present
    assert result["short"] == "www"
    assert result["long"] == "www.example.com"
    assert result["domain"] == "example.com"
