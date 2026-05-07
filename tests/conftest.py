"""Fixtures."""

import os
from pathlib import Path
import shutil

import pytest

from gitconductor.gitlab import GitlabGroup

NAME = "ejb90-group"


@pytest.fixture(scope="session")
def group(tmp_path_factory: pytest.TempPathFactory) -> GitlabGroup:
    """GitlabGroup object."""
    tmp = tmp_path_factory.mktemp("repo")
    return GitlabGroup(gitlab_key=os.environ.get("GITCONDUCTOR_GITLAB_API_KEY", ""), name=NAME, fullname=NAME, root=tmp)


@pytest.fixture(scope="session")
def testdir() -> Path:
    """Clone repo for testing."""
    return Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def repo(group: GitlabGroup) -> Path:
    """Clone repo for testing."""
    group.recursive_command("clone")
    return group.path


@pytest.fixture(autouse=True)
def chdir_tmp_when_marked(request, monkeypatch, tmp_path):
    if request.node.get_closest_marker("tmp_path") is not None:
        monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def chdir_repo_when_marked(request, monkeypatch, repo: Path):
    if request.node.get_closest_marker("repo_path") is not None:
        monkeypatch.chdir(repo)


@pytest.fixture(autouse=True)
def chdir_repo_copy_when_marked(request, monkeypatch, tmp_path: Path, repo: Path):
    if request.node.get_closest_marker("fresh_repo_path") is not None:
        shutil.copytree(repo, tmp_path / repo.name)
        monkeypatch.chdir(tmp_path / repo.name)
