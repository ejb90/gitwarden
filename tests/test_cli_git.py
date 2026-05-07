"""Test git functionality via CLI."""

from pathlib import Path
import shutil

import git
import pytest
from click.testing import CliRunner

import gitconductor.cli


@pytest.mark.tmp_path
def test_clone_simple() -> None:
    """Basic clone."""
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["clone", "ejb90-group"])

    dname = Path("ejb90-group")
    fname = dname / ".gitconductor.pkl"

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


@pytest.mark.tmp_path
def test_clone_flat() -> None:
    """Basic flat clone."""
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["clone", "--flat", "ejb90-group"])

    fname = Path(".gitconductor.pkl")   

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
        assert Path(dname).is_dir()



@pytest.mark.tmp_path
def test_clone_limited_access() -> None:
    """Clone with access to one subproject, but not the other."""
    runner = CliRunner()
    runner.invoke(gitconductor.cli.cli, ["clone", "mobot-group"])

    dname = Path("mobot-group")
    assert (dname / "access").is_dir()
    assert not (dname / "no-access").is_dir()


@pytest.mark.repo_path
def test_branch(repo: Path) -> None:
    """Test branching inside a metarepo."""
    runner = CliRunner()
    fname = Path(".gitconductor.pkl")

    result = runner.invoke(gitconductor.cli.cli, ["branch", "test"])

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


@pytest.mark.repo_path
def test_checkout(repo: Path) -> None:
    """Test branching inside a metarepo."""
    runner = CliRunner()
    fname = Path(".gitconductor.pkl")

    result = runner.invoke(gitconductor.cli.cli, ["checkout", "test"])

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


@pytest.mark.fresh_repo_path
def test_add_none(repo: Path) -> None:
    """Test adding nothing inside a metarepo."""
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["add", "mynewfile"])
    
    assert result.exit_code == 0
    for dname in (
        "ejb90-project",
        "models/model-a",
        "models/model-b",
        "models/model-c",
        "models/subgroup-1/model-d",
        "models/subgroup-1/model-e",
    ):
        dpath = repo / dname
        git_obj = git.Repo(dpath)
        assert dpath.is_dir()
        staged_diffs = git_obj.index.diff("HEAD")
        assert not staged_diffs


@pytest.mark.fresh_repo_path
def test_add_modify_simple() -> None:
    """Test adding a modified file inside a metarepo."""
    runner = CliRunner()
    root = Path().resolve()

    fnames = []
    for fname in root.rglob("**/README.md"):
        with open(fname, "w") as fobj:
            fobj.write("")
            fnames.append(str(fname.relative_to(root)))

    result = runner.invoke(
        gitconductor.cli.cli,
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
        git_obj = git.Repo(root / dname)
        assert (root / dname).is_dir()
        staged_diffs = git_obj.index.diff("HEAD")
        staged_files = [diff.a_path for diff in staged_diffs]
        assert "README.md" in staged_files


@pytest.mark.fresh_repo_path
def test_add_modify_untracked_files() -> None:
    """Test adding a modified file inside a metarepo."""
    runner = CliRunner()
    root = Path().resolve()
    
    fnames = []
    for fname in root.rglob("**/README.md"):
        with open(fname, "w") as fobj:
            fobj.write("")
            fnames.append(str(fname.relative_to(root)))
        with open(fname.parent / "test", "w") as fobj:
            fobj.write("")

    result = runner.invoke(
        gitconductor.cli.cli,
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
        git_obj = git.Repo(root / dname)
        assert (root / dname).is_dir()
        staged_diffs = git_obj.index.diff("HEAD")
        staged_files = [diff.a_path for diff in staged_diffs]
        assert "README.md" in staged_files
        assert "test" not in staged_files


@pytest.mark.fresh_repo_path
def test_add_modify_new_files() -> None:
    """Test adding a modified file inside a metarepo."""
    runner = CliRunner()
    root = Path().resolve()

    fnames = []
    for fname in root.rglob("**/README.md"):
        with open(fname, "w") as fobj:
            fobj.write("")
            fnames.append(str(fname.relative_to(root)))
        with open(fname.parent / "test", "w") as fobj:
            fobj.write("")
            fnames.append(str((fname.parent / "test").relative_to(root)))

    result = runner.invoke(
        gitconductor.cli.cli,
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
        git_obj = git.Repo(root / dname)
        assert (root / dname).is_dir()
        staged_diffs = git_obj.index.diff("HEAD")
        staged_files = [diff.a_path for diff in staged_diffs]
        assert "README.md" in staged_files
        assert "test" in staged_files


@pytest.mark.fresh_repo_path
def test_commit_none() -> None:
    """Test commiting nothing inside a metarepo."""
    runner = CliRunner()
    root = Path().resolve() 

    result = runner.invoke(gitconductor.cli.cli, ["commit", "-m", "mynewfile"])
    assert result.exit_code == 0

    for dname in (
        "ejb90-project",
        "models/model-a",
        "models/model-b",
        "models/model-c",
        "models/subgroup-1/model-d",
        "models/subgroup-1/model-e",
    ):
        git_obj = git.Repo(root / dname)
        assert (root / dname).is_dir()
        staged_diffs = git_obj.index.diff("HEAD")
        assert not staged_diffs


@pytest.mark.fresh_repo_path
def test_commit_change() -> None:
    """Test commiting a change inside a metarepo."""
    runner = CliRunner()
    root =  Path().resolve()

    fnames = []
    for fname in Path(root).rglob("**/README.md"):
        with open(fname, "w") as fobj:
            fobj.write("")
            fnames.append(str(fname.relative_to(root)))

    result = runner.invoke(
        gitconductor.cli.cli,
        ["add", *fnames],
    )
    result = runner.invoke(
        gitconductor.cli.cli,
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
        git_obj = git.Repo(root / dname)
        assert (root / dname).is_dir()
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
@pytest.mark.repo_path
def test_viz(monkeypatch: pytest.MonkeyPatch, command: str, subdir: str, expectation: list[str]) -> None:
    """Test tree visualisation."""
    runner = CliRunner()
    if subdir:
        monkeypatch.chdir(subdir)
    result = runner.invoke(gitconductor.cli.cli, ["viz", command])

    assert result.exit_code == 0
    for name in expectation:
        assert name in result.output


@pytest.mark.repo_path
def test_status() -> None:
    """Test status."""
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["status"])
    assert result.exit_code == 0



@pytest.mark.fresh_repo_path
def test_status_unstaged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test status."""
    # Modify file
    monkeypatch.chdir("ejb90-project")
    with open("README.md", "w") as fobj:
        fobj.write("Hello, World!")
    
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["status"])
    assert result.exit_code == 0


@pytest.mark.fresh_repo_path
def test_status_staged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test status."""
    # Modify file
    monkeypatch.chdir("ejb90-project")
    with open("README.md", "w") as fobj:
        fobj.write("Hello, World!")

    runner = CliRunner()
    # Add file to staging
    runner.invoke(gitconductor.cli.cli, ["add", "README.md"])
    result = runner.invoke(gitconductor.cli.cli, ["status"])
    assert result.exit_code == 0


@pytest.mark.fresh_repo_path
def test_status_staged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test status."""
    # Modify file
    monkeypatch.chdir("ejb90-project")
    Path("tmp").touch()

    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["status"])
    assert result.exit_code == 0