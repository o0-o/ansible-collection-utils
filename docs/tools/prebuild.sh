#!/usr/bin/env bash
# GNU General Public License v3.0+
# SPDX-License-Identifier: GPL-3.0-or-later
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Copyright (c) 2025 oØ.o (@o0-o)
#
# This file is part of the o0_o.utils Ansible Collection.

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SOURCE_DIR="${REPO_ROOT}/docs/source"
GENERATED_DIR="${SOURCE_DIR}/generated"

rm -rf "${GENERATED_DIR}"
mkdir -p "${GENERATED_DIR}"
chmod og-w "${GENERATED_DIR}"

pushd "${SOURCE_DIR}" >/dev/null
trap 'popd >/dev/null' EXIT

antsibull-docs \
    --config-file "${SOURCE_DIR}/antsibull-docs.cfg" \
    collection \
    --cleanup everything \
    --use-current \
    --squash-hierarchy \
    --dest-dir "${GENERATED_DIR}" \
    o0_o.utils
