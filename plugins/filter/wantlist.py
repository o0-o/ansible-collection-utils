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

"""Ensure value is a list filter."""

from __future__ import annotations

from typing import Any, Dict

from ansible.errors import AnsibleFilterError
from ansible_collections.o0_o.utils.plugins.module_utils.list_utils import (
    wantlist as _wantlist,
)


class FilterModule:
    """Ansible filter plugin."""

    def filters(self) -> Dict[str, Any]:
        """Return available filters for this plugin.

        Wraps the utility to surface errors as AnsibleFilterError for
        clear reporting in play output.

        :returns Dict[str, Any]: Mapping of filter names to callables
        """
        return {"wantlist": self.wantlist}

    def wantlist(self, value: Any, want_list: bool = True) -> Any:
        """Proxy to module_utils.wantlist with Ansible error handling.

        :param value: Value to process
        :param bool want_list: If True, always return a list; else
            prefer single values
        :returns: Processed value
        :raises AnsibleFilterError: On unexpected errors
        """
        try:
            return _wantlist(value, want_list=want_list)
        except Exception as e:
            raise AnsibleFilterError(str(e))
