"""Test cloning functionality."""

import pathlib

import git
import pytest
from click.testing import CliRunner

import gitwarden.cli


def test_clone_simple(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """Basic clone."""
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(gitwarden.cli.cli, ["clone", "ejb90-group"])

    dname = tmp_path / "ejb90-group"
    fname = dname / ".gitwarden.pkl"

    assert result.exit_code == 0
    assert dname.is_dir()
    assert fname.is_file()

    for dname2 in (
        "ejb90-project",
        "models/model-a",
        "models/model-b",
        "models/model-c",
        "models/subgroup-1/model-d",
        "models/subgroup-1/model-e",
    ):
        assert (dname / dname2).is_dir()


def test_clone_flat(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """Basic flat clone."""
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(gitwarden.cli.cli, ["clone", "ejb90-group", "--flat"])

    dname = tmp_path / "ejb90-group"
    fname = dname / ".gitwarden.pkl"

    assert result.exit_code == 0
    assert fname.is_file()

    for dname2 in (
        "ejb90-group-ejb90-project",
        "ejb90-group-models-model-a",
        "ejb90-group-models-model-b",
        "ejb90-group-models-model-c",
        "ejb90-group-models-subgroup-1-model-d",
        "ejb90-group-models-subgroup-1-model-e",
    ):
        assert (dname.parent / f"{dname.name}-{dname2}").is_dir()


def test_clone_limited_access(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """Clone with access to one subproject, but not the other."""
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    runner.invoke(gitwarden.cli.cli, ["clone", "mobot-group"])

    dname = tmp_path / "mobot-group"
    assert (dname / "access").is_dir()
    assert not (dname / "no-access").is_dir()


def test_branch(monkeypatch: pytest.MonkeyPatch, repo: pathlib.Path) -> None:
    """Test branching inside a metarepo."""
    runner = CliRunner()
    monkeypatch.chdir(repo)
    fname = pathlib.Path(".gitwarden.pkl")

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
        assert git_obj.active_branch.name == "main"


def test_checkout(monkeypatch: pytest.MonkeyPatch, repo: pathlib.Path) -> None:
    """Test branching inside a metarepo."""
    runner = CliRunner()
    monkeypatch.chdir(repo)
    fname = pathlib.Path(".gitwarden.pkl")

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
