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

"""Base class for lookup plugins that extend vars lookup."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase


class VarsLookupBase(LookupBase):
    """Base class for lookup plugins that need to access variables.

    Provides a convenient lookup_var() method that retrieves variable
    values directly from the templar's available variables. Useful for
    lookup plugins that need to access variables and facts in a
    consistent way.

    Variables are accessed from the templar's available variables,
    which includes facts and all other variables from the play context.
    """

    def lookup_var(
        self,
        var_name: str,
        host: Optional[str] = None,
        **kwargs: Any
    ) -> Any:
        """Look up a variable value from the templar's available variables.

        This method accesses variables directly from the templar's
        available variables, which includes facts and all other variables
        from the play context. Can optionally access variables from a
        specific host's hostvars.

        :param str var_name: Name of the variable to look up
        :param Optional[str] host: Hostname to look up variables for.
            If None, uses current host's variables. If provided, looks
            up variables from hostvars[host]
        :param kwargs: Additional keyword arguments. Supports:
            - default: Default value to return if variable is not found
              or any error occurs. If not provided, raises
              AnsibleLookupError on failure. Can be any value including
              None.
        :returns Any: The variable value or default if provided and
            variable not found
        :raises AnsibleLookupError: If the variable cannot be accessed
            and no default is provided, or if unexpected keyword arguments
            are provided
        """
        # Extract default parameter if provided
        has_default = "default" in kwargs
        default = kwargs.pop("default", None)

        # Validate no unexpected kwargs
        if kwargs:
            unexpected = ", ".join(sorted(kwargs.keys()))
            raise AnsibleLookupError(
                f"lookup_var() got unexpected keyword argument(s): "
                f"{unexpected}"
            )

        # Get all available variables including facts from templar
        try:
            available_vars = self._templar.available_variables

            # If host is specified, look up in hostvars
            if host is not None:
                hostvars = available_vars.get("hostvars")
                if hostvars is None:
                    if has_default:
                        return default
                    raise AnsibleLookupError(
                        f"Cannot access host '{host}' variables: "
                        f"hostvars not available"
                    )
                if host not in hostvars:
                    if has_default:
                        return default
                    raise AnsibleLookupError(
                        f"Host '{host}' not found in hostvars"
                    )
                host_vars = hostvars[host]
                if var_name in host_vars:
                    return host_vars[var_name]
                else:
                    if has_default:
                        return default
                    raise AnsibleLookupError(
                        f"No variable named '{var_name}' found for host '{host}'."
                    )
            # Otherwise use current host's variables
            else:
                if var_name in available_vars:
                    return available_vars[var_name]
                else:
                    if has_default:
                        return default
                    raise AnsibleLookupError(
                        f"No variable named '{var_name}' was found."
                    )
        except AnsibleLookupError:
            if has_default:
                return default
            raise
        except AttributeError as e:
            if has_default:
                return default
            raise AnsibleLookupError(
                f"Failed to access templar's available variables: {e}"
            ) from e
        except Exception as e:
            if has_default:
                return default
            raise AnsibleLookupError(
                f"Failed to access variable '{var_name}': {e}"
            ) from e
