"""Main CLI arguments.

Interact with Gitlab via API.
"""

import os
import pathlib
import pickle

import rich.tree
import rich_click as click

from gitwarden import gitlab, output, visualise


@click.group()
@click.option("--gitlab-url", type=str, default="https://gitlab.com", required=False)
@click.option(
    "--gitlab-key",
    type=str,
    default=os.environ.get("GITLAB_API_KEY", ""),
    required=False,
)
@click.option(
    "--cfg",
    type=click.Path(path_type=pathlib.Path),
    default=None,
    required=False,
)
@click.pass_context
def cli(ctx: click.Context, gitlab_url: str, gitlab_key: str, cfg: pathlib.Path) -> None:
    """Dummy for click."""
    ctx.ensure_object(dict)
    ctx.obj["url"] = gitlab_url
    ctx.obj["key"] = gitlab_key
    ctx.obj["cfg"] = cfg


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
    group = load_cfg(ctx.obj["cfg"])

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
    group = load_cfg(ctx.obj["cfg"])

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
    """Add files to staging area for each in each Project repository in the hierarchy recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        fnames (tuple):                     Files to add.

    Returns:
        None
    """
    group = load_cfg(ctx.obj["cfg"])

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
    """Add commit staged changes for each in each Project repository in the hierarchy recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        message (str):                      Commit message.

    Returns:
        None
    """
    group = load_cfg(ctx.obj["cfg"])

    [output.TABLE.add_column(c) for c in ["Name", "Branch", "Files", "Message"]]
    group.recursive_command("commit", message=message)


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
    group = load_cfg(ctx.obj["cfg"])

    rich.tree.Tree("Tree")
    if viz_type == "tree":
        visualise.tree(group)
    elif viz_type == "table":
        visualise.table(group, maxdepth=maxdepth)
    elif viz_type == "access":
        visualise.access(group, explicit=explicit, maxdepth=maxdepth)


def load_cfg(cfg: pathlib.Path | None) -> gitlab.GitlabGroup | gitlab.GitlabProject:
    """Load Group/Project instance.

    Arguments:
        cfg (pathlib.Path, None):                   Path to cfg serialised pickle, or None.

    Returns:
        gitlab.GitlabGroup, gitlab.GitlabProject:   Returned instance.
    """
    if cfg is None:
        cfg = gitlab.GROUP_FNAME
        if not cfg.is_file():
            for parent in pathlib.Path().resolve().parents:
                cfg = parent / gitlab.GROUP_FNAME
                if cfg.is_file():
                    print(cfg)
                    break
            else:
                raise FileNotFoundError(f'No gitwarden configuration file "{gitlab.GROUP_FNAME}" found up to root.')
    elif isinstance(cfg, pathlib.Path):
        if not cfg.is_file():
            raise FileNotFoundError(f'The provided gitwarden configuration file "{cfg}" does not exist.')
    else:
        raise TypeError("Expected pathlib.Path or None for `cfg`.")

    with open(cfg, "rb") as fobj:
        group = pickle.load(fobj)
        group.rebuild(cfg)

    # Now down-select to the subgroup/project in the pwd
    grp = find_subgroup(group)
    return grp


def find_subgroup(group: gitlab.GitlabGroup | gitlab.GitlabProject) -> gitlab.GitlabGroup | gitlab.GitlabProject:
    """Find subgroup in pwd of Group structure.

    Arguments:
        group (gitlab.GitlabGroup):     Gitlab group instance.

    Returns:
        gitlab.GitlabGroup, None:       Gitlab group instance.

    """
    pwd = pathlib.Path().resolve()
    if group.path.resolve() == pwd:
        return group
    for project in group.projects:
        if project.path.resolve() == pwd:
            return project

    for grp in group.subgroups:
        if grp.path.resolve() == pwd:
            return grp
        return find_subgroup(grp)
    else:
        return group
