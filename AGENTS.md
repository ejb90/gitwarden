# Agents

This file gives coding agents the local rules for working in this repository.

## Project Shape

`gitconductor` is a Python CLI/library for managing nested GitLab groups and projects. The core package lives in `gitconductor/`, tests live in `tests/`, and the root `README.md` is also exposed to the package through `gitconductor/_data/README.md`.

Important modules:

* `gitconductor/cli.py`: top-level Click/Rich Click command group.
* `gitconductor/cli_git.py`: recursive git CLI commands.
* `gitconductor/cli_python.py`: recursive Python package CLI commands.
* `gitconductor/gitlab.py`: GitLab group/project models and recursive operations.
* `gitconductor/misc.py`: config loading and README helpers.
* `tests/conftest.py`: GitLab clone fixtures and directory-changing markers.

## Commands

Use these commands when validating changes:

```bash
uv run pytest
uv run pytest -k test_name
uv run ruff check .
uv run ruff format .
```

The test suite is configured with coverage and a 90 percent fail-under threshold. Full tests may need a valid `GITCONDUCTOR_GITLAB_API_KEY` and network access to GitLab.

## Coding Rules

* Preserve user changes. Do not revert unrelated dirty work.
* Use typed function signatures throughout tests and source code.
* Use Google-style docstrings for new or edited functions.
* Keep CLI wrappers thin; put recursive project behavior on `GitlabGroup` or `GitlabProject`.
* Prefer `pathlib.Path` over string path manipulation.
* Prefer structured subprocess calls such as `subprocess.run([...], capture_output=True, text=True)`.
* Keep edits scoped. Avoid opportunistic refactors while fixing a bug.
* Update `README.md` when changing user-facing CLI behavior.

## Test Fixtures

Tests use custom markers to choose the working directory:

* `tmp_path`: run from a temporary directory.
* `repo_path`: run from the cloned root repository.
* `fresh_repo_path`: copy the cloned repository and run from the fresh copy.

When adding tests, choose the narrowest marker that matches the behavior under test.

## Packaging Notes

Python package discovery treats a repository as a package when it contains `pyproject.toml` or `setup.py`. Recursive Python commands should work from the top-level group, a subgroup, or an individual project directory.
