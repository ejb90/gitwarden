"""Main CLI arguments."""

import os
import pathlib

import rich.console
import rich.markdown
import rich.tree
import rich_click as click

from gitconductor import misc, settings, visualise

click.rich_click.TEXT_MARKUP = "markdown"
click.rich_click.MARKDOWN_SYNTAX = "commonmark"


@click.group(help=misc.readme_header())
@click.option("--gitlab-url", type=str, default=os.environ.get("GITCONDUCTOR_GITLAB_URL", None), required=False)
@click.option(
    "--gitlab-key",
    type=str,
    default=os.environ.get("GITCONDUCTOR_GITLAB_API_KEY", None),
    required=False,
)
@click.option(
    "--cfg",
    type=click.Path(path_type=pathlib.Path),
    default=os.environ.get("GITCONDUCTOR_CONFIG", pathlib.Path().home() / ".config/gitconductor/gitconductor.yaml"),
    required=False,
)
@click.option(
    "--state",
    type=click.Path(path_type=pathlib.Path),
    default=None,
    required=False,
)
@click.pass_context
def cli(ctx: click.Context, gitlab_url: str, gitlab_key: str, cfg: pathlib.Path, state: pathlib.Path) -> None:
    """Manage nested GitLab groups and projects."""
    ctx.ensure_object(dict)
    cfg = settings.Settings(cfg=cfg)
    ctx.obj["url"] = gitlab_url if gitlab_url else cfg.gitconductor_gitlab_url
    ctx.obj["key"] = gitlab_key if gitlab_key else cfg.gitconductor_gitlab_api_key
    ctx.obj["cfg"] = cfg
    ctx.obj["state"] = state


# Hack to add submodules to the CLI without circular imports.
# This is required because the submodules need to import the main CLI group to add their own subcommands, but the main
# CLI group also needs to import the submodules to add them as subcommands.
from . import cli_git, cli_python  # noqa: F401,E402


# =====================================================================================================================
@cli.group()
@click.pass_context
def viz(ctx: click.Context) -> None:
    """Visualise the hierarchy recursively in different ways."""
    pass


@viz.command()
@click.pass_context
def tree(ctx: click.Context) -> None:
    """Visualise the hierarchy as a tree."""
    group = misc.load_cfg(ctx.obj["state"])
    visualise.tree(group)


@viz.command()
@click.pass_context
@click.option("--maxdepth", type=int, default=None, help="Maximum recursion depth to traverse for output.")
def table(ctx: click.Context, maxdepth: int | None) -> None:
    """Visualise the hierarchy as a table."""
    group = misc.load_cfg(ctx.obj["state"])
    visualise.table(group, maxdepth=maxdepth)


@viz.command()
@click.pass_context
@click.option(
    "--explicit",
    is_flag=True,
    default=False,
    help="Explicitly show each individual user for each subgroup and project in the full tree. "
    "Else abbreviate to show only the highest level of access for each group and each user.",
)
@click.option(
    "--matrix",
    is_flag=True,
    default=False,
    help="Show a 2D matrix of each user and each group.",
)
@click.option("--maxdepth", type=int, default=None, help="Maximum recursion depth to traverse for output.")
def access(ctx: click.Context, explicit: bool, maxdepth: int | None, matrix: bool = False) -> None:
    """Visualise access recursively."""
    group = misc.load_cfg(ctx.obj["state"])

    if matrix:
        visualise.access_matrix(group, maxdepth=maxdepth)
    else:
        visualise.access(group, explicit=explicit, maxdepth=maxdepth)


# =====================================================================================================================
@cli.command()
def help() -> None:
    """Print some generic help from README.md if docs aren't available."""
    console = rich.console.Console()
    console.print(rich.markdown.Markdown(misc.readme_header()))
    console.print(rich.markdown.Markdown(misc.readme()["Configuration"]))

    info = "\n".join(misc.readme()["Installation"].splitlines()[4:])
    console.print(rich.markdown.Markdown(info))
