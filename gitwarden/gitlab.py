"""Gitlab-related constructs."""

from __future__ import annotations
import os
import pathlib
import pickle
import typing

import git
import gitlab
from pydantic import BaseModel, Field
import rich
import rich.console
import rich.live
import rich.progress
import rich.table
import rich.tree


GROUP_FNAME = pathlib.Path(".gitwarden.pkl")


# 1. Define the known operation names
OP_CODES = [
    "BEGIN",
    "CHECKING_OUT",
    "COMPRESSING",
    "COUNTING",
    "END",
    "FINDING_SOURCES",
    "RECEIVING",
    "RESOLVING",
    "WRITING",
]

# 2. Build the map using a dictionary comprehension
# It maps the integer value to its string name
OP_CODE_MAP = {
    getattr(git.RemoteProgress, op_code): op_code
    for op_code in OP_CODES
}

PROGRESS_TOTAL = rich.progress.Progress(
    rich.progress.TextColumn("Project: [progress.description]{task.description:30}"),
    rich.progress.BarColumn(),
    rich.progress.MofNCompleteColumn(),
)
PROGRESS_PROJECT = rich.progress.Progress(
    rich.progress.TextColumn("Step:    [progress.description]{task.description:30}"),
    rich.progress.BarColumn(),
    rich.progress.TextColumn("[green][progress.completed]{task.completed}%"),
)
TASK_TOTAL = PROGRESS_TOTAL.add_task(description="", total=0)
TASK_PROJECT = PROGRESS_PROJECT.add_task(description="", total=100)
TABLE = rich.table.Table()
CONSOLE = rich.console.Console()
LIVE = rich.live.Live(console=CONSOLE, refresh_per_second=10)
LIVE.start()


class CloneProgress(git.RemoteProgress):
    """Override git.RemoteProgress to update progress bars."""
    last_op_code = None

    def update(self, op_code, cur_count, max_count=None, message=''):
        """Get updates from git, pass to rich output."""
        # If the op_code changes, reset the counter and change name on the progress bar.
        if op_code != self.last_op_code:
            PROGRESS_PROJECT.reset(TASK_PROJECT)
            self.last_op_code = op_code

        # Caulcate the percentage done for this op_code
        percent = 0
        if max_count:
            percent = int((cur_count / max_count) * 100)
        description = OP_CODE_MAP.get(op_code, "").title()
        
        # Update the project's progress bar
        PROGRESS_PROJECT.update(TASK_PROJECT, description=description, completed=percent)
        # Push to terminal
        LIVE.update(rich.console.Group(TABLE, PROGRESS_PROJECT, PROGRESS_TOTAL), refresh=True)


class GitlabGroup(BaseModel):
    """A Gitlab Group convenience class.

    Attributes:
        ...
    """
    name: str
    shortname: str = ""
    gitlab_url: str = "https://gitlab.com"
    gitlab_key: str = os.environ.get("GITLAB_PRIVATE_KEY", "")
    server: typing.Any | None = None
    group: typing.Any | None = None
    root: pathlib.Path = pathlib.Path().resolve()
    path: pathlib.Path = pathlib.Path().resolve()
    flat: bool = True
    projects: list[str] = Field(default_factory=list)
    subgroups: list[str] = Field(default_factory=list)
    subgroup: bool = False

    def model_post_init(self, __context=None) -> None:
        """Post-init function calls."""
        self.shortname = pathlib.Path(self.name).parts[-1]
        self.server = gitlab.Gitlab(self.gitlab_url, private_token=self.gitlab_key)
        self.root = self.root.resolve()
        self.group = self.server.groups.get(self.name)
        self.path = self.root / self.name
        self.build()

    @property
    def toplevel_dir(self):
        return self.root / self.path.relative_to(self.root).parts[0]

    def build(self) -> None:
        """Build each project object."""
        # Loop through projects in the group, set up GitlabProject instance for the project
        for project in sorted(self.group.projects.list(all=True), key=lambda x: x.path):
            proj = GitlabProject(project=project, root=self.root)
            if self.flat:
                proj.path = self.path / project.path
            else:
                proj.path = self.path / project.path.replace(self.path.name + "-", "")
            self.projects.append(proj)

        # Loop through sub-groups in the group, set up GitlabGroup instance for the subgroup
        for group in self.group.subgroups.list(all=True):
            grp = GitlabGroup(
                gitlab_url=self.gitlab_url,
                gitlab_key=self.gitlab_key,
                name=group.full_path,
                root=self.root,
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
        if not self.subgroup:
            PROGRESS_TOTAL.update(TASK_TOTAL, description=self.name, total=self.count)
        else:
            PROGRESS_TOTAL.update(TASK_TOTAL, description=self.name)
        
        for project in self.projects:
            if hasattr(project, command):
                getattr(project, command)(**kwargs)
                TABLE.add_row(*project.row)
                PROGRESS_TOTAL.update(TASK_TOTAL, description=project.name)
                PROGRESS_TOTAL.advance(TASK_TOTAL)
                LIVE.update(rich.console.Group(TABLE, PROGRESS_PROJECT, PROGRESS_TOTAL), refresh=True)
            else:
                raise Exception(f'Command "{command}" not recognised.')

        for subgroup in self.subgroups:
            subgroup.recursive_command(command, **kwargs) 
        
        if not self.subgroup:
            LIVE.update(rich.console.Group(TABLE), refresh=True)
        
        self.dump()

    def dump(self) -> None:
        """Dump to file."""
        with open(self.toplevel_dir / GROUP_FNAME, "wb") as fobj:
            pickle.dump(self, fobj)


class GitlabProject(BaseModel):
    """A Gitlab Project convenience class."""

    project: typing.Any
    name: str = ""
    root: pathlib.Path | None = None
    path: pathlib.Path | None = None
    git: typing.Any | None = None
    row: str = ""

    def model_post_init(self, __context=None) -> None:
        """Post-init function calls."""
        if self.path is None:
            self.path = pathlib.Path() / self.project.path

    def clone(self):
        """"""
        self.git = git.Repo.clone_from(self.project.ssh_url_to_repo, self.path, progress=CloneProgress())
        self.name = pathlib.Path(self.git.working_tree_dir).name

        self.row = [
            self.name,
            str(self.path.relative_to(self.root)),
            self.git.git.rev_parse("--abbrev-ref", "HEAD"),
            str(self.path.relative_to(self.root)),
            self.git.remote(name="origin").url,
        ]
    
    def branch(self, name=None):
        """"""
        if not self.path:
            raise Exception(f"Cannot find repository @ \"{self.path}\"")
        self.git = git.Repo(self.path)

        self.row = [
            self.name,
            str(self.path.relative_to(self.root)),
            self.git.git.rev_parse("--abbrev-ref", "HEAD"),
            name,
        ]
        self.git.create_head(name)

    def checkout(self, name=None):
        """"""
        if not self.path:
            raise Exception(f"Cannot find repository @ \"{self.path}\"")
        self.git = git.Repo(self.path)

        self.row = [
            self.name,
            str(self.path.relative_to(self.root)),
            self.git.git.rev_parse("--abbrev-ref", "HEAD"),
            name,
        ]
        self.git.heads[name].checkout()
