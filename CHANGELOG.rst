=========================
o0\_o.utils Release Notes
=========================

.. contents:: Topics

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
