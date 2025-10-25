"""Main CLI arguments."""

import os
import pathlib

import rich_click as click

import gitwarden.gitlab as gitlab


@click.group()
@click.option("--gitlab-url", type=str, default="https://gitlab.com", required=False)
@click.option(
    "--gitlab-key",
    type=str,
    default=os.environ.get("GITLAB_PRIVATE_KEY", ""),
    required=False,
)
@click.pass_context
def cli(ctx: click.Context, gitlab_url: str, gitlab_key: str):
    """Dummy for click"""
    ctx.ensure_object(dict)
    ctx.obj["url"] = gitlab_url
    ctx.obj["key"] = gitlab_key


@cli.command()
@click.argument("group")
@click.argument(
    "directory",
    type=click.Path(path_type=pathlib.Path),
    default=None,
    required=False,
)
@click.option("--flat", type=bool, default=False, required=False)
@click.pass_context
def clone(ctx: click.Context, group: str, directory: pathlib.Path | None, flat: bool) -> None:
    """Clone repos recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags
        group (str):                        Name of the Gitlab group to recursively clone.
        directory (pathlib.Path, None):     Directory in which to clone repositories.

    Returns:
        None
    """

    group = gitlab.GitlabGroup(
        gitlab_url=ctx.obj["url"], 
        gitlab_key=ctx.obj["key"], 
        gitlab_group=group,
        flat=flat,
    )
    if directory is not None:
        group.path = directory
    # group.recursive_command("clone")
