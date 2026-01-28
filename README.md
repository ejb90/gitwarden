# gitconductor

![tests](https://github.com/ejb90/gitconductor/actions/workflows/test.yml/badge.svg)
[![Coverage](https://codecov.io/gh/ejb90/gitconductor/branch/main/graph/badge.svg)](https://codecov.io/gh/ejb90/gitconductor)
[![License](https://img.shields.io/github/license/ejb90/gitconductor)](LICENSE)
![Ruff](https://img.shields.io/badge/code%20style-ruff-261230)
[![Documentation](https://readthedocs.org/projects/gitconductor/badge/?version=latest)](https://gitconductor.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/gitconductor)](https://pypi.org/project/gitconductor/)
[![Python versions](https://img.shields.io/pypi/pyversions/gitconductor)](https://pypi.org/project/gitconductor/)


`gitconductor` is a command-line tool and Python library for managing git operations over *nested GitLab groups* using the official [GitLab Python API](https://python-gitlab.readthedocs.io/en/stable/). It makes it easier to traverse complex group/sub-group hierarchies, perform recursive git operations, without the need for submodule interdependencies, accessing only the sub-groups/projects for which the user has access.

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

## Gitlab Access

Access to Gitlab is controlled via Personal Access Tokens. To generate:

1. Login to Gitlab.
2. Click to user icon.
3. Click preferences in the drop down.
4. Click "Personal access tokens" on the left side bar.
5. Click the "Add new token" button in the top right.
6. Give it a helpful name.
7. Set the expiry date - for closed systems the longest permissable time of 1 year is easiest.
8. Click the tick box for:
    * read_user
    * read_repository
    * read_virtual_registry
    * read_registry
    * read_api
    * self_rotate
9. Click the "Generate token" button below.
10. Copy the new token (noting it can't be viewed again after).

# Configuration

## Configuration file

Gitconductor can store settings in a file. By default, this is at "~/.config/gitconductor/gitconductor.toml". The location can be changed via the `GITCONDUCTOR_CONFIG` environment variable. Alternatively, a path can be passed via the top-level `--cfg` CLI argument.

## Environment Variables

* `GITCONDUCTOR_CONFIG`: Gitconductor configuration YAML file location.
* `GITCONDUCTOR_GITLAB_API_KEY`: Gitlab Private Access Token.
* `GITCONDUCTOR_GITLAB_URL`: Gitlab main URL.

## GitLab API Keys

Keys can be set up in two ways:

1. Via an environment variable: `export GITCONDUCTOR_GITLAB_API_KEY=<my-private-key>`
2. Via the "gitconductor.toml" file in the `gitconductor_gitlab_api_key` variable.

# Usage (CLI)

## Clone

To clone a Gitlab project at, for example, [https://gitlab.com/ejb90-group](https://gitlab.com/ejb90-group).

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

...

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

Contributions welcome — feel free to open issues or submit PRs.

# License

MIT License • © 2026
