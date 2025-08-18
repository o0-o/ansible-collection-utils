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

import traceback
from typing import Any, Dict, List, Union

from ansible.errors import AnsibleFilterError


DOCUMENTATION = r"""
---
name: hostname
short_description: Parse and structure hostname strings
version_added: "1.0.0"
description:
  - Parses hostnames into structured components
  - Supports Unicode/IDN hostnames with automatic Punycode conversion
  - Extracts components like short name, domain, TLD, eTLD, and more
options:
  _input:
    description:
      - Hostname string to parse or dict with hostname fields
      - If dict, looks for keys in order (long, fqdn, short, hostname)
    type: raw
    required: true
requirements:
  - dnspython
  - idna
  - tldextract
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
# Parse a simple hostname
- debug:
    msg: "{{ 'www.example.com' | o0_o.utils.hostname }}"
# Returns: {short: www, long: www.example.com, domain: example.com, ...}

# Parse Unicode hostname
- debug:
    msg: "{{ 'münchen.de' | o0_o.utils.hostname }}"
# Returns: {short: münchen, long: münchen.de, ascii: xn--mnchen-3ya.de, ...}

# Parse from dict
- debug:
    msg: "{{ {'hostname': 'server.local'} | o0_o.utils.hostname }}"
"""

RETURN = r"""
short:
  description: First label of the hostname
  type: str
  returned: when hostname has at least one label
long:
  description: Full hostname without trailing dot
  type: str
  returned: when hostname has 2+ labels
domain:
  description: Everything after the first label
  type: str
  returned: when hostname has 2+ labels
tld:
  description: Rightmost label (top-level domain)
  type: str
  returned: when hostname has 2+ labels
fqdn:
  description: Fully qualified domain name
  type: str
  returned: when hostname has 3+ labels
etld:
  description: Effective TLD from Public Suffix List
  type: str
  returned: when found in PSL
registered:
  description: Registered domain (eTLD+1)
  type: str
  returned: when eTLD is found
ascii:
  description: ASCII/Punycode representation
  type: str
  returned: when hostname contains non-ASCII characters
labels:
  description: List of DNS labels (in ASCII form)
  type: list
  returned: always
pretty:
  description: Human-friendly name (passthrough from input dict)
  type: str
  returned: when present in input dict
"""

try:
    import dns.name  # dnspython

    HAS_DNS = True
    DNS_IMPORT_ERROR = None
except ImportError:
    HAS_DNS = False
    DNS_IMPORT_ERROR = traceback.format_exc()

try:
    import idna

    HAS_IDNA = True
    IDNA_IMPORT_ERROR = None
except ImportError:
    HAS_IDNA = False
    IDNA_IMPORT_ERROR = traceback.format_exc()

try:
    import tldextract  # for eTLD/eTLD+1 using the Public Suffix List

    HAS_TLDEXTRACT = True
    TLDEXTRACT_IMPORT_ERROR = None
    # Create extractor with no network access to avoid concurrent
    # fetch issues. Uses only the bundled snapshot of the PSL.
    _TLD_EXTRACTOR = tldextract.TLDExtract(
        suffix_list_urls=None, fallback_to_snapshot=True, cache_dir=False
    )
except ImportError:
    HAS_TLDEXTRACT = False
    TLDEXTRACT_IMPORT_ERROR = traceback.format_exc()
    _TLD_EXTRACTOR = None


