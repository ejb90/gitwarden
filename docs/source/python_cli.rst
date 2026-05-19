Python Package CLI
==================

Gitconductor can inspect and operate on Python packages inside a cloned GitLab
hierarchy. A repository is treated as a Python package when it contains
``pyproject.toml`` or ``setup.py``.

Generate Requirements
---------------------

Generate a ``requirements.txt`` file containing direct references to each Python
package in the current hierarchy:

.. code-block:: bash

   gitconductor py-requirements

By default, Gitconductor will not overwrite an existing output file. Use
``--force`` to overwrite it:

.. code-block:: bash

   gitconductor py-requirements --force

Choose a different output file:

.. code-block:: bash

   gitconductor py-requirements --fname model-requirements.txt

Generate a ``pyproject.toml``-style dependencies snippet:

.. code-block:: bash

   gitconductor py-requirements --pyproject

Install Packages
----------------

Install every Python package in the current hierarchy into the active Python
environment:

.. code-block:: bash

   gitconductor py-installer

Install packages in editable mode:

.. code-block:: bash

   gitconductor py-installer --editable

Use a different package manager command:

.. code-block:: bash

   gitconductor py-installer --package-manager "python -m pip"

Install from a specific package index:

.. code-block:: bash

   gitconductor py-installer --index https://example.com/simple

Build Wheels
------------

Build wheels for each Python package in the current hierarchy:

.. code-block:: bash

   gitconductor py-wheel
