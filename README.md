# o0_o.utils

[![GitHub CI](https://github.com/o0-o/ansible-collection-utils/workflows/CI/badge.svg)](https://github.com/o0-o/ansible-collection-utils/actions)
[![Ansible Galaxy](https://img.shields.io/ansible/collection/v/o0_o/utils.svg?color=brightgreen&label=Ansible%20Galaxy)](https://galaxy.ansible.com/o0_o/utils)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://o0-o.github.io/ansible-collection-utils/)

General utility filters and plugins for Ansible.

## Overview

This collection provides reusable utility filters and plugins that can be used across other Ansible collections and playbooks. It focuses on common data manipulation and transformation tasks.

## Installation

```bash
ansible-galaxy collection install o0_o.utils
```

## Dependencies

This collection requires the following Python libraries for the hostname filter:
- `dnspython` - DNS name parsing and validation
- `idna` - Internationalized domain name support  
- `tldextract` - Accurate TLD extraction using the Public Suffix List

Install them with:
```bash
pip install dnspython idna tldextract
```

## Usage

### Filter Plugins

#### hostname

Parses hostname strings into structured data with various components.

```yaml
- name: Parse FQDN
  debug:
    msg: "{{ 'server.example.com' | o0_o.utils.hostname }}"
  # Returns:
  # {
  #   "short": "server",
  #   "long": "server.example.com",
  #   "domain": "example.com",
  #   "tld": "com",
  #   "etld": "example.com",
  #   "fqdn": "server.example.com",
  #   "list": ["server", "example", "com"]
  # }

- name: Parse simple hostname (single component)
  debug:
    msg: "{{ 'localhost' | o0_o.utils.hostname }}"
  # Returns:
  # {
  #   "short": "localhost",
  #   "list": ["localhost"]
  # }

- name: Parse two-component hostname
  debug:
    msg: "{{ 'server.local' | o0_o.utils.hostname }}"
  # Returns:
  # {
  #   "short": "server",
  #   "long": "server.local",
  #   "domain": "local",
  #   "tld": "local",
  #   "list": ["server", "local"]
  # }

- name: Extract from dict with node_name key
  debug:
    msg: "{{ {'node_name': 'web01.prod.example.com'} | o0_o.utils.hostname }}"
```

The hostname filter returns a dictionary with the following keys (when applicable):
- `short`: First component of the hostname (always present)
- `long`: Full hostname string (2+ components only)
- `domain`: Everything after the first component (2+ components)
- `tld`: Top-level domain - last component (2+ components)
- `etld`: Effective top-level domain - last two components (3+ components only)
- `fqdn`: Fully qualified domain name (3+ components only)
- `pretty`: Passthrough from input dict if present
- `list`: List of all components split on '.' (always present)

#### si

Parses SI (decimal) and IEC (binary) unit prefixes into structured data with byte calculations.

```yaml
- name: Parse size with SI prefix
  debug:
    msg: "{{ '20G' | o0_o.utils.si }}"
  # Returns:
  # {
  #   "bytes": 20000000000,
  #   "pretty": "20 GB",
  #   "value": 20.0,
  #   "prefix": "G",
  #   "base_unit": "B",
  #   "multiplier": 1000000000,
  #   "base": 1000
  # }

- name: Parse with IEC binary prefix
  debug:
    msg: "{{ '5Gi' | o0_o.utils.si }}"
  # Returns:
  # {
  #   "bytes": 5368709120,
  #   "pretty": "5 GiB",
  #   "value": 5.0,
  #   "prefix": "Gi",
  #   "base_unit": "B",
  #   "multiplier": 1073741824,
  #   "base": 1024
  # }

- name: Force binary interpretation
  debug:
    msg: "{{ '10GB' | o0_o.utils.si(binary=true) }}"
  # Returns:
  # {
  #   "bytes": 10737418240,
  #   "pretty": "10 GiB",
  #   "value": 10.0,
  #   "prefix": "Gi",
  #   "base_unit": "B",
  #   "multiplier": 1073741824,
  #   "base": 1024
  # }

- name: Parse frequency units
  debug:
    msg: "{{ '2.4GHz' | o0_o.utils.si }}"
  # Returns:
  # {
  #   "hertz": 2400000000,
  #   "pretty": "2.4 GHz",
  #   "value": 2.4,
  #   "prefix": "G",
  #   "base_unit": "hertz",
  #   "multiplier": 1000000000,
  #   "base": 1000
  # }
```

The si filter supports:
- **SI decimal prefixes**: k/K (kilo), M (mega), G (giga), T (tera), P (peta), E (exa), Z (zetta), Y (yotta), R (ronna), Q (quetta)
- **IEC binary prefixes**: Ki (kibi), Mi (mebi), Gi (gibi), Ti (tebi), Pi (pebi), Ei (exbi), Zi (zebi), Yi (yobi)
- **Automatic byte assumption**: Bare prefixes like "20G" are treated as bytes ("20GB")
- **Unit canonicalization**: Hz→hertz, B→bytes, s→seconds, etc.
- **Binary mode**: Forces SI prefixes to be interpreted as IEC (GB→GiB)
- **Optimized output**: Returns simplified format when optimize=true

#### string2items

Converts delimited strings into lists, useful for parsing comma-separated values or other delimited data.

```yaml
- name: Parse comma-separated string (default)
  debug:
    msg: "{{ 'foo,bar,baz' | o0_o.utils.string2items }}"
  # Returns: ['foo', 'bar', 'baz']

- name: Parse with custom delimiter
  debug:
    msg: "{{ '/usr/bin:/usr/local/bin:/opt/bin' | o0_o.utils.string2items(':') }}"
  # Returns: ['/usr/bin', '/usr/local/bin', '/opt/bin']

- name: Parse with trimming disabled
  debug:
    msg: "{{ 'foo, bar , baz' | o0_o.utils.string2items(',', false) }}"
  # Returns: ['foo', ' bar ', ' baz']

- name: Handles numeric and boolean inputs
  debug:
    msg: "{{ 42 | o0_o.utils.string2items }}"
  # Returns: ['42']
```

Parameters:
- `delimiter`: String to split on (default: ',')
- `trim`: Whether to strip whitespace from items and filter empty items (default: true)

#### wantlist

Ensures values are in list format or simplifies lists to single values based on the `want_list` parameter.

```yaml
- name: Ensure value is a list (default behavior)
  debug:
    msg: "{{ 'single_host' | o0_o.utils.wantlist }}"
  # Returns: ['single_host']

- name: Handle None values
  debug:
    msg: "{{ None | o0_o.utils.wantlist }}"
  # Returns: []

- name: Simplify single-item lists
  debug:
    msg: "{{ ['single_item'] | o0_o.utils.wantlist(false) }}"
  # Returns: 'single_item'

- name: Simplify empty lists
  debug:
    msg: "{{ [] | o0_o.utils.wantlist(false) }}"
  # Returns: None

- name: Use in loops to handle both strings and lists
  command: ping {{ item }}
  loop: "{{ target_hosts | o0_o.utils.wantlist }}"
  vars:
    target_hosts: "{{ single_host | default(host_list) }}"
```

Parameters:
- `want_list`: If true, always return a list. If false, prefer single values (default: true)

The wantlist filter is particularly useful when dealing with variables that might be either a single value or a list, ensuring consistent behavior in loops and conditionals.

## Documentation

- Latest HTML docs: https://o0-o.github.io/ansible-collection-utils/
- Build locally:
  - `pip install -r docs/requirements.txt`
  - `make -C docs html`

## Development & Testing

```bash
# Run sanity tests
ansible-test sanity --venv

# Run unit tests
ansible-test units --venv

# Run integration tests
ansible-test integration --venv
```

## License

Licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.txt) or later (GPLv3+)
