"""Interact with Gitlab via API.

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

from __future__ import annotations

import os
import pathlib
import pickle
import typing

import git
import gitlab
import rich
import rich.console
import rich.layout
import rich.progress
import rich_click as click
from pydantic import BaseModel, Field


class GitlabGroup(BaseModel):
    """A Gitlab Group convenience class.

    Attributes:
        ...
    """

    gitlab_group: typing.Any
    gitlab_server: typing.Any
    path: pathlib.Path = pathlib.Path().resolve()
    cfg: pathlib.Path = pathlib.Path().resolve() / ".gitwarden/gitwarden.pkl"
    projects: list[str] = Field(default_factory=list)
    subgroups: list[str] = Field(default_factory=list)
    subgroup: bool = False

    _progress: typing.Any = None
    _table: typing.Any = None

    def model_post_init(self, __context=None) -> None:
        """Post-init function calls."""
        if self.cfg.is_file():
            self.load(self.cfg)
        self.build_projects()
        self.save()

    def save(self) -> None:
        """Serialize the model to pickle."""
        if not self.cfg.parent.is_dir():
            self.cfg.parent.mkdir()
        with open(self.cfg, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, cfg: pathlib.Path) -> GitlabGroup:
        """Load serialised model from pickle."""
        with open(cfg, "rb") as fobj:
            obj = pickle.load(fobj)
        return obj

    @property
    def count(self) -> int:
        """How many repositories are in the full group structure?"""
        count = 0
        for _project in self.projects:
            count += 1
        for subgroup in self.subgroups:
            count += subgroup.count
        return count

    def _rich_progress_bar(self, description: str) -> None:
        """"""
        self._progress = rich.progress.Progress()
        self._progress.add_task(description=description, total=self.count)

    def _rich_table(self, title: str, columns: list[str] | None = None) -> None:
        """"""
        if columns is None:
            columns = ["Name", "Group", "Describe", "Remote"]
        self._table = rich.table.Table(title=title)
        for column in columns:
            self._table.add_column(column)

    def build_projects(self) -> None:
        """Build each project object."""
        for project in self.gitlab_group.projects.list(all=True):
            self.projects.append(GitlabProject(gitlab_project=project))
        for group in self.gitlab_group.subgroups.list(all=True):
            subgroup = GitlabGroup(gitlab_group=group)
            subgroup = self.gitlab_server.groups.get(subgroup.id)
            subgroup.subgroup = True
            self.subgroups.append(subgroup)

    def recursive_command(self, command: str, **kwargs) -> None:
        """Recursively walk down group tree, finding projects and executing commands."""
        if not self.subgroup:
            self._console = rich.console.Console()
            layout = rich.layout.Layout()
            layout.split(
                rich.layout.Layout(name="top", ratio=3),
                rich.layout.Layout(name="bottom", ratio=1),
            )
            self._rich_progress_bar(command)
            self._rich_table(command)

        for project in self.projects:
            if hasattr(project, command):
                result = getattr(project, command)(**kwargs)
                self._table.add_row(*result)

        for subgroup in self.subgroups:
            subgroup.recursive_command()

        if not self.subgroup:
            self._console.print(self._table)


class GitlabProject:
    """A Gitlab Project convenience class."""

    def __init__(self, gitlab_project) -> None:
        self.gitlab_project = gitlab_project
        self.path = pathlib.Path() / self.gitlab_project.path
        self.git = None

    def build_local_repo(self) -> None:
        """Clone/check local repo."""
        if not self.path.is_dir():
            self.git = git.Repo.clone_from(self.gitlab_project.ssh_url_to_repo, self.path)
        else:
            self.git = git.Repo(self.path)

    def clone(self, directory: pathlib.Path | None=None):
        """"""
        if directory is not None:
            self.path = directory
        self.build_local_repo()
        return [
            pathlib.Path(self.git.working_tree_dir).name,
            "",
            self.git.git.rev_parse("--abbrev-ref", "HEAD"),
            self.git.remote(name="origin").url,
        ]

    def branch(self) -> None:
        """"""


def get_gitlab_group(
    group: str,
    url: str = "https://gitlab.com",
    key: str = os.environ.get("GITLAB_PRIVATE_KEY"),
) -> GitlabGroup:
    """Get GitlabGroup object.

    Arguments:
        ...

    Returns:
        ...
    """

    gitlab_server = gitlab.Gitlab(url, private_token=key)
    group = gitlab_server.groups.get(group)
    return GitlabGroup(gitlab_group=group, gitlab_server=gitlab_server)


@click.group()
def main() -> None:
    """Dummy for click"""
    pass


@main.command()
@click.argument("group")
@click.argument(
    "directory",
    type=click.Path(path_type=pathlib.Path),
    default=None,
    required=False,
)
def clone(group: str, directory: pathlib.Path | None) -> None:
    """Clone repos recursively.

    Arguments:
        group (str):                        Name of the Gitlab group to recursively clone.
        directory (pathlib.Path, None):     Directory in which to clone repositories.

    Returns:
        None
    """
    group = get_gitlab_group(group)
    # group.clone(directory)
    group.recursive_command("clone", directory=directory)


@main.command()
def branch() -> None:
    """Branch repos recursively.

    Arguments:
        ...

    Returns:
        None
    """


@main.command()
def checkout() -> None:
    """Checkout repos recursively.

    Arguments:
        ...

    Returns:
        ...
    """


@main.command()
def pull() -> None:
    """Pull repos recursively.

    Arguments:
        ...

    Returns:
        ...
    """