class FilterModule:
    """Filter for parsing and processing hostname strings."""

    def filters(self) -> Dict[str, Any]:
        """Return the filter functions."""
        return {"hostname": self.hostname}

    def _coerce_hostname_str(self, data: Union[str, Dict[str, Any]]) -> str:
        """Extract hostname string from various input formats.

        :param data: String hostname or dict with hostname fields
        :returns: Hostname string (lowercase, trimmed)
        :raises AnsibleFilterError: If input format is invalid
        """
        if isinstance(data, dict):
            for key in ("long", "fqdn", "short", "hostname"):
                v = data.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip().lower()
            return ""
        elif isinstance(data, str):
            return data.strip().lower()
        raise AnsibleFilterError("hostname filter accepts a string or a dict")

    def hostname(self, data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Return a structured view of a hostname.

        Output keys:
          - short: first label (always present if at least 1 label)
          - long: input hostname without trailing dot (if >=2 labels)
          - domain: everything after the first label (if >=2 labels)
          - tld: rightmost label (if >=2 labels; NOT a PSL check)
          - etld: effective TLD (public suffix)
          - registered: registered domain - eTLD+1 (eg example.co.uk)
          - fqdn: canonical FQDN without trailing dot (if >=3 labels)
          - ascii: punycode/ASCII form (only if differs from long)
          - labels: list of labels (ASCII; lowercase)
          - pretty: passthrough if present in input dict
        """
        # Check for required dependencies
        if not HAS_DNS:
            raise AnsibleFilterError(
                "The dnspython library is required for the hostname filter. "
                "Install it with: pip install dnspython",
                orig_exc=DNS_IMPORT_ERROR,
            )
        if not HAS_IDNA:
            raise AnsibleFilterError(
                "The idna library is required for the hostname filter. "
                "Install it with: pip install idna",
                orig_exc=IDNA_IMPORT_ERROR,
            )
        if not HAS_TLDEXTRACT:
            raise AnsibleFilterError(
                "The tldextract library is required for the hostname filter. "
                "Install it with: pip install tldextract",
                orig_exc=TLDEXTRACT_IMPORT_ERROR,
            )

        raw = self._coerce_hostname_str(data)
        if not raw:
            return {}

        # Track if hostname is absolute (has trailing dot)
        is_abs = raw.endswith(".")

        # For IDNA, we need to work without the trailing dot
        hostname_no_dot = raw[:-1] if is_abs else raw

        # IDNA encode/decode to validate and normalize Unicode names
        try:
            # IDNA round-trip for strict validation & normalization
            ascii_name = idna.encode(hostname_no_dot).decode("ascii")
            unicode_name = idna.decode(ascii_name.encode("ascii"))
        except Exception as e:
            raise AnsibleFilterError(f"Invalid IDN hostname: {e}")

        # Parse and validate labels with dnspython
        labels: List[str]
        try:
            n = dns.name.from_text(unicode_name)
        except Exception as e:
            raise AnsibleFilterError(f"Invalid hostname: {e}")
        # `n.labels` are bytes; last label b'' if absolute
        # Normalize to ASCII labels (punycode) for stable keys
        byte_labels = list(n.labels)
        # Remove empty label at end if present (absolute name)
        if byte_labels and byte_labels[-1] == b"":
            byte_labels = byte_labels[:-1]
        labels = [lbl.decode("utf-8", errors="strict") for lbl in byte_labels]

        # Also get the unicode labels for display
        unicode_labels = unicode_name.split(".")

        # Assemble result
        result: Dict[str, Any] = {
            "labels": labels,  # ASCII labels for stable keys
        }

        if labels:
            # Use unicode label for short, not ASCII
            result["short"] = unicode_labels[0]
            if len(labels) >= 2:
                # unicode version without trailing dot
                result["long"] = unicode_name
                # Only include ascii if it differs from long
                if ascii_name != unicode_name:
                    result["ascii"] = ascii_name
                result["domain"] = ".".join(unicode_labels[1:])
                result["tld"] = labels[-1]
            if len(labels) >= 3:
                result["fqdn"] = unicode_name
            # Always extract eTLD and registered domain
            ext = _TLD_EXTRACTOR(unicode_name)
            # ext.suffix is the public suffix (eTLD)
            # ext.registered_domain is eTLD+1
            if ext.suffix:
                result["etld"] = ext.suffix
            if ext.registered_domain:
                result["registered"] = ext.registered_domain

        if isinstance(data, dict) and "pretty" in data:
            result["pretty"] = data["pretty"]

        return result
