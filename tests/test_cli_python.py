"""Test python functionality via CLI."""
import logging
from pathlib import Path
import shutil

import pytest
from click.testing import CliRunner

import gitconductor.cli


@pytest.mark.fresh_repo_path
def test_pyrequirements_basic() -> None:
    """Basic useage."""
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["py-requirements"])

    assert result.exit_code == 0
    assert Path("requirements.txt").is_file()


@pytest.mark.fresh_repo_path
def test_pyrequirements_setup(testdir: Path) -> None:
    """Basic useage."""
    for fname in Path().resolve().rglob("**/pyproject.toml"):
        fname.unlink()
        shutil.copy(testdir / "setup.py", fname.parent / "setup.py")
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["py-requirements"])

    assert result.exit_code == 0
    assert Path("requirements.txt").is_file()


@pytest.mark.fresh_repo_path
def test_pyrequirements_pyproject() -> None:
    """Basic useage."""
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["py-requirements", "--pyproject"])

    assert result.exit_code == 0
    assert Path("pyproject.toml").is_file()


@pytest.mark.fresh_repo_path
def test_pyrequirements_force() -> None:
    """Basic useage."""
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["py-requirements", "--force"])

    assert result.exit_code == 0
    assert Path("requirements.txt").is_file()


@pytest.mark.fresh_repo_path
def test_pyrequirements_force_with_file() -> None:
    """Basic useage."""
    Path("requirements.txt").touch()
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["py-requirements", "--force"])

    assert result.exit_code == 0
    assert Path("requirements.txt").is_file()


@pytest.mark.fresh_repo_path
def test_pyrequirements_noforce_with_file(caplog) -> None:
    """Basic useage."""
    Path("requirements.txt").touch()
    print(list(Path().iterdir()))
    runner = CliRunner()
    with caplog.at_level(logging.WARNING):
        result = runner.invoke(gitconductor.cli.cli, ["py-requirements"])
    assert result.exit_code == 0
    assert "File already exists" in caplog.text
