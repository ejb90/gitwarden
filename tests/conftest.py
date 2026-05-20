"""Fixtures."""

import os
import shutil
from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest

from gitconductor.gitlab import GitlabGroup

NAME = "ejb90-group"
REMOTE = f"https://gitlab.com/{NAME}"


@pytest.fixture(scope="session")
def group(tmp_path_factory: pytest.TempPathFactory) -> GitlabGroup:
    """GitlabGroup object."""
    tmp = tmp_path_factory.mktemp("repo")
    return GitlabGroup(gitlab_key=os.environ.get("GITCONDUCTOR_GITLAB_API_KEY", ""), name="", source=REMOTE, root=tmp)


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
def chdir_tmp_when_marked(request: FixtureRequest, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Change to a temporary directory for tests marked with ``tmp_path``.

    Args:
        request (FixtureRequest): Active pytest fixture request.
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
        tmp_path (Path): Temporary directory for the current test.
    """
    if request.node.get_closest_marker("tmp_path") is not None:
        monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def chdir_repo_when_marked(request: FixtureRequest, monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
    """Change to the cloned repository for tests marked with ``repo_path``.

    Args:
        request (FixtureRequest): Active pytest fixture request.
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
        repo (Path): Cloned repository path.
    """
    if request.node.get_closest_marker("repo_path") is not None:
        monkeypatch.chdir(repo)


@pytest.fixture(autouse=True)
def chdir_repo_copy_when_marked(
    request: FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    repo: Path,
) -> None:
    """Change to a fresh repository copy for tests marked with ``fresh_repo_path``.

    Args:
        request (FixtureRequest): Active pytest fixture request.
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
        tmp_path (Path): Temporary directory for the current test.
        repo (Path): Cloned repository path to copy.
    """
    if request.node.get_closest_marker("fresh_repo_path") is not None:
        shutil.copytree(repo, tmp_path / repo.name)
        monkeypatch.chdir(tmp_path / repo.name)
