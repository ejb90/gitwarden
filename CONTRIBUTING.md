# Contributing

## Development Setup

Clone the repository and install the project with its development dependencies:

```bash
uv sync --extra dev
```

Follow the Gitlab API access setup in the README.md.

## Running Tests

Run the test suite with:

```bash
uv run pytest
```

To run a focused subset:

```bash
uv run pytest -k test_name
```

The pytest configuration enables coverage and currently requires at least 90 percent coverage. Some tests clone or inspect GitLab repositories, so make sure your token and network access are available before running the full suite.

## Linting and Formatting

This repository uses Ruff for linting and formatting. Run:

```bash
uv run ruff check .
uv run ruff format .
```

The Ruff configuration is strict: new functions should be typed, public functions should have Google-style docstrings, and imports should be sorted by Ruff.

## Code Style

Keep changes small and consistent with the existing codebase:

* Prefer existing helpers such as `misc.load_cfg` and `recursive_command` over adding parallel traversal logic.
* Keep CLI behavior in `gitconductor/cli_*.py` and project/group behavior in `gitconductor/gitlab.py`.
* Use `pathlib.Path` for filesystem paths.
* Avoid shell-string subprocess calls; pass argument lists to `subprocess.run`.
* Add or update tests in `tests/` for behavior changes.

## Pull Requests

Before opening a pull request:

1. Run the relevant tests.
2. Run Ruff checks and formatting.
3. Update the README or docs when CLI behavior changes.
4. Keep unrelated refactors out of the same pull request.

Include a short summary of the change, the tests you ran, and any GitLab/network assumptions needed to reproduce the result.
