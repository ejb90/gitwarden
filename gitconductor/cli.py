"""Main CLI arguments.

Interact with Gitlab via API.
"""

import os
import pathlib

import rich.console
import rich.markdown
import rich.tree
import rich_click as click

from gitconductor import gitlab, misc, output, settings, visualise

click.rich_click.TEXT_MARKUP = True
click.rich_click.MARKDOWN_SYNTAX = "commonmark"


@click.group(help=misc.readme_header())
@click.option(
    "--gitlab-url", type=str, default=os.environ.get("GITCONDUCTOR_URL", None), required=False
)
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
    """Dummy for click."""
    ctx.ensure_object(dict)
    cfg = settings.Settings(cfg=cfg)
    ctx.obj["url"] = gitlab_url if gitlab_url else cfg.gitconductor_gitlab_url
    ctx.obj["key"] = gitlab_key if gitlab_key else cfg.gitconductor_gitlab_api_key
    ctx.obj["cfg"] = cfg
    ctx.obj["state"] = state


# =====================================================================================================================
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


# =====================================================================================================================
@cli.command()
@click.pass_context
@click.argument(
    "viz_type",
    type=click.Choice(["tree", "table", "access"]),
    required=True,
)
@click.option(
    "--explicit",
    type=bool,
    is_flag=True,
    default=False,
    help="Explicitly show each individual user for each sub-Group and Project.",
)
@click.option("--maxdepth", type=int, default=None, help="Maximum recursion depth to traverse for output.")
def viz(ctx: click.Context, viz_type: str, explicit: bool, maxdepth: int | None) -> None:
    """Visualise the hierarchy recursively in different ways.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        viz_type (str):                     Visualisation type.
        explicit (bool):                    Show all info for all projects/groups.
        maxdepth (int):                     Maximum recursion depth (0=PWD).

    Returns:
        None
    """
    group = misc.load_cfg(ctx.obj["state"])

    rich.tree.Tree("Tree")
    if viz_type == "tree":
        visualise.tree(group)
    elif viz_type == "table":
        visualise.table(group, maxdepth=maxdepth)
    elif viz_type == "access":
        visualise.access(group, explicit=explicit, maxdepth=maxdepth)


@cli.command()
@click.pass_context
def help(ctx: click.Context) -> None:
    """
    Print some generic help from README.md if docs aren't available.
    """
    console = rich.console.Console()
    console.print(rich.markdown.Markdown(misc.readme_header()))
    console.print(rich.markdown.Markdown(misc.readme()["Configuration"]))

    info = "\n".join(misc.readme()["Installation"].splitlines()[4:])
    console.print(rich.markdown.Markdown(info))
    print()