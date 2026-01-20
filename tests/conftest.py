"""Fixtures."""

import pathlib

import pytest

from gitconductor.gitlab import GitlabGroup

NAME = "ejb90-group"


@pytest.fixture(scope="session")
def group(tmp_path_factory: pytest.TempPathFactory) -> GitlabGroup:
    """GitlabGroup object."""
    tmp = tmp_path_factory.mktemp("repo")
    return GitlabGroup(name=NAME, fullname=NAME, root=tmp)


@pytest.fixture(scope="session")
def repo(group: GitlabGroup) -> pathlib.Path:
    """Clone repo for testing."""
    group.recursive_command("clone")
    return group.path
