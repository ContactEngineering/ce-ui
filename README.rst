User interface for contact.engineering
======================================

Purpose
-------

This plugin contains the user-facing interface of contact.engineering. It
consists of static HTML files and Vue.js applications.

Installation
------------

For production:

.. code-block:: bash

    pip install ce-ui

For development:

Clone project, enter project directory and run

.. code-block:: bash

    pip install -e .[dev]

Documentation
-------------

- `docs/authentication.rst <docs/authentication.rst>`_ — how users sign in
  (ORCID, Google, email and password), how to obtain credentials for each
  identity provider, and why publishing requires an ORCID iD. This package owns
  the user model and the provider configuration, so this is where sign-in is
  documented; topobank is agnostic of it.
