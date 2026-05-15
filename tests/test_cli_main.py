"""Test misc functionality via CLI."""

from click.testing import CliRunner

import gitconductor.cli


def test_help() -> None:
    """Test help string."""
    runner = CliRunner()

    result = runner.invoke(gitconductor.cli.cli, ["help"])

    assert result.exit_code == 0
    assert "is a command-line tool and Python library" in result.output
