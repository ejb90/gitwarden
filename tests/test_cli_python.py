"""Test python functionality via CLI."""

import json
import logging
import shutil
import subprocess

# Meta --------------------------------------------------------------------------------------------
from importlib.metadata import Distribution, distributions
from pathlib import Path
from urllib.parse import unquote, urlparse

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


def package_source_path(dist: Distribution) -> Path | None:
    """Get the local source path for a direct-url distribution.

    Args:
        dist (Distribution): Installed package distribution metadata.

    Returns:
        Path | None: Source path when the distribution was installed from a local path.
    """
    direct_url = dist.read_text("direct_url.json")
    if not direct_url:
        return None

    try:
        data = json.loads(direct_url)
    except json.JSONDecodeError:
        return None

    url = data.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme != "file":
        return None

    return Path(unquote(parsed.path)).resolve()


def packages_info(root: Path | None = None) -> dict[str, dict[str, str | bool]]:
    """Collect installed package versions and editable status.

    Args:
        root (Path | None): Root path used to scope local package installations.

    Returns:
        dict[str, dict[str, str | bool]]: Mapping of package names to package metadata.
    """
    if root is None:
        root = Path.cwd()
    root = root.resolve()

    packages = {}
    for dist in distributions():
        source_path = package_source_path(dist)
        if source_path is None or not source_path.is_relative_to(root):
            continue

        packages[dist.metadata["Name"]] = {
            "version": dist.version,
            "editable": is_editable(dist),
        }
    return packages


def uninstall_packages(package_names: tuple[str, ...]) -> None:
    """Uninstall packages installed by installer tests.

    Args:
        package_names (tuple[str, ...]): Package names to uninstall.
    """
    for package_name in package_names:
        subprocess.run(["uv", "pip", "uninstall", package_name], check=False)


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
    package_names = ("ejb90-project", "model-a", "model-b", "model-c", "model-d", "model-e")
    runner = CliRunner()
    try:
        result = runner.invoke(gitconductor.cli.cli, ["py-installer"])

        assert result.exit_code == 0

        packages = packages_info()
        for repo in package_names:
            assert repo in packages
            assert not packages[repo]["editable"]
    finally:
        uninstall_packages(package_names)


@pytest.mark.fresh_repo_path
def test_pyinstaller_editable() -> None:
    """Install Python packages."""
    package_names = ("ejb90-project", "model-a", "model-b", "model-c", "model-d", "model-e")
    runner = CliRunner()
    try:
        result = runner.invoke(gitconductor.cli.cli, ["py-installer", "--editable"])

        assert result.exit_code == 0

        packages = packages_info()
        for repo in package_names:
            assert repo in packages
            assert packages[repo]["editable"]
    finally:
        uninstall_packages(package_names)


@pytest.mark.fresh_repo_path
def test_pyinstaller_subgroup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Install Python packages."""
    package_names = ("model-a", "model-b", "model-c", "model-d", "model-e")
    monkeypatch.chdir("models")
    runner = CliRunner()
    try:
        result = runner.invoke(gitconductor.cli.cli, ["py-installer"])

        assert result.exit_code == 0

        packages = packages_info()
        for repo in package_names:
            assert repo in packages
            assert not packages[repo]["editable"]
        assert "ejb90-project" not in packages
    finally:
        uninstall_packages(package_names)


@pytest.mark.fresh_repo_path
def test_pywheel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Build Python wheels through the recursive GitLab command."""
    repo_names = ("model-a", "model-b", "model-c", "subgroup-1/model-d", "subgroup-1/model-e")
    monkeypatch.chdir(Path("models"))
    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["py-wheel"])

    assert result.exit_code == 0

    for repo in repo_names:
        wheel_path = (
            Path(repo) / "dist" / f"{Path(repo).name.replace('/', '-').replace('-', '_')}-0.1.0-py3-none-any.whl"
        )
        assert wheel_path.is_file()
