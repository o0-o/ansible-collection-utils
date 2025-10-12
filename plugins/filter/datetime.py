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

"""Filter plugin for parsing date/time strings to structured format."""

from __future__ import annotations

from typing import Any, Dict, Optional
from ansible.errors import AnsibleFilterError
from ansible_collections.o0_o.utils.plugins.module_utils import parse_datetime


DOCUMENTATION = r"""
---
name: datetime
short_description: Parse date/time strings to structured datetime dict
version_added: "1.5.0"
description:
  - Parse date/time strings in any common format to structured dict
  - Returns dict with seconds, iso8601, offset (if timezone), and pretty
  - Seconds is epoch timestamp for dates, seconds since midnight for time-only
  - Pretty format follows Chicago Manual of Style (CMOS)
  - Only includes precision present in the input string
  - Supports standard formats like MM/DD/YYYY, YYYY-MM-DD, ISO 8601
  - Uses python-dateutil library for robust parsing
options:
  _input:
    description:
      - Date/time string to parse
      - 'Examples: "01/15/2025", "2025-01-15 14:30", "2:45 PM"'
    type: str
    required: true
author:
  - oØ.o (@o0-o)
"""

EXAMPLES = r"""
# Parse date only (no time)
- name: Parse date without time
  ansible.builtin.debug:
    msg: "{{ '01/15/2025' | o0_o.utils.datetime }}"
  # Output:
  # {
  #   "seconds": 1736899200,
  #   "iso8601": "2025-01-15",
  #   "pretty": "Wednesday, January 15, 2025"
  # }

# Parse date with time (no seconds)
- name: Parse date with time
  ansible.builtin.debug:
    msg: "{{ '2025-01-15 14:30' | o0_o.utils.datetime }}"
  # Output:
  # {
  #   "seconds": 1736951400,
  #   "iso8601": "2025-01-15T14:30",
  #   "pretty": "Wednesday, January 15, 2025, 2:30 p.m."
  # }

# Parse date with time and seconds
- name: Parse date with full time
  ansible.builtin.debug:
    msg: "{{ '2025-01-15 14:30:45' | o0_o.utils.datetime }}"
  # Output:
  # {
  #   "seconds": 1736951445,
  #   "iso8601": "2025-01-15T14:30:45",
  #   "pretty": "Wednesday, January 15, 2025, 2:30:45 p.m."
  # }

# Parse with timezone
- name: Parse date with timezone
  ansible.builtin.debug:
    msg: "{{ '2025-01-15T14:30:00-05:00' | o0_o.utils.datetime }}"
  # Output:
  # {
  #   "seconds": 1736969400,
  #   "iso8601": "2025-01-15T14:30:00-05:00",
  #   "offset": -18000,
  #   "pretty": "Wednesday, January 15, 2025, 2:30 p.m. UTC-05:00"
  # }

# Parse time only (no date)
- name: Parse time without date
  ansible.builtin.debug:
    msg: "{{ '2:45 PM' | o0_o.utils.datetime }}"
  # Output:
  # {
  #   "seconds": 53100,
  #   "iso8601": "14:45:00Z",
  #   "pretty": "2:45 p.m."
  # }

# Use in fact processing (like BIOS dates from dmidecode)
- name: Convert BIOS release date
  ansible.builtin.set_fact:
    bios_date: "{{ '06/15/2024' | o0_o.utils.datetime }}"

# Access individual fields
- name: Get just the timestamp
  ansible.builtin.debug:
    msg: "{{ ('01/15/2025' | o0_o.utils.datetime)['seconds'] }}"

- name: Get pretty formatted string
  ansible.builtin.debug:
    msg: "{{ ('01/15/2025 2:45 PM' | o0_o.utils.datetime)['pretty'] }}"
  # Output: "Wednesday, January 15, 2025, 2:45 p.m."

# Handle parsing failures with default
- name: Parse with fallback
  ansible.builtin.set_fact:
    date_value: >-
      {{ date_string | o0_o.utils.datetime | default({}) }}
"""

RETURN = r"""
_value:
  description: Dictionary with datetime fields based on input precision
  type: dict
  returned: when date can be parsed
  contains:
    seconds:
      description: >-
        Unix epoch timestamp for dates, or seconds since midnight
        (0-86399) for time-only input.
      type: int
      returned: always
    iso8601:
      description: >-
        ISO 8601 formatted datetime or time string. Adapts to input
        precision.
      type: str
      returned: always
    offset:
      description: >-
        Timezone offset in seconds from UTC. Negative for west of UTC,
        positive for east. Only present if input includes timezone information.
      type: int
      returned: when timezone present
    pretty:
      description: >-
        CMOS-formatted datetime string. Format adapts to input precision
        (date only, date+time, time-only, with or without timezone).
      type: str
      returned: always
  sample:
    seconds: 1736951400
    iso8601: "2025-01-15T14:30:00"
    pretty: "Wednesday, January 15, 2025, 2:30 p.m."
"""


class FilterModule(object):
    """Ansible filter plugin for datetime parsing."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters for this plugin.

        :returns Dict[str, Any]: Mapping of filter names to callables
        """
        return {"datetime": self.datetime_filter}

    def datetime_filter(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Parse date/time string to structured dict.

        :param str date_str: Date/time string in any common format
        :returns Optional[Dict[str, Any]]: Dict with epoch, iso8601,
            offset (if tz), and pretty fields, or None if parsing fails
        :raises AnsibleFilterError: If required date parsing libraries are
            not available
        """
        try:
            return parse_datetime(date_str)
        except ImportError as e:
            raise AnsibleFilterError(
                f"Date parsing libraries not available: {e}"
            )
        except Exception as e:
            raise AnsibleFilterError(f"Failed to parse date '{date_str}': {e}")
