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

"""
Base class for Ansible action plugins with utility helpers.

This module provides a mixin class with general-purpose utilities for
action plugins, including text normalization, inventory hostname
detection, command timing display, and inter-plugin delegation.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

from ansible_collections.o0_o.utils.plugins.module_utils.typeguard_compat import (  # noqa: E501
    typechecked,
)


class UtilsActionBase:
    """
    Mixin class for Ansible action plugins with general utility helpers.

    This mixin provides cross-cutting helpers that are useful across
    different types of action plugins, regardless of the target system.

    Utilities include:
    - Text normalization (newline handling)
    - Inventory hostname detection for logging
    - Command timing display for debugging
    - Inter-plugin delegation using FQCNs

    Note: @typechecked is applied to methods rather than the class to
    avoid metaclass conflicts when subclasses also inherit from Ansible
    base classes like ActionBase.

    Usage:
        from ansible.plugins.action import ActionBase
        from ansible_collections.o0_o.utils.plugins.module_utils \
            import UtilsActionBase

        class ActionModule(UtilsActionBase, ActionBase):
            def run(self, tmp=None, task_vars=None):
                ...
    """

    @contextmanager
    @typechecked
    def _binary_safe_execution(self) -> Generator[None, None, None]:
        """Context manager to allow non-UTF-8 data in module responses.

        Temporarily disables Ansible's strict UTF-8 response validation,
        allowing binary data to pass through module execution without
        raising deserialization errors.

        This is necessary when reading binary file content via the
        command module, as Ansible's default behavior rejects responses
        containing surrogate characters (used for non-UTF-8 bytes).

        The raw module does not require this workaround as it bypasses
        the module response deserialization layer.

        Usage::

            with self._binary_safe_execution():
                result = self._execute_module(
                    module_name='command',
                    module_args={'_raw_params': f'cat {path}'},
                    task_vars=task_vars,
                )

        :yields: None
        :raises RuntimeError: If ansible.constants has not been imported
        """
        # Verify ansible.constants is available (must be imported by the
        # action plugin since module_utils cannot import it directly)
        if "ansible.constants" not in sys.modules:
            raise RuntimeError(
                "_binary_safe_execution() requires ansible.constants to be "
                "imported. Add 'from ansible import constants' to your "
                "action plugin."
            )

        constants = sys.modules["ansible.constants"]

        original = constants.MODULE_STRICT_UTF8_RESPONSE
        constants.MODULE_STRICT_UTF8_RESPONSE = False
        try:
            yield
        finally:
            constants.MODULE_STRICT_UTF8_RESPONSE = original

    @typechecked
    def _normalize_newlines(self, text: str) -> str:
        """
        Normalize Windows-style line endings to Unix-style.

        Converts CRLF (\\r\\n) to LF (\\n) for consistent parsing
        across platforms. This matches the behavior of the builtin
        command module.

        :param str text: Text with potential CRLF line endings
        :returns str: Text with normalized LF line endings
        """
        return text.replace("\r\n", "\n")

    @typechecked
    def _def_inventory_hostname(
        self, task_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get/define the inventory hostname for log/warning messages.

        Prefers the value from ``task_vars`` when provided, then falls
        back to the task's vars mapping. Defaults to ``localhost`` when
        no value can be determined (e.g., local actions).

        Sets self.inventory_hostname and returns the value.

        :param task_vars: Optional task vars mapping
        :returns str: The inventory hostname or 'localhost' as fallback
        """
        if isinstance(task_vars, dict):
            host = task_vars.get("inventory_hostname")
            if host:
                self.inventory_hostname = str(host)
                return self.inventory_hostname

        try:
            mapping = getattr(self._task, "vars", None)
            if isinstance(mapping, dict):
                host = mapping.get("inventory_hostname")
                if host:
                    self.inventory_hostname = str(host)
                    return self.inventory_hostname
        except Exception:
            pass

        self.inventory_hostname = "localhost"
        return self.inventory_hostname

    @typechecked
    def _display_longest_command(
        self, commands_result: Dict[str, Any], context: str = ""
    ) -> None:
        """Display debug information about the longest running command.

        :param dict commands_result: Result from _run() call
        :param str context: Context description for the debug message
        """
        if not isinstance(commands_result.get("commands"), dict):
            return

        # Find the longest running command
        longest_cmd = None
        longest_elapsed = 0

        for cmd_key, cmd_result in commands_result["commands"].items():
            if "elapsed" in cmd_result:
                elapsed = cmd_result["elapsed"].get("seconds", 0)
                if elapsed > longest_elapsed:
                    longest_elapsed = elapsed
                    longest_cmd = cmd_result.get("cmd", cmd_key)

        context_str = f" ({context})" if context else ""
        if longest_elapsed > 0:
            self._display.vvv(
                f"[{self.inventory_hostname}] Longest command{context_str}: "
                f"{longest_cmd} took {longest_elapsed}s"
            )
        else:
            self._display.vvv(
                f"[{self.inventory_hostname}] All commands{context_str} "
                f"completed in under 1 second"
            )

    @typechecked
    def _run_action(
        self,
        plugin_name: str,
        plugin_args: Dict[str, Any],
        task_vars: Optional[Dict[str, Any]] = None,
        check_mode: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Execute another action plugin using the provided arguments.

        :param str plugin_name: Fully qualified name of the plugin to
            run (e.g. 'ansible.builtin.command')
        :param dict plugin_args: Dictionary of arguments to pass to the
            plugin
        :param Optional[dict] task_vars: Dictionary of task variables
            from the calling task
        :param Optional[bool] check_mode: Override check mode setting
        :returns dict: The result dictionary returned by the plugin's
            run method
        """
        current_fqcn = self._task.action.lower().strip()
        requested_fqcn = plugin_name.lower().strip()

        if requested_fqcn == current_fqcn:
            raise RecursionError(
                f"CompatAction attempted to call '{plugin_name}' from within "
                "itself. This would result in infinite recursion."
            )

        task = self._task.copy()
        task.args.clear()
        task.args.update(plugin_args)

        if getattr(self, "raw", False):
            task.args["raw"] = True

        plugin = self._shared_loader_obj.action_loader.get(
            plugin_name,
            task=task,
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj,
        )

        if plugin is None:
            return self._execute_module(
                module_name=plugin_name,
                module_args=plugin_args,
                task_vars=task_vars,
            )

        if check_mode is not None:
            plugin._task.check_mode = check_mode

        result = plugin.run(task_vars=task_vars)

        # Update raw mode based on delegated plugin's result
        if "raw" in result:
            if getattr(self, "raw", None) == "auto":
                self.raw = result["raw"]
            elif result["raw"]:
                self.raw = True

        return result
