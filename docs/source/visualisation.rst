Visualisation
=============

Gitconductor can print the saved GitLab hierarchy and access information in
several Rich-powered terminal views.

Tree
----

Print the group and project hierarchy as a tree:

.. code-block:: bash

   gitconductor viz tree

Example output:

.. code-block:: text

   ejb90-group
   └── models
       ├── model-a
       ├── model-b
       ├── model-c
       └── subgroup-1
           ├── model-a
           └── model-b

Table
-----

Print projects and groups in a table:

.. code-block:: bash

   gitconductor viz table

Limit traversal depth:

.. code-block:: bash

   gitconductor viz table --maxdepth 1

Access
------

Show who has access to a hierarchy:

.. code-block:: bash

   gitconductor viz access

Show each individual user for each subgroup and project:

.. code-block:: bash

   gitconductor viz access --explicit

Show access as a matrix of users against groups and projects:

.. code-block:: bash

   gitconductor viz access --matrix

Limit access traversal depth:

.. code-block:: bash

   gitconductor viz access --maxdepth 1
