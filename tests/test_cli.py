"""Test cloning functionality."""

import pathlib
import shutil

import git
import pytest
from click.testing import CliRunner

import gitwarden.cli
import gitwarden.gitlab


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


def test_add_none(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
    """Test adding nothing inside a metarepo."""
    runner = CliRunner()
    shutil.copytree(repo, tmp_path / repo.name)
    monkeypatch.chdir(tmp_path / repo.name)

    result = runner.invoke(gitwarden.cli.cli, ["add", "mynewfile"])
    assert result.exit_code == 0

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
        staged_diffs = git_obj.index.diff("HEAD")
        assert not staged_diffs


def test_add_modify_simple(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
    """Test adding a modified file inside a metarepo."""
    runner = CliRunner()
    repo2 = tmp_path / repo.name

    shutil.copytree(repo, repo2)
    monkeypatch.chdir(repo2)

    fnames = []
    for fname in pathlib.Path(repo2).rglob("**/README.md"):
        with open(fname, "w") as fobj:
            fobj.write("")
            fnames.append(str(fname.relative_to(repo2)))

    result = runner.invoke(
        gitwarden.cli.cli,
        ["add", *fnames],
    )
    assert result.exit_code == 0

    for dname in (
        "ejb90-project",
        "models/model-a",
        "models/model-b",
        "models/model-c",
        "models/subgroup-1/model-d",
        "models/subgroup-1/model-e",
    ):
        git_obj = git.Repo(repo2 / dname)
        assert (repo2 / dname).is_dir()
        staged_diffs = git_obj.index.diff("HEAD")
        staged_files = [diff.a_path for diff in staged_diffs]
        assert "README.md" in staged_files


def test_add_modify_untracked_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path
) -> None:
    """Test adding a modified file inside a metarepo."""
    runner = CliRunner()
    repo2 = tmp_path / repo.name

    shutil.copytree(repo, repo2)
    monkeypatch.chdir(repo2)

    fnames = []
    for fname in pathlib.Path(repo2).rglob("**/README.md"):
        with open(fname, "w") as fobj:
            fobj.write("")
            fnames.append(str(fname.relative_to(repo2)))
        with open(fname.parent / "test", "w") as fobj:
            fobj.write("")

    result = runner.invoke(
        gitwarden.cli.cli,
        ["add", *fnames],
    )
    assert result.exit_code == 0

    for dname in (
        "ejb90-project",
        "models/model-a",
        "models/model-b",
        "models/model-c",
        "models/subgroup-1/model-d",
        "models/subgroup-1/model-e",
    ):
        git_obj = git.Repo(repo2 / dname)
        assert (repo2 / dname).is_dir()
        staged_diffs = git_obj.index.diff("HEAD")
        staged_files = [diff.a_path for diff in staged_diffs]
        assert "README.md" in staged_files
        assert "test" not in staged_files


def test_add_modify_new_files(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
    """Test adding a modified file inside a metarepo."""
    runner = CliRunner()
    repo2 = tmp_path / repo.name

    shutil.copytree(repo, repo2)
    monkeypatch.chdir(repo2)

    fnames = []
    for fname in pathlib.Path(repo2).rglob("**/README.md"):
        with open(fname, "w") as fobj:
            fobj.write("")
            fnames.append(str(fname.relative_to(repo2)))
        with open(fname.parent / "test", "w") as fobj:
            fobj.write("")
            fnames.append(str((fname.parent / "test").relative_to(repo2)))

    result = runner.invoke(
        gitwarden.cli.cli,
        ["add", *fnames],
    )
    assert result.exit_code == 0

    for dname in (
        "ejb90-project",
        "models/model-a",
        "models/model-b",
        "models/model-c",
        "models/subgroup-1/model-d",
        "models/subgroup-1/model-e",
    ):
        git_obj = git.Repo(repo2 / dname)
        assert (repo2 / dname).is_dir()
        staged_diffs = git_obj.index.diff("HEAD")
        staged_files = [diff.a_path for diff in staged_diffs]
        print([i.name for i in (repo2 / dname).iterdir()])
        print(staged_files)
        assert "README.md" in staged_files
        assert "test" in staged_files


def test_commit_none(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
    """Test commiting nothing inside a metarepo."""
    runner = CliRunner()
    repo2 = tmp_path / repo.name

    shutil.copytree(repo, repo2)
    monkeypatch.chdir(repo2)

    result = runner.invoke(gitwarden.cli.cli, ["commit", "-m", "mynewfile"])
    assert result.exit_code == 0

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
        staged_diffs = git_obj.index.diff("HEAD")
        assert not staged_diffs


def test_commit_change(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, repo: pathlib.Path) -> None:
    """Test commiting a change inside a metarepo."""
    runner = CliRunner()
    repo2 = tmp_path / repo.name

    shutil.copytree(repo, repo2)
    monkeypatch.chdir(repo2)

    fnames = []
    for fname in pathlib.Path(repo2).rglob("**/README.md"):
        with open(fname, "w") as fobj:
            fobj.write("")
            fnames.append(str(fname.relative_to(repo2)))

    result = runner.invoke(
        gitwarden.cli.cli,
        ["add", *fnames],
    )
    result = runner.invoke(
        gitwarden.cli.cli,
        ["commit", "-m", "change"],
    )
    assert result.exit_code == 0

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
        staged_diffs = git_obj.index.diff("HEAD")
        assert not staged_diffs


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


def test_load_cfg_directly(repo: pathlib.Path) -> None:
    """Load cfg file directly."""
    grp = gitwarden.cli.load_cfg(repo / gitwarden.gitlab.GROUP_FNAME)
    assert isinstance(grp, gitwarden.gitlab.GitlabGroup)


def test_load_cfg_missing_walk() -> None:
    """Load missing cfg file, walking up to root."""
    with pytest.raises(FileNotFoundError, match=r'No gitwarden configuration file ".+" found up to root.'):
        gitwarden.cli.load_cfg(None)


def test_load_cfg_directly_missing() -> None:
    """Load missing cfg file."""
    with pytest.raises(FileNotFoundError, match=r'The provided gitwarden configuration file ".+" does not exist.'):
        gitwarden.cli.load_cfg(pathlib.Path("missing_file"))


def test_load_cfg_wrong_type() -> None:
    """Load cfg file with wrong type."""
    with pytest.raises(TypeError, match=r"Expected pathlib.Path or None for `cfg`."):
        gitwarden.cli.load_cfg(1)
