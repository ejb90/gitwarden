"""Gitlab-related constructs."""

from __future__ import annotations

import os
import pathlib
import pickle
import typing

import git
import gitlab
import rich
import rich.console
from pydantic import BaseModel, Field

from gitwarden import output

GROUP_FNAME = pathlib.Path(".gitwarden.pkl")


class GitlabInstance(BaseModel):
    """A Gitlab generic instance convenience class.

    Attributes:
        ...
    """

    gitlab_url: str = "https://gitlab.com"
    gitlab_key: str = os.environ.get("GITLAB_API_KEY", "")
    server: typing.Any | None = None
    root: pathlib.Path = pathlib.Path().resolve()
    path: pathlib.Path = pathlib.Path().resolve()


class GitlabGroup(GitlabInstance):
    """A Gitlab Group convenience class.

    Attributes:
        ...
    """

    name: str
    fullname: str = ""
    group: typing.Any | None = None
    flat: bool = False
    projects: list[str] = Field(default_factory=list)
    subgroups: list[str] = Field(default_factory=list)
    subgroup: bool = False

    def model_post_init(self, __context: str | None = None) -> None:
        """Post-init function calls."""
        print(self.name)
        self.server = gitlab.Gitlab(self.gitlab_url, private_token=self.gitlab_key)
        self.root = self.root.resolve()
        self.group = self.server.groups.get(self.fullname)
        self.path = self.root / self.fullname.replace(os.sep, "-") if self.flat else self.root / self.fullname
        self.build()

    @property
    def members(self) -> list:
        """Get members."""
        self.group = self.server.groups.get(self.group.id)
        return self.group.members_all.list(all=True)

    @property
    def toplevel_dir(self) -> pathlib.Path:
        """What is the top level work directory?

        Returns:
            pathlib.Path:       Directory name.
        """
        if self.flat:
            return self.root
        else:
            return self.root / self.path.relative_to(self.root).parts[0]

    def build(self) -> None:
        """Build each project object."""
        # Loop through projects in the group, set up GitlabProject instance for the project
        for project in sorted(self.group.projects.list(all=True), key=lambda x: x.path):
            proj = GitlabProject(project=project, root=self.root)
            if self.flat:
                proj.path = self.path.parent / f"{self.path.name}-{project.path}"
            else:
                proj.path = self.path / project.path
            self.projects.append(proj)

        # Loop through sub-groups in the group, set up GitlabGroup instance for the subgroup
        for group in self.group.subgroups.list(all=True):
            grp = GitlabGroup(
                gitlab_url=self.gitlab_url,
                gitlab_key=self.gitlab_key,
                fullname=group.full_path,
                name=pathlib.Path(group.full_path).name,
                root=self.root,
                flat=self.flat,
                subgroup=True,
            )
            self.subgroups.append(grp)

    @property
    def count(self) -> int:
        """How many repositories are in the full group structure?

        Returns:
            int:        Total number of projects in all recursive subgeoups.
        """
        count = len(self.projects)
        for subgroup in self.subgroups:
            count += subgroup.count
        return count

    def recursive_command(self, command: str, **kwargs: dict) -> None:
        """Recursively walk down group tree, finding projects and executing commands."""
        if not self.subgroup:
            output.PROGRESS_TOTAL.update(output.TASK_TOTAL, description=self.name, total=self.count)
        else:
            output.PROGRESS_TOTAL.update(output.TASK_TOTAL, description=self.name)
        for project in self.projects:
            if hasattr(project, command):
                getattr(project, command)(**kwargs)
                output.TABLE.add_row(*project.row)
                output.PROGRESS_TOTAL.update(output.TASK_TOTAL, description=project.name)
                output.PROGRESS_TOTAL.advance(output.TASK_TOTAL)
                output.LIVE.update(
                    rich.console.Group(output.TABLE, output.PROGRESS_PROJECT, output.PROGRESS_TOTAL),
                    refresh=True,
                )
            else:
                raise Exception(f'Command "{command}" not recognised.')

        for subgroup in self.subgroups:
            subgroup.recursive_command(command, **kwargs)

        if not self.subgroup:
            output.LIVE.update(rich.console.Group(output.TABLE), refresh=True)
        self.dump()

    def dump(self) -> None:
        """Dump to file."""
        with open(self.toplevel_dir / GROUP_FNAME, "wb") as fobj:
            pickle.dump(self, fobj)


class GitlabProject(GitlabInstance):
    """A Gitlab Project convenience class."""

    project: typing.Any
    name: str = ""
    git: typing.Any | None = None
    row: str = ""

    def model_post_init(self, __context: str | None = None) -> None:
        """Post-init function calls."""
        self.server = gitlab.Gitlab(self.gitlab_url, private_token=self.gitlab_key)
        if self.path is None:
            self.path = pathlib.Path() / self.project.path

    @property
    def members(self) -> list:
        """Get members."""
        self.project = self.server.projects.get(self.project.id)
        return self.project.members_all.list(all=True)

    def clone(self) -> None:
        """Clone a repository.

        Returns:
            None
        """
        self.git = git.Repo.clone_from(self.project.ssh_url_to_repo, self.path, progress=output.CloneProgress())
        self.name = pathlib.Path(self.git.working_tree_dir).name

        self.row = [
            self.name,
            str(self.path.relative_to(self.root)),
            self.git.git.rev_parse("--abbrev-ref", "HEAD"),
            str(self.path.relative_to(self.root)),
            self.git.remote(name="origin").url,
        ]

    def branch(self, name: str | None = None) -> None:
        """Make branch in a repository.

        Returns:
            None
        """
        if not self.path:
            raise Exception(f'Cannot find repository @ "{self.path}"')
        self.git = git.Repo(self.path)

        self.row = [
            self.name,
            str(self.path.relative_to(self.root)),
            self.git.git.rev_parse("--abbrev-ref", "HEAD"),
            name,
        ]
        self.git.create_head(name)

    def checkout(self, name: str | None = None) -> None:
        """Checkout a branch in a repository.

        Returns:
            None
        """
        if not self.path:
            raise Exception(f'Cannot find repository @ "{self.path}"')
        self.git = git.Repo(self.path)

        self.row = [
            self.name,
            str(self.path.relative_to(self.root)),
            self.git.git.rev_parse("--abbrev-ref", "HEAD"),
            name,
        ]
        self.git.heads[name].checkout()
