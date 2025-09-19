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

from typing import Any, Dict, Union

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.o0_o.utils.plugins.module_utils import parse_hostname


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
  returned: when hostname has non-ASCII and is RFC 5891 compliant
labels:
  description: List of DNS labels (in ASCII form)
  type: list
  returned: always
compliance:
  description: Standards compliance information
  type: dict
  returned: always
  contains:
    rfc5891:
      description: Whether hostname is RFC 5891 (IDNA2008) compliant
      type: bool
pretty:
  description: Human-friendly name (passthrough from input dict)
  type: str
  returned: when present in input dict
"""


class FilterModule:
    """Filter for parsing and processing hostname strings."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters for this plugin.

        :returns Dict[str, Any]: Mapping of filter names to callables
        """
        return {"hostname": self.hostname_filter}

    def hostname_filter(
        self, data: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse a hostname into structured components.

        Delegates to ``module_utils.hostname_utils.parse_hostname`` and
        surfaces errors as
        :class:`ansible.errors.AnsibleFilterError`.

        :param data: Hostname or dict with hostname fields
        :returns Dict[str, Any]: Parsed hostname components
        :raises AnsibleFilterError: On dependency or validation errors
        """
        try:
            return parse_hostname(data)
        except Exception as e:
            raise AnsibleFilterError(
                f"hostname failed: {type(e).__name__}: {to_native(e)}"
            ) from e
