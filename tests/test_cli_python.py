"""Test python functionality via CLI."""

import json
import logging
import shutil
import subprocess

# Meta --------------------------------------------------------------------------------------------
from importlib.metadata import Distribution, distributions
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner

import gitconductor.cli


def is_editable(dist: Distribution) -> bool:
    """Determine whether a distribution was installed in editable mode.

    Args:
        dist (Distribution): Installed package distribution metadata.

    Returns:
        bool: Whether the distribution is editable.
    """
    direct_url = dist.read_text("direct_url.json")
    if not direct_url:
        return False

    try:
        data = json.loads(direct_url)
    except json.JSONDecodeError:
        return False

    return data.get("dir_info", {}).get("editable", False)


def packages_info() -> dict[str, dict[str, str | bool]]:
    """Collect installed package versions and editable status.

    Returns:
        dict[str, dict[str, str | bool]]: Mapping of package names to package metadata.
    """
    packages = {
        dist.metadata["Name"]: {
            "version": dist.version,
            "editable": is_editable(dist),
        }
        for dist in distributions()
    }
    return packages


# Requirements ------------------------------------------------------------------------------------
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
def test_pyrequirements_noforce_with_file(caplog: LogCaptureFixture) -> None:
    """Basic useage."""
    Path("requirements.txt").touch()
    print(list(Path().iterdir()))
    runner = CliRunner()
    with caplog.at_level(logging.WARNING):
        result = runner.invoke(gitconductor.cli.cli, ["py-requirements"])
    assert result.exit_code == 0
    assert "File already exists" in caplog.text


# Installer ---------------------------------------------------------------------------------------
@pytest.mark.fresh_repo_path
def test_pyinstaller_simple() -> None:
    """Install Python packages."""
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["py-installer"])

    assert result.exit_code == 0

    packages = packages_info()
    for repo in ("ejb90-project", "model-a", "model-b", "model-c", "model-d", "model-e"):
        assert repo in packages
        assert not packages[repo]["editable"]
        subprocess.run(["uv", "pip", "uninstall", repo], check=True)


@pytest.mark.fresh_repo_path
def test_pyinstaller_editable() -> None:
    """Install Python packages."""
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["py-installer", "--editable"])

    assert result.exit_code == 0

    packages = packages_info()
    for repo in ("ejb90-project", "model-a", "model-b", "model-c", "model-d", "model-e"):
        assert repo in packages
        assert packages[repo]["editable"]
        subprocess.run(["uv", "pip", "uninstall", repo], check=True)


@pytest.mark.fresh_repo_path
def test_pyinstaller_subgroup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Install Python packages."""
    monkeypatch.chdir("models")
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["py-installer"])

    assert result.exit_code == 0

    packages = packages_info()
    for repo in ("model-a", "model-b", "model-c", "model-d", "model-e"):
        assert repo in packages
        assert not packages[repo]["editable"]
        subprocess.run(["uv", "pip", "uninstall", repo], check=True)
    assert "ejb90-project" not in packages
