# gitconductor

![tests](https://github.com/ejb90/gitconductor/actions/workflows/test.yml/badge.svg)
[![Coverage](https://codecov.io/gh/ejb90/gitconductor/branch/main/graph/badge.svg)](https://codecov.io/gh/ejb90/gitconductor)
[![License](https://img.shields.io/github/license/ejb90/gitconductor)](LICENCE.md)
![Ruff](https://img.shields.io/badge/code%20style-ruff-261230)
[![Documentation](https://readthedocs.org/projects/gitconductor/badge/?version=latest)](https://gitconductor.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/gitconductor)](https://pypi.org/project/gitconductor/)
[![Python versions](https://img.shields.io/pypi/pyversions/gitconductor)](https://pypi.org/project/gitconductor/)


`gitconductor` is a command-line tool and Python library for managing git operations over *nested GitLab groups* using the official [GitLab Python API](https://python-gitlab.readthedocs.io/en/stable/). It makes it easier to traverse complex group/subgroup hierarchies and perform recursive git operations without submodule interdependencies, while accessing only the subgroups and projects available to the user.

[Documentation](https://gitconductor.readthedocs.io/en/latest/).

# Features

* Recursive group traversal — operate on entire GitLab group trees, not just individual projects
* Git operations across nested groups (clone, pull, status, etc.)
* Unified CLI and Python API
* Built on top of the official GitLab Python API
* Designed for automation, scripting, and bulk maintenance

# Installation

```
pip install gitconductor
```

## GitLab Access

Access to GitLab is controlled via Personal Access Tokens. To generate one:

1. Log in to GitLab.
2. Click your user icon.
3. Click preferences in the dropdown.
4. Click "Personal access tokens" in the left sidebar.
5. Click the "Add new token" button in the top right.
6. Select "legacy".
7. Give it a helpful name.
8. Set the expiry date. For closed systems, the longest permissible time of 1 year is usually easiest.
9. Select the scopes:
    * read_user
    * read_repository
    * read_api
    * write_repository
10. Click the "Generate token" button below.
11. Copy the new token (noting it can't be viewed again after).

# Configuration

## Configuration file

Gitconductor can store settings in a TOML file. By default, this is at `~/.config/gitconductor/gitconductor.toml`. The location can be changed via the `GITCONDUCTOR_CONFIG` environment variable. Alternatively, a path can be passed via the top-level `--cfg` CLI argument.

## Environment Variables

* `GITCONDUCTOR_CONFIG`: Gitconductor configuration TOML file location.
* `GITCONDUCTOR_GITLAB_API_KEY`: GitLab Personal Access Token.
* `GITCONDUCTOR__GITLAB_URL`: GitLab main URL.

## GitLab API Keys

Keys can be set up in two ways:

1. Via an environment variable: `export GITCONDUCTOR_GITLAB_API_KEY=<my-private-key>`
2. Via the `gitconductor.toml` file in the `gitconductor_gitlab_api_key` variable.

# Usage (CLI)

## Clone

To clone a GitLab group at, for example, [https://gitlab.com/ejb90-group](https://gitlab.com/ejb90-group):

```
gitconductor clone ejb90-group
```

## Branch

```
gitconductor branch <name>
```

## Checkout

```
gitconductor checkout <name>
```

## Pull

NOT IMPLEMENTED.

## Visualisation

### Tree

To visualise the hierarchy of Groups/Projects as a Run, run:

```
gitconductor viz tree
```

Results in:

```
ejb90-group
└── models
    ├── model-a
    ├── model-b
    ├── model-c
    └── subgroup-1
        ├── model-a
        └── model-b
```

### Table

To visualise the hierarchy of Groups/Projects as a Table, run:

```
gitconductor viz table
```

Results in:

```
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name          ┃ Tree                                  ┃ Branch ┃ Path                                  ┃ Remote                                                              ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ model-a       │ ejb90-group/models/model-a            │ main   │ ejb90-group/models/model-a            │ git@gitlab.com:ejb90-group/models/model-a.git                       │
│ model-b       │ ejb90-group/models/model-b            │ main   │ ejb90-group/models/model-b            │ git@gitlab.com:ejb90-group/models/model-b.git                       │
│ model-c       │ ejb90-group/models/model-c            │ main   │ ejb90-group/models/model-c            │ git@gitlab.com:ejb90-group/models/model-c.git                       │
│ model-a       │ ejb90-group/models/subgroup-1/model-a │ main   │ ejb90-group/models/subgroup-1/model-a │ git@gitlab.com:ejb90-group/models/subgroup-1/subgroup-1-model-a.git │
│ model-b       │ ejb90-group/models/subgroup-1/model-b │ main   │ ejb90-group/models/subgroup-1/model-b │ git@gitlab.com:ejb90-group/models/subgroup-1/subgroup-1-model-b.git │
└───────────────┴───────────────────────────────────────┴────────┴───────────────────────────────────────┴─────────────────────────────────────────────────────────────────────┘
```

### Access

To see who has access to a given hierarchy of Groups/Projects, run:

```
gitconductor viz access
```

Results in:

```
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Group/Project      ┃ User  ┃ Access Level ┃ Public Email ┃ Expiry ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│ ejb90-group        │ Ellis │ Owner        │              │        │
│ ejb90-group/models │ mobot │ Reporter     │              │        │
└────────────────────┴───────┴──────────────┴──────────────┴────────┘
```

To show access as a matrix of users against groups and projects, run:

```
gitconductor viz access --matrix
```

## Python

Gitconductor can also inspect and manipulate cloned repositories as Python packages. A repository is treated as a Python package when it contains either `pyproject.toml` or `setup.py`. Python commands run recursively from the current Gitconductor group, subgroup, or project, so you can work across a whole clone or narrow the operation by changing into a subgroup directory first.

### Generate Requirements

Generate a `requirements.txt` file containing direct references to each Python package in the repository tree:

```
gitconductor py-requirements
```

By default, Gitconductor writes to `requirements.txt` and will not overwrite an existing file unless `--force` is passed:

```
gitconductor py-requirements --force
```

To choose a different output file:

```
gitconductor py-requirements --fname model-requirements.txt
```

A pyproject.toml-style `dependencies` snippet is also possible with the `--pyproject` argument:

```
gitconductor py-requirements --pyproject
```


### Install Python Packages

Install every Python package in the current GitLab group tree into the active Python environment:

```
gitconductor py-installer
```

By default this runs `uv pip install <path>` for each Python package it finds. To install packages in editable mode:

```
gitconductor py-installer --editable
```

You can pass a different package-manager command with `--package-manager`:

```
gitconductor py-installer --package-manager "python -m pip"
```

To install from a specific package index:

```
gitconductor py-installer --index https://example.com/simple
```

# Usage (Python API)

```
group = gitlab.GitlabGroup(
    gitlab_url=ctx.obj["url"],
    gitlab_key=ctx.obj["key"],
    name=name,
    root=directory,
)
group.recursive_command("clone")
```

# Development & Contributing

Contributions welcome — feel free to open issues or submit PRs. See [CONTRIBUTING.md](CONTRIBUTING.md).

# License

MIT License • © 2026
