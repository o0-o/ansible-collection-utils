=========================
o0\_o.utils Release Notes
=========================

.. contents:: Topics

v2.1.0
======

Minor Changes
-------------

- date_utils - Added format_elapsed_seconds() function to convert elapsed time in seconds to human-readable format.
- date_utils - Changed format_epoch_timestamp() to use local system timezone by default instead of UTC for human-readable timestamps (https://github.com/o0-o/ansible-collection-utils/pull/XXX).

v2.0.0
======

Breaking Changes / Porting Guide
--------------------------------

- datetime filter and parse_datetime() function now return simplified dictionaries with only 'seconds', 'pretty', and optionally 'microseconds' fields. The 'iso8601' and 'offset' fields have been removed to reduce output size. Users needing ISO 8601 formatted strings or timezone offsets can generate these on-demand using appropriate filters.

v1.7.0
======

Major Changes
-------------

- Added ``o0_o.utils.var`` lookup plugin for flexible variable lookups with optional ``host`` and ``default`` parameters. The ``host`` parameter allows accessing variables from other hosts' hostvars, while ``default`` provides graceful fallback values when variables are not found.

Minor Changes
-------------

- VarsLookupBase - Added ``default`` parameter to ``lookup_var()`` method for graceful handling of missing variables without raising errors.
- VarsLookupBase - Added ``host`` parameter to ``lookup_var()`` method for cross-host variable lookups via hostvars.
- VarsLookupBase - Added kwargs validation to detect typos and invalid parameters early with clear error messages.
- VarsLookupBase - Changed from ``AnsibleError`` to ``AnsibleLookupError`` for more semantically correct exception handling in lookup plugins.

New Plugins
-----------

Lookup
~~~~~~

- o0_o.utils.var - Look up variable with optional default and host parameters

v1.6.0
======

Minor Changes
-------------

- date_utils.format_epoch_timestamp - Add optional ``tz`` parameter to format timestamps in a specific timezone instead of always using UTC.
- filter.strip_comments - New filter exposing the comment stripping helper to playbooks.
- hostname_utils - Add ``generate_random_hostname()`` function to create cryptographically secure random RFC-compliant hostnames using lowercase letters only, suitable for testing scenarios like SSH client config validation.
- module_utils.string_utils - Added ``strip_comments`` helper using pyparsing to remove comments from multiline text with configurable comment styles.

v1.5.0
======

Minor Changes
-------------

- Added the `o0_o.utils.datetime` filter for parsing date/time strings to structured dicts with seconds (epoch or time-only), iso8601, offset (timezone in seconds, if present), and pretty (CMOS style) fields. Only includes precision present in input.
- Added the `o0_o.utils.dict2items` filter that mirrors the extended behaviour of `items2dict`, supporting the same key fallback logic, default values, and collision handling.
- Added the `o0_o.utils.items2dict` filter with configurable key/value field names (including key fallbacks), collision behaviour, default values, and optional deep combines via the `combine` filter.
- Added the `o0_o.utils.lines2items` filter as a thin wrapper around Python's `splitlines()` for converting multi-line text into lists, with a `splitlines` alias for familiarity.
- Added the `o0_o.utils.rekey` filter that re-keys dictionaries using the shared helpers, including key fallbacks, optional preservation of the original key, default value support, and collision controls.
- Added the `o0_o.utils.truthy_or_integer` filter that prefers integer literals while still handling Ansible boolean strings, plus options to map zero to false and to require positive integers.
- Added the `parse_datetime` utility function in `date_utils` module for flexible date parsing using python-dateutil's internal parser API to detect precision (date-only, time-only, with/without seconds, etc.), returning comprehensive datetime information with adaptive formatting.
- README streamlined to brief overview with links to GitHub Pages docs (antsibull-docs); removed plugin lists and lengthy examples; documented that docs are not versioned and are published continuously by CI.

v1.4.1
======

Minor Changes
-------------

- Switched matrix ansible-test runs to use --docker to ensure consistent containerised environments.
- Updated CI build job to run black, flake8, yamllint, and a quick ansible-test sanity check before building the collection.

v1.4.0
======

Minor Changes
-------------

- Add minimal docstrings to filter methods for consistency.
- Added focused unit coverage for hostname, list, and SI helper utilities alongside slimmer smoke tests for their filter wrappers.
- Introduced a GitHub Pages workflow that builds documentation with antsibull-docs generated sources and Sphinx.
- Refactor filters to import shared logic from module_utils.
- Refined utils filter plugins to expose ``*_filter`` callables and surface native error messages when helper utilities fail.
- Refreshed the collection README with consolidated examples and dependency guidance for the filter helpers.
- Update unit tests to target module_utils directly where appropriate.

v1.3.0
======

Major Changes
-------------

- New ``string2items`` filter for converting delimited strings to lists with configurable delimiters and optional trimming.
- New ``wantlist`` filter to coerce values into lists or scalars based on the ``want_list`` parameter.

Minor Changes
-------------

- Improved dictionary handling in ``wantlist`` to avoid iterating over keys when normalizing values.

v1.2.1
======

Minor Changes
-------------

- Adjusted ``si`` filter output formatting to use consistent decimal precision and trimmed trailing zeros.

v1.2.0
======

Minor Changes
-------------

- ASCII/Punycode results surface only for compliant hostnames and CI-style hostnames with underscores are handled gracefully.
- ``hostname`` filter now reports RFC 5891 compliance instead of raising for non-compliant hostnames and exposes compliance metadata.

v1.1.2
======

Minor Changes
-------------

- Exported ``SiFilter`` in ``__init__`` for streamlined imports and refreshed README badges and CI install steps.

v1.1.1
======

Minor Changes
-------------

- Documented bare prefix behaviour and added Galaxy/CI badges to the README.
- ``si`` filter now treats bare SI/IEC prefixes as bytes for compatibility with common command output.

Bugfixes
--------

- Ensured bare numbers without prefixes return empty dicts to preserve legacy behaviour.

v1.1.0
======

Major Changes
-------------

- Introduced ``si`` filter supporting SI and IEC prefixes, binary interpretation, and pretty output modes.

Minor Changes
-------------

- Centralized lint configuration and tidied formatting across the collection.

v1.0.1
======

Major Changes
-------------

- Added ``__init__.py`` to filter package to enable clean imports.

v1.0.0
======

Major Changes
-------------

- Initial release featuring the ``hostname`` filter with Unicode/IDN support, component extraction, DNS validation, and extensive testing.
