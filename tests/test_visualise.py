"""Test visualisation helpers."""

from pathlib import Path

import gitlab

from gitconductor import visualise


class HiddenMembersGroup:
    """Group-like object with hidden membership."""

    path = Path("/tmp/group/project")
    visibility = "private"

    @property
    def members(self) -> list:
        """Raise a GitLab permission-style error."""
        raise gitlab.exceptions.GitlabListError("403 Forbidden", response_code=403)


class VisibleMember:
    """Member-like object."""

    id = 1
    name = "Ellis"
    access_level = 50
    public_email = ""
    expires_at = None


class VisibleMembersGroup:
    """Group-like object with visible membership."""

    path = Path("/tmp/group/project")
    visibility = "private"

    @property
    def members(self) -> list[VisibleMember]:
        """Return visible members."""
        return [VisibleMember()]


def test_build_access_warns_when_members_hidden() -> None:
    """Test access rendering degrades when membership is hidden."""
    rows = visualise.build_access(HiddenMembersGroup(), root=Path("/tmp/group"))

    assert rows == [
        [
            "group/project",
            visualise.ACCESS_WARNING_USER,
            visualise.ACCESS_WARNING_LEVEL,
            "",
            "403: 403 Forbidden",
            "private",
        ]
    ]


def test_build_access_skips_hidden_members_in_colour_only_mode() -> None:
    """Test matrix input keeps hidden-member warning rows."""
    rows = visualise.build_access(HiddenMembersGroup(), root=Path("/tmp/group"), colour_only=True)

    assert rows[0][1] == visualise.ACCESS_WARNING_USER


def test_build_access_still_lists_visible_members() -> None:
    """Test visible membership is unchanged."""
    rows = visualise.build_access(VisibleMembersGroup(), root=Path("/tmp/group"))

    assert rows[0][:3] == ["group/project", "Ellis", "[blue]Owner"]
