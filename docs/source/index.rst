.. meta::
  :antsibull-docs: 2.21.0


.. _plugins_in_o0_o.utils:

O0_O.Utils
==========

Collection version 2.2.0

.. contents::
   :local:
   :depth: 1

Description
-----------

General utility filters and plugins for Ansible.

**Author:**

* oØ.o (@o0-o)

**Supported ansible-core versions:**

* 2.9 or newer

.. ansible-links::

  - title: "Issue Tracker"
    url: "https://github.com/o0-o/ansible-collection-utils/issues"
    external: true
  - title: "Repository (Sources)"
    url: "https://github.com/o0-o/ansible-collection-utils"
    external: true




.. toctree::
    :maxdepth: 1

.. _plugin_index_for_o0_o.utils:

Plugin Index
------------

These are the plugins in the o0_o.utils collection:

.. _filter_plugins_in_o0_o.utils:

Filter Plugins
~~~~~~~~~~~~~~

* :ansplugin:`datetime filter <o0_o.utils.datetime#filter>` -- Parse date/time strings to structured datetime dict
* :ansplugin:`dict2items filter <o0_o.utils.dict2items#filter>` -- Convert dictionary to list of item mappings
* :ansplugin:`hostname filter <o0_o.utils.hostname#filter>` -- Parse and structure hostname strings
* :ansplugin:`items2dict filter <o0_o.utils.items2dict#filter>` -- Convert list of mapping entries to a dictionary
* :ansplugin:`lines2items filter <o0_o.utils.lines2items#filter>` -- Split string input into a list of lines
* :ansplugin:`rekey filter <o0_o.utils.rekey#filter>` -- Change dictionary keys to values of nested fields
* :ansplugin:`si filter <o0_o.utils.si#filter>` -- Parse values with SI or IEC unit prefixes
* :ansplugin:`string2items filter <o0_o.utils.string2items#filter>` -- Convert a delimited string into a list of items
* :ansplugin:`strip_comments filter <o0_o.utils.strip_comments#filter>` -- Remove comments from multiline text
* :ansplugin:`truthy_or_integer filter <o0_o.utils.truthy_or_integer#filter>` -- Interpret input as integer or boolean
* :ansplugin:`unflatten filter <o0_o.utils.unflatten#filter>` -- Convert flat dictionary with delimited keys to nested dict
* :ansplugin:`wantlist filter <o0_o.utils.wantlist#filter>` -- Ensure value is a list or simplify lists

.. toctree::
    :maxdepth: 1
    :hidden:

    datetime_filter
    dict2items_filter
    hostname_filter
    items2dict_filter
    lines2items_filter
    rekey_filter
    si_filter
    string2items_filter
    strip_comments_filter
    truthy_or_integer_filter
    unflatten_filter
    wantlist_filter

.. _lookup_plugins_in_o0_o.utils:

Lookup Plugins
~~~~~~~~~~~~~~

* :ansplugin:`var lookup <o0_o.utils.var#lookup>` -- Look up variable with optional default and host parameters

.. toctree::
    :maxdepth: 1
    :hidden:

    var_lookup
