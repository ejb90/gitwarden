"""Fixtures."""
import pytest

import gitwarden.gitlab

NAME = "ejb90-group"

@pytest.fixture(scope="session")
def group(tmp_path_factory):
    """GitlabGroup object."""
    tmp = tmp_path_factory.mktemp("repo")
    return gitwarden.gitlab.GitlabGroup(name=NAME, root=tmp)


@pytest.fixture(scope="session")
def repo(group):
    """Clone repo for testing."""
    group.recursive_command("clone")
    return group.path
