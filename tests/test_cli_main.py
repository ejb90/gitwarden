"""Test misc functionality via CLI."""

from click.testing import CliRunner
from pytest import MonkeyPatch

import gitconductor.cli
from gitconductor import output


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
    assert "Clone a GitLab group or project from its full HTTPS or SSH URL." in result.output
    assert "Arguments:" not in result.output
    assert "Returns:" not in result.output


def test_cli_restores_cursor(monkeypatch: MonkeyPatch) -> None:
    """Test CLI restores the terminal cursor after command invocation."""
    calls = []

    def show_cursor(show: bool) -> None:
        calls.append(show)

    monkeypatch.setattr(output.CONSOLE, "show_cursor", show_cursor)

    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["help"])

    assert result.exit_code == 0
    assert calls[-1] is True


def test_cli_restores_cursor_after_command_help(monkeypatch: MonkeyPatch) -> None:
    """Test CLI restores the terminal cursor after eager help output."""
    calls = []

    def show_cursor(show: bool) -> None:
        calls.append(show)

    monkeypatch.setattr(output.CONSOLE, "show_cursor", show_cursor)

    runner = CliRunner()
    result = runner.invoke(gitconductor.cli.cli, ["clone", "--help"])

    assert result.exit_code == 0
    assert calls[-1] is True
