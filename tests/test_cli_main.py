"""Test misc functionality via CLI."""

from click.testing import CliRunner

import gitconductor.cli


def test_help() -> None:
    """Test help string."""
    runner = CliRunner()

    result = runner.invoke(gitconductor.cli.cli, ["help"])

    assert result.exit_code == 0
    assert "is a command-line tool and Python library" in result.output


def test_command_help_is_user_facing() -> None:
    """Test command help does not expose implementation docstring sections."""
    runner = CliRunner()

    result = runner.invoke(gitconductor.cli.cli, ["clone", "--help"])

    assert result.exit_code == 0
    assert "Clone a GitLab group or project and save its hierarchy state." in result.output
    assert "Arguments:" not in result.output
    assert "Returns:" not in result.output
