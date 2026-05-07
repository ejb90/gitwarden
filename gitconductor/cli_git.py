"""Git-specific CLI arguments."""

import pathlib

import click

from gitconductor import gitlab, misc, output

from .cli import cli


@cli.command()
@click.argument("name")
@click.argument(
    "directory",
    type=click.Path(path_type=pathlib.Path),
    default=pathlib.Path(),
    required=False,
)
@click.option("--flat", type=bool, is_flag=True, default=False)
@click.pass_context
def clone(ctx: click.Context, name: str, directory: pathlib.Path, flat: bool) -> None:
    """Clone Gitlab (sub-)Group/Project repositories recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        name (str):                         Name of the Gitlab group to recursively clone.
        directory (pathlib.Path, None):     Directory in which to clone repositories.
        flat (bool):                        Flat directory structure?

    Returns:
        None
    """
    [output.TABLE.add_column(c) for c in ["Name", "Tree", "Branch", "Path", "Remote"]]

    group = gitlab.GitlabGroup(
        gitlab_url=ctx.obj["url"],
        gitlab_key=ctx.obj["key"],
        fullname=name,
        name=name,
        flat=flat,
        root=directory,
        cfg=ctx.obj["cfg"],
    )
    group.recursive_command("clone")


@cli.command()
@click.argument(
    "name",
    type=str,
    default=None,
    required=True,
)
@click.pass_context
def branch(ctx: click.Context, name: str) -> None:
    """Add a branch in each Project repository in the hierarchy recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        name (str):                         Name of the branch to checkout.

    Returns:
        None
    """
    group = misc.load_cfg(ctx.obj["state"])

    [output.TABLE.add_column(c) for c in ["Name", "Tree", "Old Branch", "New Branch"]]
    group.recursive_command("branch", name=name)


@cli.command()
@click.argument(
    "name",
    type=str,
    default=None,
    required=True,
)
@click.pass_context
def checkout(ctx: click.Context, name: str) -> None:
    """Checkout a branch in each Project repository in the hierarchy recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        name (str):                         Name of the branch to checkout.

    Returns:
        None
    """
    group = misc.load_cfg(ctx.obj["state"])

    [output.TABLE.add_column(c) for c in ["Name", "Tree", "Old Branch", "New Branch"]]
    group.recursive_command("checkout", name=name)


@cli.command()
@click.argument(
    "fnames",
    nargs=-1,
    type=str,
)
@click.pass_context
def add(ctx: click.Context, fnames: tuple) -> None:
    """Add files to staging area in each Project repository in the hierarchy recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        fnames (tuple):                     Files to add.

    Returns:
        None
    """
    group = misc.load_cfg(ctx.obj["state"])

    [output.TABLE.add_column(c) for c in ["Name", "Branch", "Files"]]
    group.recursive_command("add", fnames=fnames)


@cli.command()
@click.option(
    "-m",
    "--message",
    type=str,
)
@click.pass_context
def commit(ctx: click.Context, message: str) -> None:
    """Commit staged changes in each Project repository in the hierarchy recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        message (str):                      Commit message.

    Returns:
        None
    """
    group = misc.load_cfg(ctx.obj["state"])

    [output.TABLE.add_column(c) for c in ["Name", "Branch", "Files", "Message"]]
    group.recursive_command("commit", message=message)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show status of each Project repository in the hierarchy recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        message (str):                      Commit message.

    Returns:
        None
    """
    group = misc.load_cfg(ctx.obj["state"])

    [output.TABLE.add_column(c) for c in ["Repository", "File", "Status"]]
    group.recursive_command("status")


@cli.command()
@click.pass_context
def push(ctx: click.Context) -> None:
    """Push each Project repository in the hierarchy recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        message (str):                      Commit message.

    Returns:
        None
    """
    group = misc.load_cfg(ctx.obj["state"])
    group.recursive_command("push")
