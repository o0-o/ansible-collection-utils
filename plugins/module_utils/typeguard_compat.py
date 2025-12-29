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

"""Typeguard import with dependency checking."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

try:
    from typeguard import typechecked

    HAS_TYPEGUARD = True
    TYPEGUARD_IMPORT_ERROR = None
except ImportError:
    HAS_TYPEGUARD = False
    TYPEGUARD_IMPORT_ERROR = (
        "typeguard>=4.0.0 is required for this collection. "
        "Install with: pip install 'typeguard>=4.0.0'"
    )

    F = TypeVar("F", bound=Callable[..., Any])

    def typechecked(func: F) -> F:
        """Wrap function to raise ImportError when called.

        Unlike optional dependencies, typeguard is required. This
        decorator wraps functions so they raise ImportError when
        called, ensuring users install typeguard before using the
        collection.
        """
        from functools import wraps

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            raise ImportError(TYPEGUARD_IMPORT_ERROR)

        return wrapper  # type: ignore[return-value]

__all__ = ["typechecked", "HAS_TYPEGUARD", "TYPEGUARD_IMPORT_ERROR"]
