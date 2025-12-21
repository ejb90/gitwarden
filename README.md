# gitwarden

`gitwarden` is a command-line tool and Python library for managing git operations over **nested GitLab groups** using the official GitLab Python API. It makes it easy to traverse complex group hierarchies, perform recursive git operations, and remove submodule interdependencies, accessing only the sub-groups/projects the user has access to.

# Features

* Recursive group traversal — operate on entire GitLab group trees, not just individual projects
* Git operations across nested groups (clone, pull, status, etc.)
* Unified CLI and Python API
* Built on top of the official GitLab Python API
* Designed for automation, scripting, and bulk maintenance

# Installation

```
pip install gitwarden
```

## Configuration

### GitLab API Keys

Keys can be set up in two ways:

1. Via an environment variable: `export GITLAB_PRIVATE_KEY=<my-private-key>`
2. Via the "gitwarden.yaml" file.

# Usage (CLI)

## Clone

To clone a Gitlab project at, for example, "https://gitlab.com/ejb90-group"

```
gitwarden clone ejb90-group
```

## Branch

```
gitwarden branch <name>
```

## Checkout

```
gitwarden checkout <name>
```

## Pull

...

## Visualisation

### Tree

To visualise the hierarchy of Groups/Projects as a Run, run:

```
gitwarden viz tree
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
gitwarden viz table
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
gitwarden viz access
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

MIT License • © 2025
