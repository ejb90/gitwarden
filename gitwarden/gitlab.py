"""Gitlab-related constructs."""

from __future__ import annotations
import os
import pathlib
import typing

import git
import gitlab
from pydantic import BaseModel, Field


from icecream import ic


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
                proj.path = self.path / project.path.replace(self.path.name+"-", "")            
            self.projects.append(proj)
            print(proj.path)
        for group in self.group.subgroups.list(all=True): 
            grp = GitlabGroup(
                gitlab_url=self.gitlab_url,
                gitlab_key=self.gitlab_key,
                gitlab_group=group.full_path,
                path=self.path if self.flat else self.path / group.path,
                flat=self.flat,
                )
            self.subgroups.append(grp)
        
        exit()

    @property
    def count(self) -> int:
        """How many repositories are in the full group structure?"""
        count = 0
        for project in self.projects:
            count += 1
        for subgroup in self.subgroups:
            count += subgroup.count
        return count

    def recursive_command(self, command, **kwargs):
        """Recursively walk down group tree, finding projects and executing commands."""
        for project in self.projects:
            if hasattr(project, command):
                getattr(project, command)(**kwargs)
            else:
                raise Exception(f'Command "{command}" not recognised.')

        for subgroup in self.subgroups:
            subgroup.recursive_command(command)


class GitlabProject(BaseModel):
    """A Gitlab Project convenience class."""
    project: typing.Any
    path: pathlib.Path | None = None
    git: typing.Any | None = None

    def model_post_init(self, __context=None) -> None:
        """Post-init function calls."""
        if self.path is None:
            self.path = pathlib.Path() / self.project.path

    def build_local_repo(self):
        """Clone/check local repo."""
        if not self.path.is_dir():
            self.git = git.Repo.clone_from(
                self.project.ssh_url_to_repo, self.path
            )
        else:
            self.git = git.Repo(self.path)

    def clone(self):
        """"""
        self.build_local_repo()
        # return [
        #     pathlib.Path(self.git.working_tree_dir).name,
        #     "",
        #     self.git.git.rev_parse("--abbrev-ref", "HEAD"),
        #     self.git.remote(name="origin").url,
        # ]
