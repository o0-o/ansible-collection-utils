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

"""Documentation fragment for typeguard runtime type checking."""

from __future__ import annotations


class ModuleDocFragment:
    """Documentation fragment for typeguard requirement."""

    DOCUMENTATION = r"""
requirements:
  - typeguard >= 4.0.0
notes:
  - This collection requires C(typeguard) for runtime type checking.
  - Install with C(pip install 'typeguard>=4.0.0').
"""
