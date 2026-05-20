Configuration
=============

GitLab Access
-------------

Gitconductor uses a GitLab Personal Access Token to read groups, projects, and
repository metadata.

.. include:: ../../gitconductor/_data/snippets/gitlab_token_steps.md
   :parser: myst_parser.sphinx_

You can pass the token via an environment variable:

.. include:: ../../gitconductor/_data/snippets/token_env.md
   :parser: myst_parser.sphinx_

Settings File
-------------

Gitconductor can load settings from a TOML file. By default, the CLI looks for:

.. code-block:: text

   ~/.config/gitconductor/gitconductor.toml

You can override this path with ``GITCONDUCTOR_CONFIG`` or the top-level
``--cfg`` option.

Example:

.. code-block:: toml

   gitconductor_gitlab_api_key = "glpat-..."

Environment Variables
---------------------

``GITCONDUCTOR_CONFIG``
   Path to the Gitconductor TOML settings file.

``GITCONDUCTOR_GITLAB_API_KEY``
   GitLab Personal Access Token.

Saved Hierarchy State
---------------------

After ``gitconductor clone`` runs, Gitconductor writes a ``.gitconductor.pkl``
state file at the top of the cloned hierarchy. Later recursive commands load
that state and infer the current group, subgroup, or project from the current
working directory.

Use ``--state`` when you need to point a command at a specific saved hierarchy
state file.
