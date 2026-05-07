"""Test misc functionality."""

from pathlib import Path

import pytest

from gitconductor import gitlab, misc, settings


def test_load_cfg_directly(repo: Path) -> None:
    """Load cfg file directly."""
    grp = misc.load_cfg(repo / gitlab.GROUP_FNAME)
    assert isinstance(grp, gitlab.GitlabGroup)


def test_load_cfg_missing_walk() -> None:
    """Load missing cfg file, walking up to root."""
    with pytest.raises(FileNotFoundError, match=r'No gitconductor configuration file ".+" found up to root.'):
        misc.load_cfg(None)


def test_load_cfg_directly_missing() -> None:
    """Load missing cfg file."""
    with pytest.raises(FileNotFoundError, match=r'The provided gitconductor configuration file ".+" does not exist.'):
        misc.load_cfg(Path("missing_file"))


def test_load_cfg_wrong_type() -> None:
    """Load cfg file with wrong type."""
    with pytest.raises(TypeError, match=r"Expected pathlib.Path or None for `cfg`."):
        misc.load_cfg(1)


def test_readme() -> None:
    """Test readme extraction."""
    readme = misc.readme()
    assert isinstance(readme, dict)
    for key in (
        "gitconductor",
        "Features",
        "Installation",
        "Configuration",
        "Usage (CLI)",
        "Usage (Python API)",
        "Development & Contributing",
        "License",
    ):
        assert key in readme


def test_settings() -> None:
    """Test settings."""
    cfg = settings.Settings()


def test_settings_file_full() -> None:
    """Test settings."""
    cfg = settings.Settings(cfg=Path("gitconductor.toml"))
    assert cfg.gitlab.get("ssl_verify") == False


@pytest.mark.tmp_path
def test_settings_file_partial() -> None:
    """Test settings."""
    with open("gitconductor.toml", "w") as fobj:
        fobj.write("[gitlab]\nssl_verify = false\n")
    cfg = settings.Settings(cfg=Path("gitconductor.toml"))
    assert cfg.gitlab.get("ssl_verify") == False