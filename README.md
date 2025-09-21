# o0_o.utils

[![GitHub CI](https://github.com/o0-o/ansible-collection-utils/workflows/CI/badge.svg)](https://github.com/o0-o/ansible-collection-utils/actions)
[![Ansible Galaxy](https://img.shields.io/ansible/collection/v/o0_o/utils.svg?color=brightgreen&label=Ansible%20Galaxy)](https://galaxy.ansible.com/o0_o/utils)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://o0-o.github.io/ansible-collection-utils/)

General-purpose filters and helpers for Ansible automation.

## Overview

The o0_o.utils collection ships reusable data-manipulation filters that other
collections can depend on. Filters convert hostnames into structured facts,
normalize SI/IEC units, and adapt scalar values into consistent list formats.
Full documentation is published at
https://o0-o.github.io/ansible-collection-utils/.

## Installation

```bash
ansible-galaxy collection install o0_o.utils
```

## Dependencies

The hostname filter requires the following optional Python libraries:
- `dnspython`
- `idna`
- `tldextract`

Install them with:
```bash
pip install dnspython idna tldextract
```

## Usage

### Basic Examples

```yaml
- name: Parse a simple hostname
  ansible.builtin.debug:
    msg: "{{ 'server.example.com' | o0_o.utils.hostname }}"

- name: Convert a comma list into items
  ansible.builtin.debug:
    msg: "{{ 'foo,bar,baz' | o0_o.utils.string2items }}"

- name: Normalize a storage value
  ansible.builtin.debug:
    msg: "{{ '20G' | o0_o.utils.si }}"

- name: Ensure loop target is always a list
  vars:
    servers: "{{ inventory_hostname }}"
  ansible.builtin.debug:
    msg: "{{ servers | o0_o.utils.wantlist }}"
```

### Advanced Usage

```yaml
- name: Force binary interpretation of SI values
  ansible.builtin.debug:
    msg: "{{ '10GB' | o0_o.utils.si(binary=true) }}"

- name: Preserve whitespace when splitting values
  ansible.builtin.debug:
    msg: "{{ 'foo, bar , baz' | o0_o.utils.string2items(',', false) }}"

- name: Combine wantlist with loops for flexible input types
  vars:
    targets: "{{ single_host | default(['web01', 'web02']) }}"
  ansible.builtin.include_tasks: ping.yml
  loop: "{{ targets | o0_o.utils.wantlist }}"

- name: Surface parsed hostname metadata
  vars:
    host_info: "{{ {'hostname': 'gateway.local'} | o0_o.utils.hostname }}"
  ansible.builtin.debug:
    msg: "Registered domain is {{ host_info['domain'] | default('n/a') }}"
```

## Plugins

### Action Plugins

- None at this time.

### Modules

- None at this time.

### Roles

- None at this time.

### Filter Plugins

- `hostname`: Parse hostnames into structured dictionaries with compliance
  details and optional ASCII output.
- `si`: Interpret SI/IEC prefixes across capacity, frequency, bandwidth, and
  electrical units, returning normalized values.
- `string2items`: Split delimited strings (or scalars) into lists with control
  over trimming behaviour.
- `wantlist`: Coerce values into lists or singletons based on the ``want_list``
  flag for predictable loop handling.

## Development & Testing

```bash
ansible-test sanity --venv
ansible-test units --venv
ansible-test integration --venv
```

CI runs `black`, `flake8`, and `yamllint` before building the collection; any
lint failure blocks the pipeline, so keep code and YAML formatted locally.

## License

Licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.txt)
or later (GPLv3+)
