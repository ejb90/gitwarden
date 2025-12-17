"""Fixtures."""

import pathlib

import pytest

from gitwarden import gitlab

NAME = "ejb90-group"


@pytest.fixture(scope="session")
def group(tmp_path_factory: pytest.TempPathFactory) -> gitlab.Group:
    """GitlabGroup object."""
    tmp = tmp_path_factory.mktemp("repo")
    return gitlab.GitlabGroup(name=NAME, root=tmp)


@pytest.fixture(scope="session")
def repo(group: gitlab.Group) -> pathlib.Path:
    """Clone repo for testing."""
    group.recursive_command("clone")
    return group.path
