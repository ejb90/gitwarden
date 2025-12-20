"""Main CLI arguments.

Interact with Gitlab via API.

List of git commands, see `git --help`:

* clone     Clone a repository into a new directory                                 DONE
* init      Create an empty Git repository or reinitialize an existing one
* add       Add file contents to the index
* mv        Move or rename a file, a directory, or a symlink
* restore   Restore working tree files
* rm        Remove files from the working tree and from the index
* bisect    Use binary search to find the commit that introduced a bug
* diff      Show changes between commits, commit and working tree, etc
* grep      Print lines matching a pattern
* log       Show commit logs
* show      Show various types of objects
* status    Show the working tree status
* branch    List, create, or delete branches                                        DONE
* commit    Record changes to the repository
* merge     Join two or more development histories together
* rebase    Reapply commits on top of another base tip
* reset     Reset current HEAD to the specified state
* switch    Switch branches
* tag       Create, list, delete or verify a tag object signed with GPG
* fetch     Download objects and refs from another repository
* pull      Fetch from and integrate with another repository or a local branch
* push      Update remote refs along with associated objects

See:

* [gitman](https://gitman.readthedocs.io/en/latest/)
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
    default=os.environ.get("GITLAB_PRIVATE_KEY", ""),
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
    """Clone repos recursively.

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
    """Clone repos recursively.

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
    """Clone repos recursively.

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
@click.pass_context
@click.argument(
    "viz_type",
    type=click.Choice(["tree", "table", "access"]),
    required=True,
)
@click.option("--explicit", type=bool, is_flag=True, default=False)
def viz(ctx: click.Context, viz_type: str, explicit: bool) -> None:
    """Clone repos recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        viz_type (str):                     Visualisation type.
        explicit (bool):                    Show all info for all projects/groups.

    Returns:
        None
    """
    group = load_cfg(ctx.obj["cfg"])

    rich.tree.Tree("Tree")
    if viz_type == "tree":
        visualise.tree(group)
    elif viz_type == "table":
        visualise.table(group)
    elif viz_type == "access":
        visualise.access(group, explicit)


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
                    break
            else:
                raise Exception(f'No gitwarden configuration file "{gitlab.GROUP_FNAME}" found up to root.')
    else:
        raise Exception(f'The provided gitwarden configuration file "{cfg}" does not exist.')

    with open(cfg, "rb") as fobj:
        group = pickle.load(fobj)
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
        return None
