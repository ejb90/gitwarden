"""Main CLI arguments.

Interact with Gitlab via API.

List of git commands, see `git --help`:

* clone     Clone a repository into a new directory
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
* branch    List, create, or delete branches
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
def clone(
    ctx: click.Context, group: str, directory: pathlib.Path | None, flat: bool
) -> None:
    """Clone repos recursively.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        group (str):                        Name of the Gitlab group to recursively clone.
        directory (pathlib.Path, None):     Directory in which to clone repositories.

    Returns:
        None
    """
    [gitlab.TABLE.add_column(c) for c in ["Name", "Tree", "Branch", "Path", "Remote"]]

    group = gitlab.GitlabGroup(
        gitlab_url=ctx.obj["url"],
        gitlab_key=ctx.obj["key"],
        gitlab_group=group,
        flat=flat,
    )
    if directory is not None:
        group.path = directory
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
        name (str):                         Name of the branch to create.

    Returns:
        None
    """
    [gitlab.TABLE.add_column(c) for c in ["Name", "Tree", "Old Branch", "New Branch"]]

    if gitlab.GROUP_FNAME.is_file():
        with open(gitlab.GROUP_FNAME, "rb") as fobj:
            group = pickle.load(fobj)

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
    [gitlab.TABLE.add_column(c) for c in ["Name", "Tree", "Old Branch", "New Branch"]]

    if gitlab.GROUP_FNAME.is_file():
        with open(gitlab.GROUP_FNAME, "rb") as fobj:
            group = pickle.load(fobj)

    group.recursive_command("checkout", name=name)