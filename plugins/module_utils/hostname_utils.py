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

import secrets
import string
import traceback
from typing import Any, Dict, List

from ansible_collections.o0_o.utils.plugins.module_utils.typeguard_compat import (  # noqa: E501
    typechecked,
)

try:
    import dns.name  # type: ignore[import-untyped]

    HAS_DNS = True
    DNS_IMPORT_ERROR = None
except Exception:  # pragma: no cover - surfaced to caller
    HAS_DNS = False
    DNS_IMPORT_ERROR = traceback.format_exc()

try:
    import idna  # type: ignore[import-untyped]

    HAS_IDNA = True
    IDNA_IMPORT_ERROR = None
except Exception:  # pragma: no cover - surfaced to caller
    HAS_IDNA = False
    IDNA_IMPORT_ERROR = traceback.format_exc()

try:
    import tldextract  # type: ignore[import-untyped]

    HAS_TLDEXTRACT = True
    TLDEXTRACT_IMPORT_ERROR = None
    _TLD_EXTRACTOR = tldextract.TLDExtract(
        suffix_list_urls=None, fallback_to_snapshot=True, cache_dir=False
    )
except Exception:  # pragma: no cover - surfaced to caller
    HAS_TLDEXTRACT = False
    TLDEXTRACT_IMPORT_ERROR = traceback.format_exc()
    _TLD_EXTRACTOR = None

__all__ = ["parse_hostname", "generate_random_hostname"]


@typechecked
def generate_random_hostname(length: int = 16) -> str:
    """Generate cryptographically secure RFC-compliant hostname.

    Creates a random hostname using lowercase ASCII letters only,
    ensuring RFC compliance by:
    - Starting with a letter (not a digit)
    - Containing only lowercase letters
    - Having specified length (default 16 characters)

    Suitable for use as dummy hostnames in SSH client configuration
    testing (ssh -G) or other scenarios requiring valid but meaningless
    hostnames.

    :param int length: Length of hostname to generate (default 16)
    :returns str: Random lowercase hostname
    :raises ValueError: If length is less than 1
    """
    if length < 1:
        raise ValueError("Hostname length must be at least 1")

    alphabet = string.ascii_lowercase
    return "".join(secrets.choice(alphabet) for i in range(length))


@typechecked
def _coerce_hostname_str(data: Any) -> str:
    """Extract a hostname string from supported inputs.

    Accepts either a string or a dict containing one of the following
    keys (first found wins): ``long``, ``fqdn``, ``short``,
    ``hostname``.

    :param Any data: String hostname or dict with hostname fields.
        Unsupported types raise TypeError.
    :returns: Hostname string (lowercase, trimmed); ``''`` if not found
    :raises TypeError: When input type is unsupported
    """
    if isinstance(data, dict):
        for key in ("long", "fqdn", "short", "hostname"):
            v = data.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip().lower()
        return ""
    if isinstance(data, str):
        return data.strip().lower()
    raise TypeError("hostname input must be str or dict")


@typechecked
def parse_hostname(data: Any) -> Dict[str, Any]:
    """Parse a hostname string into structured components.

    Returns a dict with keys such as ``short``, ``long``, ``domain``,
    ``tld``, ``etld``, ``registered``, ``fqdn``, ``ascii``,
    ``labels`` and ``compliance``.

    This function is dependency-light but expects the following
    optional libraries to be present for full functionality:
    - dnspython (``dns``)
    - idna
    - tldextract

    :param Any data: String hostname or dict with common hostname keys.
        Unsupported types raise TypeError.
    :returns: Parsed components; ``{}`` when input is empty
    :raises ImportError: If required libraries are missing
    :raises TypeError: If input type is unsupported
    """
    if not HAS_DNS:
        raise ImportError(f"dnspython is required: {DNS_IMPORT_ERROR or ''}")
    if not HAS_IDNA:
        raise ImportError(f"idna is required: {IDNA_IMPORT_ERROR or ''}")
    if not HAS_TLDEXTRACT:
        raise ImportError(
            f"tldextract is required: {TLDEXTRACT_IMPORT_ERROR or ''}"
        )

    raw = _coerce_hostname_str(data)
    if not raw:
        return {}

    is_abs = raw.endswith(".")
    hostname_no_dot = raw[:-1] if is_abs else raw

    rfc5891_compliant = True
    ascii_name = None
    try:
        # IDNA round-trip for strict validation and normalization
        ascii_name = idna.encode(hostname_no_dot).decode(
            "ascii"
        )  # type: ignore[name-defined]
        unicode_name = idna.decode(
            ascii_name.encode("ascii")
        )  # type: ignore[name-defined]
    except Exception:
        rfc5891_compliant = False
        unicode_name = hostname_no_dot

    try:
        n = dns.name.from_text(unicode_name)  # type: ignore[name-defined]
    except Exception as e:  # pragma: no cover - depends on inputs
        raise ValueError(f"Invalid hostname: {e}")

    byte_labels = list(n.labels)  # type: ignore[attr-defined]
    if byte_labels and byte_labels[-1] == b"":
        byte_labels = byte_labels[:-1]
    labels: List[str] = [
        lbl.decode("utf-8", errors="strict") for lbl in byte_labels
    ]
    unicode_labels = unicode_name.split(".")

    result: Dict[str, Any] = {
        "labels": labels,
        "compliance": {"rfc5891": rfc5891_compliant},
    }

    if labels:
        result["short"] = unicode_labels[0]
        if len(labels) >= 2:
            result["long"] = unicode_name
            if ascii_name and ascii_name != unicode_name:
                result["ascii"] = ascii_name
            result["domain"] = ".".join(unicode_labels[1:])
            result["tld"] = labels[-1]
        if len(labels) >= 3:
            result["fqdn"] = unicode_name

        ext = _TLD_EXTRACTOR(unicode_name)  # type: ignore[operator]
        if ext.suffix:
            result["etld"] = ext.suffix
        if ext.top_domain_under_public_suffix:
            result["registered"] = ext.top_domain_under_public_suffix

    if isinstance(data, dict) and "pretty" in data:
        result["pretty"] = data["pretty"]

    return result
