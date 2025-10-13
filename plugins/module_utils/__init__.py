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
)
from ansible_collections.o0_o.utils.plugins.module_utils.dict_utils import (  # noqa: E501
    dict2items,
    items2dict,
    rekey,
)
from ansible_collections.o0_o.utils.plugins.module_utils.date_utils import (  # noqa: E501
    parse_date_to_epoch,
    parse_datetime,
)
from ansible_collections.o0_o.utils.plugins.module_utils.string_utils import (  # noqa: E501
    to_pascal_case,
)

__all__ = [
    "parse_hostname",
    "string2items",
    "wantlist",
    "parse_si",
    "truthy_or_integer",
    "items2dict",
    "dict2items",
    "rekey",
    "parse_date_to_epoch",
    "parse_datetime",
    "to_pascal_case",
]
