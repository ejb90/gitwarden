"""Gitlab-related constructs."""

from __future__ import annotations
import os
import pathlib
import typing

import git
import gitlab
from pydantic import BaseModel, Field
import rich
import rich.console
import rich.live
import rich.progress
import rich.table



PROGRESS = rich.progress.Progress(
    # rich.progress.TextColumn("[bold blue]{task.fields[filename]}[/]"),
    rich.progress.BarColumn(),
    rich.progress.MofNCompleteColumn(),
)
TASK = PROGRESS.add_task(description="Processing", total=0)
TABLE = rich.table.Table()
[TABLE.add_column(c) for c in ["Name", "Tree", "Branch", "Path", "Remote"]]
CONSOLE = rich.console.Console()
LIVE = rich.live.Live(console=CONSOLE, refresh_per_second=10)
LIVE.start()


class GitlabGroup(BaseModel):
    """A Gitlab Group convenience class.

    Attributes:
        ...
    """

    gitlab_group: str
    gitlab_url: str = "https://gitlab.com"
    gitlab_key: str = os.environ.get("GITLAB_PRIVATE_KEY", "")
    server: typing.Any | None = None
    group: typing.Any | None = None
    path: pathlib.Path = pathlib.Path().resolve()
    flat: bool = True
    projects: list[str] = Field(default_factory=list)
    subgroups: list[str] = Field(default_factory=list)
    subgroup: bool = False

    def model_post_init(self, __context=None) -> None:
        """Post-init function calls."""
        self.server = gitlab.Gitlab(self.gitlab_url, private_token=self.gitlab_key)
        self.group = self.server.groups.get(self.gitlab_group)
        self.build()

    def build(self) -> None:
        """Build each project object."""
        for project in sorted(self.group.projects.list(all=True), key=lambda x: x.path):
            proj = GitlabProject(project=project)
            if self.flat:
                proj.path = self.path / project.path
            else:
                proj.path = self.path / project.path.replace(self.path.name + "-", "")
            self.projects.append(proj)
        for group in self.group.subgroups.list(all=True):
            grp = GitlabGroup(
                gitlab_url=self.gitlab_url,
                gitlab_key=self.gitlab_key,
                gitlab_group=group.full_path,
                path=self.path if self.flat else self.path / group.path,
                flat=self.flat,
                subgroup=True,
            )
            self.subgroups.append(grp)

    @property
    def count(self) -> int:
        """How many repositories are in the full group structure?"""
        count = len(self.projects)
        for subgroup in self.subgroups:
            count += subgroup.count
        return count

    def recursive_command(self, command: str, **kwargs) -> None:
        """Recursively walk down group tree, finding projects and executing commands."""
        # self._rich_progress_bar(command)
        # self._rich_table(command)
        if not self.subgroup:
            PROGRESS.update(TASK, total=self.count)
        
        for project in self.projects:
            if hasattr(project, command):
                getattr(project, command)(**kwargs)
                TABLE.add_row(*project.row)
                PROGRESS.advance(TASK)
            else:
                raise Exception(f'Command "{command}" not recognised.')
            LIVE.update(rich.console.Group(TABLE, PROGRESS))

        for subgroup in self.subgroups:
            subgroup.recursive_command(command)                

    # def _rich_progress_bar(self, description: str):
    #     """"""
    #     self._progress = rich.progress.Progress()
    #     self._progress.add_task(description=description, total=self.count)

    # def _rich_table(
    #     self, title: str, columns: list[str] = ["Name", "Group", "Describe", "Remote"]
    # ):
    #     """"""
    #     self._table = rich.table.Table(title=title)
    #     for column in columns:
    #         self._table.add_column(column)


class GitlabProject(BaseModel):
    """A Gitlab Project convenience class."""

    project: typing.Any
    path: pathlib.Path | None = None
    git: typing.Any | None = None
    row: str = ""

    def model_post_init(self, __context=None) -> None:
        """Post-init function calls."""
        if self.path is None:
            self.path = pathlib.Path() / self.project.path

    def build_local_repo(self):
        """Clone/check local repo."""
        if not self.path.is_dir():
            self.git = git.Repo.clone_from(self.project.ssh_url_to_repo, self.path)
        else:
            self.git = git.Repo(self.path)

    def clone(self):
        """"""
        self.build_local_repo()
        self.row = [
            pathlib.Path(self.git.working_tree_dir).name,
            self.project.path_with_namespace,
            self.git.git.rev_parse("--abbrev-ref", "HEAD"),
            str(self.path),
            self.git.remote(name="origin").url,
        ]
