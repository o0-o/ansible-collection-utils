o0_o.utils Changelog
====================

v1.3.0
------

Minor Changes
~~~~~~~~~~~~~
- New ``string2items`` filter for converting delimited strings to lists.
- Support for configurable delimiters and optional whitespace trimming.
- Automatic conversion of scalar types (numbers, booleans) to strings.
- New ``wantlist`` filter for ensuring values are lists or single values.
- Handles None, strings, dicts, and various iterables appropriately.
- Includes ``want_list`` parameter to control output format.
- Both filters include comprehensive unit and integration tests.
- Added proper handling of dictionaries in ``wantlist`` to prevent iterating over keys when converting to list.

v1.2.1
------

Minor Changes
~~~~~~~~~~~~~
- Improved ``si`` filter output formatting to use consistent decimal precision (2 decimal places with trailing zeros removed).
- Updated unit tests to match correct filter behavior.

v1.2.0
------

Minor Changes
~~~~~~~~~~~~~
- ``hostname`` filter now handles non-RFC5891-compliant hostnames gracefully instead of raising errors.
- Added compliance dict with ``rfc5891`` boolean field to indicate whether hostname meets RFC 5891 (IDNA2008) standards.
- ASCII/Punycode field is now only included for RFC5891-compliant hostnames with non-ASCII characters.
- Hostnames with underscores (common in CI environments like GitHub Actions) are now parseable but marked as non-compliant.
- Updated unit and integration tests to validate compliance field.

v1.1.2
------

Minor Changes
~~~~~~~~~~~~~
- Export ``SiFilter`` in filter module ``__init__`` for cleaner imports.
- Allows importing as ``from ...filter import SiFilter`` instead of requiring full module path.
- Updated Ansible Galaxy badge to display version number with proper title casing.
- Added collection dependency installation to CI workflow.

v1.1.1
------

Minor Changes
~~~~~~~~~~~~~
- ``si`` filter now automatically treats bare SI/IEC prefixes (e.g., ``20G``, ``5M``) as bytes, making it compatible with common command output from tools like df, du, and free.
- Improved regex parsing in ``si`` filter for better prefix detection.
- Added comprehensive documentation and examples for bare prefix behavior.
- Added GitHub CI and Ansible Galaxy badges to README.

Bugfixes
~~~~~~~~
- Fixed ``si`` filter to preserve original behavior where bare numbers without prefix or unit return empty dict.

v1.1.0
------

Minor Changes
~~~~~~~~~~~~~
- New ``si`` filter for parsing SI and IEC unit prefixes.
- Support for decimal SI prefixes (kilo to quetta, 10^3 to 10^30).
- Support for binary IEC prefixes (kibi to yobi, 2^10 to 2^80).
- Unit canonicalization (Hz -> hertz, B -> bytes, etc.).
- Binary mode for interpreting SI prefixes as IEC (GB -> GiB).
- Optimize parameter for pretty output formatting.
- Comprehensive unit tests with 26 test cases.
- Integration tests covering all major functionality.
- Centralized test requirements structure with symlinks.
- Added linter configuration files (``.yamllint``, ``pyproject.toml``).
- Improved code formatting compliance across the collection.

v1.0.1
------

Minor Changes
~~~~~~~~~~~~~
- Added ``__init__.py`` to filter plugin directory for improved import functionality.

v1.0.0
------

Minor Changes
~~~~~~~~~~~~~
- Initial release of the ``o0_o.utils`` Ansible Collection.
- New ``hostname`` filter for parsing and structuring hostnames.
- Support for Unicode/IDN hostnames with automatic Punycode conversion.
- Extraction of hostname components (short, long, domain, TLD, eTLD, registered domain, FQDN).
- Label parsing using dnspython for validation.
- Public Suffix List integration via tldextract for accurate eTLD detection.
- Comprehensive unit and integration test coverage.
- CI/CD pipeline using GitHub Actions with Docker-based testing.

