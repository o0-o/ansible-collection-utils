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

"""Module utilities for the o0_o.utils collection."""

from __future__ import annotations

from ansible_collections.o0_o.utils.plugins.module_utils.hostname_utils import (  # noqa: E501
    generate_random_hostname,
    parse_hostname,
)
from ansible_collections.o0_o.utils.plugins.module_utils.list_utils import (  # noqa: E501
    string2items,
    wantlist,
)
from ansible_collections.o0_o.utils.plugins.module_utils.si_utils import (  # noqa: E501
    parse_si,
)
from ansible_collections.o0_o.utils.plugins.module_utils.truthy_utils import (  # noqa: E501
    truthy_or_integer,
    truthy_or_string,
)
from ansible_collections.o0_o.utils.plugins.module_utils.dict_utils import (  # noqa: E501
    dict2items,
    items2dict,
    rekey,
    unflatten,
)
from ansible_collections.o0_o.utils.plugins.module_utils.date_utils import (  # noqa: E501
    format_elapsed_seconds,
    format_epoch_timestamp,
    parse_date_to_epoch,
    parse_datetime,
    parse_elapsed_time,
    time,
)
from ansible_collections.o0_o.utils.plugins.module_utils.string_utils import (  # noqa: E501
    strip_comments,
    validate_encoding,
)
from ansible_collections.o0_o.utils.plugins.module_utils.error_utils import (  # noqa: E501
    format_error_message,
)
from ansible_collections.o0_o.utils.plugins.module_utils.vars_lookup_base import (  # noqa: E501
    VarsLookupBase,
)

__all__ = [
    "generate_random_hostname",
    "parse_hostname",
    "string2items",
    "wantlist",
    "parse_si",
    "truthy_or_integer",
    "truthy_or_string",
    "items2dict",
    "dict2items",
    "rekey",
    "unflatten",
    "format_elapsed_seconds",
    "format_epoch_timestamp",
    "parse_date_to_epoch",
    "parse_datetime",
    "parse_elapsed_time",
    "time",
    "strip_comments",
    "validate_encoding",
    "format_error_message",
    "VarsLookupBase",
]
