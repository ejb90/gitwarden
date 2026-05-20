# gitconductor

![tests](https://github.com/ejb90/gitconductor/actions/workflows/test.yml/badge.svg)
[![Coverage](https://codecov.io/gh/ejb90/gitconductor/branch/main/graph/badge.svg)](https://codecov.io/gh/ejb90/gitconductor)
[![License](https://img.shields.io/github/license/ejb90/gitconductor)](LICENCE.md)
![Ruff](https://img.shields.io/badge/code%20style-ruff-261230)
[![Documentation](https://readthedocs.org/projects/gitconductor/badge/?version=latest)](https://gitconductor.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/gitconductor)](https://pypi.org/project/gitconductor/)
[![Python versions](https://img.shields.io/pypi/pyversions/gitconductor)](https://pypi.org/project/gitconductor/)

`gitconductor` is a command-line tool and Python library for managing git operations over *nested GitLab groups* using the official [GitLab Python API](https://python-gitlab.readthedocs.io/en/stable/). It traverses group and subgroup hierarchies, runs recursive git commands, and can work with Python packages inside a cloned hierarchy.

Full documentation: [gitconductor.readthedocs.io](https://gitconductor.readthedocs.io/en/latest/).

# Features

* Recursive group traversal across nested GitLab groups
* Git operations across many projects, such as clone, branch, checkout, add, commit, status, and push
* Hierarchy and access visualisation with Rich tables and trees
* Python package helpers for requirements, installation, and wheel building
* CLI and Python API entry points

# Installation

```bash
pip install gitconductor
```

# Configuration

Gitconductor needs a GitLab Personal Access Token. The quickest setup is:

```bash
export GITCONDUCTOR_GITLAB_API_KEY=<my-private-key>
```

Pass the full GitLab group or project URL to `gitconductor clone`. Gitconductor derives the GitLab instance from that URL.

Gitconductor can also store settings in a TOML file. By default, this is:

```text
~/.config/gitconductor/gitconductor.toml
```

The location can be changed via `GITCONDUCTOR_CONFIG` or the top-level `--cfg` CLI option.

# Quick Start

```bash
gitconductor clone https://gitlab.com/my-group
cd my-group
gitconductor status
gitconductor viz tree
```

Run commands from a subgroup or project directory to narrow the recursive scope.
Use `gitconductor clone --resume <url>` to reuse an existing matching hierarchy.

# Documentation

See the full documentation for:

* [Configuration](https://gitconductor.readthedocs.io/en/latest/configuration.html)
* [Git CLI commands](https://gitconductor.readthedocs.io/en/latest/git_cli.html)
* [Visualisation](https://gitconductor.readthedocs.io/en/latest/visualisation.html)
* [Python package commands](https://gitconductor.readthedocs.io/en/latest/python_cli.html)
* [Python API](https://gitconductor.readthedocs.io/en/latest/modules.html)

# Development & Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

# License

MIT License. See [LICENCE.md](LICENCE.md).
