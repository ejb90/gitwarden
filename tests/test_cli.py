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

    print(result.output)
    print(result.exception)

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
    result = runner.invoke(gitwarden.cli.cli, ["clone", "--flat", "ejb90-group"])

    fname = tmp_path / ".gitwarden.pkl"

    assert result.exit_code == 0
    assert fname.is_file()

    for dname in (
        "ejb90-group-ejb90-project",
        "ejb90-group-models-model-a",
        "ejb90-group-models-model-b",
        "ejb90-group-models-model-c",
        "ejb90-group-models-subgroup-1-model-d",
        "ejb90-group-models-subgroup-1-model-e",
    ):
        assert (tmp_path / dname).is_dir()


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
        "models/subgroup-1/model-d",
        "models/subgroup-1/model-e",
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
        "models/subgroup-1/model-d",
        "models/subgroup-1/model-e",
    ):
        git_obj = git.Repo(repo / dname)
        assert (repo / dname).is_dir()
        assert "main" in git_obj.branches
        assert "test" in git_obj.branches
        assert git_obj.active_branch.name == "test"


# def test_add_none(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
#     """Test branching inside a metarepo."""
#     import shutil
#     runner = CliRunner()
#     shutil.copytree(repo, tmp_path / repo.name)
#     monkeypatch.chdir(tmp_path / repo.name)
#     fname = pathlib.Path(".gitwarden.pkl")

#     result = runner.invoke(gitwarden.cli.cli, ["add", "mynewfile"])

#     print(result.output)
#     print(result.exception)

#     assert result.exit_code == 0


# def test_add_modify(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
#     """Test branching inside a metarepo."""
#     runner = CliRunner()
#     monkeypatch.chdir(repo)
#     fname = pathlib.Path(".gitwarden.pkl")

#     result = runner.invoke(gitwarden.cli.cli, ["add", "README.md"])
#     assert result.exit_code == 0


# def test_add_modify(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
#     """Test branching inside a metarepo."""
#     runner = CliRunner()
#     monkeypatch.chdir(repo)
#     fname = pathlib.Path(".gitwarden.pkl")

#     result = runner.invoke(gitwarden.cli.cli, ["add", "mynewfile"])
#     assert result.exit_code == 0


# def test_commit_none(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
#     """Test branching inside a metarepo."""
#     runner = CliRunner()
#     monkeypatch.chdir(repo)
#     fname = pathlib.Path(".gitwarden.pkl")

#     result = runner.invoke(gitwarden.cli.cli, ["commit", "-m", "test"])
#     assert result.exit_code == 0


# def test_commit_change(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
#     """Test branching inside a metarepo."""
#     runner = CliRunner()
#     monkeypatch.chdir(repo)
#     fname = pathlib.Path(".gitwarden.pkl")

#     result = runner.invoke(gitwarden.cli.cli, ["commit", "-m", "test"])
#     assert result.exit_code == 0


@pytest.mark.parametrize(
    ("command", "subdir", "expectation"),
    [
        (
            "tree",
            "",
            [
                "ejb90-group",
                "ejb90-project",
                "models",
                "model-a",
                "model-b",
                "model-c",
                "subgroup-1",
                "model-d",
                "model-e",
            ],
        ),
        (
            "table",
            "",
            [
                "ejb90-project",
                "model-a",
                "model-b",
                "model-c",
                "model-d",
                "model-e",
            ],
        ),
        (
            "access",
            "",
            [
                "Ellis",
                "mobot",
            ],
        ),
        (
            "tree",
            "models",
            [
                "models",
                "model-a",
                "model-b",
                "model-c",
                "subgroup-1",
                "model-d",
                "model-e",
            ],
        ),
        (
            "table",
            "models",
            [
                "model-a",
                "model-b",
                "model-c",
                "model-d",
                "model-e",
            ],
        ),
        (
            "access",
            "models",
            [
                "Ellis",
                "mobot",
            ],
        ),
        (
            "tree",
            "models",
            [
                "models",
                "model-a",
                "model-b",
                "model-c",
            ],
        ),
        (
            "table",
            "models",
            [
                "model-a",
            ],
        ),
        (
            "access",
            "models",
            [
                "Ellis",
                "mobot",
            ],
        ),
    ],
)
def test_viz(
    monkeypatch: pytest.MonkeyPatch, repo: pathlib.Path, command: str, subdir: str, expectation: list[str]
) -> None:
    """Test tree visualisation."""
    runner = CliRunner()
    monkeypatch.chdir(repo / subdir)

    result = runner.invoke(gitwarden.cli.cli, ["viz", command])

    assert result.exit_code == 0
    for name in expectation:
        assert name in result.output
