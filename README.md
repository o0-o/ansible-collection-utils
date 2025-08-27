# o0_o.utils

[![GitHub CI](https://github.com/o0-o/ansible-collection-utils/workflows/CI/badge.svg)](https://github.com/o0-o/ansible-collection-utils/actions)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-o0__o.utils-660198.svg)](https://galaxy.ansible.com/ui/repo/published/o0_o/utils/)

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