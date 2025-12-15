"""Test cloning functionality."""
import pathlib

from click.testing import CliRunner
import git
import pytest

import gitwarden.cli


def test_clone(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """Basic clone."""
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(gitwarden.cli.cli, ["clone", "ejb90-group"])

    dname = tmp_path / "ejb90-group"
    fname = dname / ".gitwarden.pkl"

    assert result.exit_code == 0
    assert dname.is_dir()
    assert fname.is_file()


def test_branch(monkeypatch: pytest.MonkeyPatch, repo: pathlib.Path) -> None:
    """Test branching inside a metarepo."""
    runner = CliRunner()
    monkeypatch.chdir(repo)
    fname =  pathlib.Path(".gitwarden.pkl")

    result = runner.invoke(gitwarden.cli.cli, ["branch", "test"])

    assert result.exit_code == 0
    assert fname.is_file()

    for dname in (
        "ejb90-project",
        "models/model-a",
        "models/model-b",
        "models/model-c",
        "models/subgroup-1/subgroup-1-model-a",
        "models/subgroup-1/subgroup-1-model-b",
    ):
        git_obj = git.Repo(repo / dname)
        assert (repo / dname).is_dir()
        assert "main" in git_obj.branches
        assert "test" in git_obj.branches
        assert git_obj.active_branch.name =="main"


def test_checkout(monkeypatch: pytest.MonkeyPatch, repo: pathlib.Path) -> None:
    """Test branching inside a metarepo."""
    runner = CliRunner()
    monkeypatch.chdir(repo)
    fname =  pathlib.Path(".gitwarden.pkl")

    result = runner.invoke(gitwarden.cli.cli, ["checkout", "test"])

    assert result.exit_code == 0
    assert fname.is_file()

    for dname in (
        "ejb90-project",
        "models/model-a",
        "models/model-b",
        "models/model-c",
        "models/subgroup-1/subgroup-1-model-a",
        "models/subgroup-1/subgroup-1-model-b",
    ):
        git_obj = git.Repo(repo / dname)
        assert (repo / dname).is_dir()
        assert "main" in git_obj.branches
        assert "test" in git_obj.branches
        assert git_obj.active_branch.name == "test"
