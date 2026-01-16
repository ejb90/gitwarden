"""Test misc functionality."""

import pathlib

import pytest

from gitwarden import gitlab, misc


def test_load_cfg_directly(repo: pathlib.Path) -> None:
    """Load cfg file directly."""
    grp = misc.load_cfg(repo / gitlab.GROUP_FNAME)
    assert isinstance(grp, gitlab.GitlabGroup)


def test_load_cfg_missing_walk() -> None:
    """Load missing cfg file, walking up to root."""
    with pytest.raises(FileNotFoundError, match=r'No gitwarden configuration file ".+" found up to root.'):
        misc.load_cfg(None)


def test_load_cfg_directly_missing() -> None:
    """Load missing cfg file."""
    with pytest.raises(FileNotFoundError, match=r'The provided gitwarden configuration file ".+" does not exist.'):
        misc.load_cfg(pathlib.Path("missing_file"))


def test_load_cfg_wrong_type() -> None:
    """Load cfg file with wrong type."""
    with pytest.raises(TypeError, match=r"Expected pathlib.Path or None for `cfg`."):
        misc.load_cfg(1)
