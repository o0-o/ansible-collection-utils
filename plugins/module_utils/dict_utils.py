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

"""Shared helpers for items2dict and dict2items filters."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

try:
    from ansible.errors import AnsibleFilterError
except ImportError:  # pragma: no cover - ansible not available in unit tests

    class AnsibleFilterError(Exception):
        """Fallback AnsibleFilterError when ansible is unavailable."""


from ansible.module_utils.common.text.converters import to_native

from ansible_collections.o0_o.utils.plugins.module_utils import wantlist


ITEMS_VALID_COLLISIONS = {"fail", "list", "combine"}


__all__ = [
    "items2dict",
    "dict2items",
    "rekey",
]


def items2dict(
    items: Iterable[Dict[str, Any]],
    key_name: Any = "key",
    value_name: Optional[str] = "value",
    collision: str = "fail",
    reverse_combine_order: bool = False,
    combine_args: Optional[Dict[str, Any]] = None,
    default_value: Any = None,
    allow_empty: bool = True,
    skip_missing_key: bool = False,
) -> Dict[Any, Any]:
    """Convert list of dictionaries into a dictionary.

    Mirrors the behaviour described for the filter implementation while
    remaining reusable in tests and other modules.
    """
    key_candidates = wantlist(key_name, want_list=True)
    if not key_candidates:
        raise AnsibleFilterError(
            "items2dict requires at least one key_name candidate"
        )
    for candidate in key_candidates:
        if not isinstance(candidate, str) or not candidate:
            raise AnsibleFilterError(
                "items2dict key_name entries must be non-empty strings"
            )

    if value_name is not None and not isinstance(value_name, str):
        raise AnsibleFilterError(
            "items2dict 'value_name' parameter must be a string or None"
        )

    collision_mode = (collision or "").lower()
    if collision_mode not in ITEMS_VALID_COLLISIONS:
        raise AnsibleFilterError(
            "items2dict collision must be one of 'fail', 'list', or 'combine'"
        )
    if reverse_combine_order and collision_mode != "combine":
        raise AnsibleFilterError(
            "items2dict reverse_combine_order is only valid when "
            "collision='combine'"
        )

    combine_kwargs = dict(combine_args or {})
    result: Dict[Any, Any] = {}

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise AnsibleFilterError(
                "items2dict expects dictionaries; "
                f"item {index} is {type(item).__name__}"
            )

        key_field: Optional[str] = None
        for candidate in key_candidates:
            if candidate in item:
                key_field = candidate
                break
        if key_field is None:
            if skip_missing_key:
                continue
            raise AnsibleFilterError(
                "items2dict element "
                f"{index} missing key candidates: {', '.join(key_candidates)}"
            )
        key_value = item[key_field]

        if value_name is None:
            value_payload: Any = {
                field: value
                for field, value in item.items()
                if field != key_field
            }
            if (
                not allow_empty
                and isinstance(value_payload, dict)
                and not value_payload
            ):
                value_payload = default_value
            if value_payload is None and default_value is not None:
                value_payload = default_value
            if (
                isinstance(value_payload, dict)
                and value_payload is default_value
            ):
                value_payload = value_payload.copy()
        else:
            value_missing = value_name not in item
            if not value_missing:
                candidate_value = item[value_name]
                if (
                    not allow_empty
                    and isinstance(candidate_value, dict)
                    and not candidate_value
                ):
                    value_missing = True
            value_payload = (
                default_value if value_missing else item[value_name]
            )
            if (
                isinstance(value_payload, dict)
                and value_payload is default_value
            ):
                value_payload = value_payload.copy()

        if collision_mode == "fail":
            if key_value in result:
                raise AnsibleFilterError(
                    f"items2dict duplicate key '{key_value}' encountered"
                )
            result[key_value] = value_payload
            continue

        if collision_mode == "list":
            existing_list = result.setdefault(key_value, [])
            if not isinstance(existing_list, list):
                result[key_value] = existing_list = [existing_list]
            existing_list.append(value_payload)
            continue

        if not isinstance(value_payload, dict):
            raise AnsibleFilterError(
                "items2dict requires dict values when collision='combine'"
            )
        if key_value not in result:
            result[key_value] = value_payload
            continue

        existing_value = result[key_value]
        if not isinstance(existing_value, dict):
            raise AnsibleFilterError(
                "items2dict existing value is not a dict; cannot merge"
            )

        merged = _combine_dicts(
            existing_value,
            value_payload,
            combine_kwargs,
            reverse_combine_order,
        )
        result[key_value] = merged

    return result


def dict2items(
    mapping: Dict[Any, Any],
    key_name: Any = "key",
    value_name: Optional[str] = "value",
    collision: str = "fail",
    default_value: Any = None,
    allow_empty: bool = True,
    skip_missing_key: bool = False,
) -> List[Dict[str, Any]]:
    """Convert dictionaries into list representations."""
    if not isinstance(mapping, dict):
        raise AnsibleFilterError("dict2items requires a dictionary input")

    key_candidates = wantlist(key_name, want_list=True)
    if not key_candidates:
        raise AnsibleFilterError(
            "dict2items requires at least one key_name candidate"
        )
    for candidate in key_candidates:
        if not isinstance(candidate, str) or not candidate:
            raise AnsibleFilterError(
                "dict2items key_name entries must be non-empty strings"
            )

    if value_name is not None and not isinstance(value_name, str):
        raise AnsibleFilterError(
            "dict2items 'value_name' parameter must be a string or None"
        )

    collision_mode = (collision or "").lower()
    if collision_mode not in ITEMS_VALID_COLLISIONS:
        raise AnsibleFilterError(
            "dict2items collision must be one of 'fail', 'list', or 'combine'"
        )

    items: List[Dict[str, Any]] = []
    for key, value in mapping.items():
        if collision_mode == "list":
            items.extend(
                _expand_list_value(
                    key,
                    value,
                    key_candidates,
                    value_name,
                    default_value,
                    allow_empty,
                    skip_missing_key,
                )
            )
            continue

        item = _build_single_item(
            key=key,
            value=value,
            key_candidates=key_candidates,
            value_name=value_name,
            default_value=default_value,
            allow_empty=allow_empty,
            skip_missing_key=skip_missing_key,
        )
        if item is not None:
            items.append(item)

    return items


def _is_empty_mapping(value: Any) -> bool:
    return isinstance(value, dict) and not value


def _build_single_item(
    *,
    key: Any,
    value: Any,
    key_candidates: List[str],
    value_name: Optional[str],
    default_value: Any,
    allow_empty: bool,
    skip_missing_key: bool,
) -> Optional[Dict[str, Any]]:
    """Construct a single output item or return None to skip."""
    if value_name is None:
        processed_value = value
        if processed_value is None or (
            _is_empty_mapping(processed_value) and not allow_empty
        ):
            processed_value = default_value
        if processed_value is None:
            if skip_missing_key:
                return None
        if processed_value is None or not isinstance(processed_value, dict):
            if skip_missing_key:
                return None
            raise AnsibleFilterError(
                "dict2items requires dict values when value_name is None"
            )

        value_dict = processed_value.copy()
        key_field = _select_output_key_field(
            key_candidates, value_dict, key, skip_missing_key
        )
        if key_field is None:
            return None
        existing = value_dict.get(key_field)
        if existing not in (None, key):
            if skip_missing_key:
                return None
            raise AnsibleFilterError(
                f"dict2items cannot assign key '{key_field}'={key!r}; "
                f"existing value {existing!r} conflicts"
            )
        value_dict[key_field] = key
        return value_dict

    processed_value = value
    if processed_value is None or (
        _is_empty_mapping(processed_value) and not allow_empty
    ):
        processed_value = default_value
    if isinstance(processed_value, dict) and processed_value is default_value:
        processed_value = processed_value.copy()

    key_field = key_candidates[0]
    return {key_field: key, value_name: processed_value}


def _expand_list_value(
    key: Any,
    value: Any,
    key_candidates: List[str],
    value_name: Optional[str],
    default_value: Any,
    allow_empty: bool,
    skip_missing_key: bool,
) -> Iterable[Dict[str, Any]]:
    """Expand list values into multiple items."""
    if not isinstance(value, list):
        if skip_missing_key:
            return []
        raise AnsibleFilterError(
            "dict2items collision='list' expects list values"
        )

    expanded: List[Dict[str, Any]] = []
    for index, element in enumerate(value):
        try:
            item = _build_single_item(
                key=key,
                value=element,
                key_candidates=key_candidates,
                value_name=value_name,
                default_value=default_value,
                allow_empty=allow_empty,
                skip_missing_key=skip_missing_key,
            )
        except AnsibleFilterError as exc:
            raise AnsibleFilterError(
                f"dict2items list element {index}: {exc}"
            ) from exc
        if item is not None:
            expanded.append(item)
    return expanded


def _select_output_key_field(
    key_candidates: List[str],
    value_dict: Optional[Dict[str, Any]],
    key: Any,
    skip_missing_key: bool,
) -> Optional[str]:
    """Choose the field used to store the key in output items."""
    if value_dict is None:
        return key_candidates[0]

    for candidate in key_candidates:
        if candidate not in value_dict:
            return candidate
    for candidate in key_candidates:
        if value_dict.get(candidate) == key:
            return candidate

    if skip_missing_key:
        return None

    raise AnsibleFilterError(
        "dict2items could not determine output key field; "
        f"checked: {', '.join(key_candidates)}"
    )


def _combine_dicts(
    existing_value: Dict[str, Any],
    value_payload: Dict[str, Any],
    combine_kwargs: Dict[str, Any],
    reverse: bool,
) -> Dict[str, Any]:
    """Call Ansible's combine filter lazily."""
    try:
        from ansible.plugins.filter.core import combine
    except ImportError as exc:  # pragma: no cover - defensive guard
        raise AnsibleFilterError(
            f"items2dict requires the core combine filter: {to_native(exc)}"
        ) from exc

    if reverse:
        return combine(value_payload, existing_value, **combine_kwargs)
    return combine(existing_value, value_payload, **combine_kwargs)


