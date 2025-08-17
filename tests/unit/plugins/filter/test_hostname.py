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

from ansible_collections.o0_o.utils.plugins.filter.hostname import FilterModule


@pytest.fixture
def filter_module():
    """Create a FilterModule instance for testing."""
    return FilterModule()


def test_filter_module_filters(filter_module):
    """Test that filters() returns expected filter functions."""
    filters = filter_module.filters()
    assert "hostname" in filters
    assert callable(filters["hostname"])


@pytest.mark.parametrize("hostname,expected", [
    # Single label
    ("localhost", {
        "short": "localhost",
        "labels": ["localhost"],
        "_absent": ["long", "fqdn", "domain", "tld", "etld", "registered"]
    }),
    
    # Two labels
    ("server.local", {
        "short": "server",
        "long": "server.local",
        "domain": "local",
        "tld": "local",
        "labels": ["server", "local"],
        "_absent": ["fqdn", "ascii"]  # No fqdn with only 2 labels
    }),
    
    # Three labels (FQDN)
    ("www.example.com", {
        "short": "www",
        "long": "www.example.com",
        "domain": "example.com",
        "tld": "com",
        "fqdn": "www.example.com",
        "labels": ["www", "example", "com"],
        "etld": "com",
        "registered": "example.com",
        "_absent": ["ascii"]  # No ascii for ASCII-only hostnames
    }),
    
    # Complex public suffix
    ("www.example.co.uk", {
        "short": "www",
        "long": "www.example.co.uk",
        "domain": "example.co.uk",
        "tld": "uk",
        "fqdn": "www.example.co.uk",
        "etld": "co.uk",
        "registered": "example.co.uk",
        "labels": ["www", "example", "co", "uk"]
    }),
    
    # Unicode hostname
    ("пример.рф", {
        "short": "пример",
        "long": "пример.рф",
        "domain": "рф",
        "ascii": "xn--e1afmkfd.xn--p1ai",
        "labels": ["xn--e1afmkfd", "xn--p1ai"]  # ASCII labels
    }),
    
    # Punycode input (converts to Unicode)
    ("xn--e1afmkfd.xn--p1ai", {
        "long": "пример.рф",
        "ascii": "xn--e1afmkfd.xn--p1ai"
    }),
    
    # Trailing dot handling
    ("www.example.com.", {
        "long": "www.example.com",  # No trailing dot
        "fqdn": "www.example.com",  # No trailing dot
        "labels": ["www", "example", "com"]
    }),
    
    # Empty input
    ("", {}),
])
def test_hostname_parsing(filter_module, hostname, expected):
    """Test hostname parsing with various inputs."""
    result = filter_module.hostname(hostname)
    
    # Check expected fields are present with correct values
    for key, value in expected.items():
        if key == "_absent":
            # Check these fields are NOT in result
            for field in value:
                assert field not in result, f"{field} should not be present"
        else:
            assert key in result, f"{key} missing from result"
            assert result[key] == value, f"{key}: expected {value}, got {result[key]}"


@pytest.mark.parametrize("input_dict,expected_short", [
    ({"hostname": "server.example.com"}, "server"),
    ({"fqdn": "mail.google.com"}, "mail"),
    ({"long": "www.test.org"}, "www"),
    ({"short": "localhost"}, "localhost"),
])
def test_dict_input(filter_module, input_dict, expected_short):
    """Test extracting hostname from dict input."""
    result = filter_module.hostname(input_dict)
    assert result["short"] == expected_short


def test_pretty_passthrough(filter_module):
    """Test that pretty field is passed through from input dict."""
    result = filter_module.hostname({
        "hostname": "server.example.com",
        "pretty": "Main Server"
    })
    assert result["pretty"] == "Main Server"
    
    # Pretty should not appear if not in input
    result = filter_module.hostname("server.example.com")
    assert "pretty" not in result


@pytest.mark.parametrize("invalid_input", [
    123,  # Integer
    ["not", "valid"],  # List
    None,  # None
])
def test_invalid_input_types(filter_module, invalid_input):
    """Test that invalid input types raise errors."""
    with pytest.raises(AnsibleFilterError, match="hostname filter accepts"):
        filter_module.hostname(invalid_input)


@pytest.mark.parametrize("invalid_hostname", [
    "server name.com",  # Space not allowed
    "server@example.com",  # @ not allowed
    "server_example.com",  # Underscore not allowed in hostnames
    "-server.com",  # Can't start with hyphen
    "server-.com",  # Can't end with hyphen
])
def test_invalid_hostnames(filter_module, invalid_hostname):
    """Test that invalid hostnames raise errors."""
    with pytest.raises(AnsibleFilterError, match="Invalid"):
        filter_module.hostname(invalid_hostname)


@pytest.mark.parametrize("missing_lib,error_pattern", [
    ("HAS_DNS", "dnspython library is required"),
    ("HAS_IDNA", "idna library is required"),
    ("HAS_TLDEXTRACT", "tldextract library is required"),
])
def test_missing_dependencies(filter_module, monkeypatch, missing_lib, error_pattern):
    """Test that missing dependencies raise appropriate errors."""
    import ansible_collections.o0_o.utils.plugins.filter.hostname as hostname_module
    
    # Keep all libs available except the one being tested
    monkeypatch.setattr(hostname_module, "HAS_DNS", True)
    monkeypatch.setattr(hostname_module, "HAS_IDNA", True)
    monkeypatch.setattr(hostname_module, "HAS_TLDEXTRACT", True)
    
    # Disable the specific library
    monkeypatch.setattr(hostname_module, missing_lib, False)
    
    with pytest.raises(AnsibleFilterError, match=error_pattern):
        filter_module.hostname("example.com")