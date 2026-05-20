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
        "Quick Start",
        "Documentation",
        "Development & Contributing",
        "License",
    ):
        assert key in readme


def test_settings() -> None:
    """Test settings."""
    settings.Settings()


@pytest.mark.parametrize(
    ("remote", "api_url", "full_path"),
    (
        ("https://gitlab.com/ejb90-group", "https://gitlab.com", "ejb90-group"),
        ("https://gitlab.example.com/group/subgroup.git", "https://gitlab.example.com", "group/subgroup"),
        ("ssh://git@gitlab.example.com/group/subgroup.git", "https://gitlab.example.com", "group/subgroup"),
        ("git@gitlab.example.com:group/subgroup.git", "https://gitlab.example.com", "group/subgroup"),
    ),
)
def test_parse_gitlab_remote(remote: str, api_url: str, full_path: str) -> None:
    """Test parsing GitLab clone URLs."""
    assert gitlab.parse_gitlab_remote(remote) == (api_url, full_path)


def test_parse_gitlab_remote_rejects_bare_group() -> None:
    """Test clone targets must be full URLs."""
    with pytest.raises(ValueError, match="Clone target must be a full GitLab URL"):
        gitlab.parse_gitlab_remote("ejb90-group")


def test_clone_target_path() -> None:
    """Test clone preflight target path."""
    assert gitlab.clone_target_path("https://gitlab.com/ejb90-group/models", Path("."), flat=False) == (
        Path.cwd() / "ejb90-group"
    )


def test_clone_target_path_flat() -> None:
    """Test flat clone preflight target path."""
    assert gitlab.clone_target_path("https://gitlab.com/ejb90-group/models", Path("."), flat=True) == (
        Path.cwd() / gitlab.GROUP_FNAME
    )


def test_settings_file_full() -> None:
    """Test settings."""
    cfg = settings.Settings(cfg=Path("gitconductor.toml"))
    assert not cfg.gitlab.get("ssl_verify")


@pytest.mark.tmp_path
def test_settings_file_partial() -> None:
    """Test settings."""
    with open("gitconductor.toml", "w") as fobj:
        fobj.write("[gitlab]\nssl_verify = false\n")
    cfg = settings.Settings(cfg=Path("gitconductor.toml"))
    assert not cfg.gitlab.get("ssl_verify")