def _is_effectively_empty(payload: Dict[str, Any]) -> bool:
    if not payload:
        return True
    for value in payload.values():
        if _is_effectively_empty_value(value):
            continue
        return False
    return True


def _is_effectively_empty_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (dict, list, tuple, set)) and not value:
        return True
    return False


def rekey(
    mapping: Dict[Any, Any],
    key_name: Any,
    store_key_as: Optional[Any] = None,
    collision: str = "fail",
    reverse_combine_order: bool = False,
    combine_args: Optional[Dict[str, Any]] = None,
    default_value: Any = None,
    allow_empty: bool = True,
    skip_missing_key: bool = False,
) -> Dict[Any, Any]:
    """Refactor dictionary keys using dict/items helpers."""
    if not isinstance(mapping, dict):
        raise AnsibleFilterError("rekey requires a dictionary input")

    new_key_candidates = wantlist(key_name, want_list=True)
    if not new_key_candidates:
        raise AnsibleFilterError(
            "rekey requires at least one key_name candidate"
        )
    for candidate in new_key_candidates:
        if not isinstance(candidate, str) or not candidate:
            raise AnsibleFilterError(
                "rekey key_name entries must be non-empty strings"
            )

    store_fields: List[str] = []
    if store_key_as is not None:
        store_fields = wantlist(store_key_as, want_list=True)
        if not store_fields:
            raise AnsibleFilterError(
                "rekey store_key_as must provide at least one field when set"
            )
        for field in store_fields:
            if not isinstance(field, str) or not field:
                raise AnsibleFilterError(
                    "rekey store_key_as entries must be non-empty strings"
                )

    if default_value is not None and not isinstance(default_value, dict):
        raise AnsibleFilterError(
            "rekey default_value must be a dictionary when value_name is None"
        )

    result: Dict[Any, Any] = {}
    combine_kwargs = dict(combine_args or {})
    for index, (original_key, value) in enumerate(mapping.items()):
        if not isinstance(value, dict):
            if skip_missing_key:
                continue
            raise AnsibleFilterError(
                "rekey expects dictionary values when value_name is None; "
                f"key {original_key!r} is {type(value).__name__}"
            )

        chosen_field: Optional[str] = None
        for candidate in new_key_candidates:
            if candidate in value:
                chosen_field = candidate
                break
        if chosen_field is None:
            if skip_missing_key:
                continue
            raise AnsibleFilterError(
                f"rekey element {index} missing key candidates: "
                f"{', '.join(new_key_candidates)}"
            )

        new_key_value = value[chosen_field]
        base_payload: Dict[str, Any] = {}
        empty_fields: List[str] = []
        for field, field_value in value.items():
            if field == chosen_field:
                continue
            if _is_effectively_empty_value(field_value):
                empty_fields.append(field)
            else:
                base_payload[field] = field_value

        if not allow_empty:
            value_payload: Dict[str, Any] = base_payload.copy()
            for field in empty_fields:
                if default_value is None:
                    value_payload[field] = {}
                else:
                    value_payload[field] = default_value.copy()
            if not value_payload:
                value_payload = (
                    default_value.copy() if default_value is not None else {}
                )
        else:
            value_payload = base_payload.copy()
            for field in empty_fields:
                value_payload[field] = value.get(field)

        target_field: Optional[str] = None
        for candidate in store_fields:
            if candidate not in value_payload:
                target_field = candidate
                break
        if target_field is None and store_fields:
            target_field = store_fields[0]

        if target_field:
            value_payload[target_field] = original_key

        if collision == "fail":
            if new_key_value in result:
                raise AnsibleFilterError(
                    f"rekey duplicate key '{new_key_value}' encountered"
                )
            result[new_key_value] = value_payload
            continue

        if collision == "list":
            existing = result.setdefault(new_key_value, [])
            if not isinstance(existing, list):
                result[new_key_value] = existing = [existing]
            existing.append(value_payload)
            continue

        if not isinstance(value_payload, dict):
            raise AnsibleFilterError(
                "rekey requires dict values when collision='combine'"
            )

        existing_value = result.get(new_key_value)
        if existing_value is None:
            result[new_key_value] = value_payload
            continue

        if not isinstance(existing_value, dict):
            raise AnsibleFilterError(
                "rekey existing value is not a dict; cannot combine"
            )

        result[new_key_value] = _combine_dicts(
            existing_value,
            value_payload,
            combine_kwargs,
            reverse_combine_order,
        )

    return result
