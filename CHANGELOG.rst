=========================
o0\_o.utils Release Notes
=========================

.. contents:: Topics

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
