Git CLI
=======

The git commands operate recursively on the saved GitLab hierarchy. Run them
from the cloned top-level group, a subgroup, or an individual project directory
to narrow the scope.

Clone
-----

Clone a GitLab group or project and save its hierarchy state:

.. code-block:: bash

   gitconductor clone ejb90-group

Clone into a specific directory:

.. code-block:: bash

   gitconductor clone ejb90-group ./work

Clone projects into a flat directory layout:

.. code-block:: bash

   gitconductor clone --flat ejb90-group

Branch
------

Create a branch in each project below the current hierarchy:

.. code-block:: bash

   gitconductor branch my-branch

Checkout
--------

Check out a branch in each project below the current hierarchy:

.. code-block:: bash

   gitconductor checkout my-branch

Add
---

Stage named files in matching projects:

.. code-block:: bash

   gitconductor add README.md pyproject.toml

Stage all unstaged files in all projects:

.. code-block:: bash

   gitconductor add --all

Commit
------

Commit staged changes in each project below the current hierarchy:

.. code-block:: bash

   gitconductor commit -m "Update project metadata"

Status
------

Show working tree status for each project below the current hierarchy:

.. code-block:: bash

   gitconductor status

Push
----

Push each project below the current hierarchy:

.. code-block:: bash

   gitconductor push

Not Yet Implemented
-------------------

``pull`` is planned but not currently implemented.
