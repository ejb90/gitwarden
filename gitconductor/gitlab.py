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

from gitconductor import output, settings

GROUP_FNAME = pathlib.Path(".gitconductor.pkl")


class GitlabInstance(BaseModel):
    """A Gitlab generic instance convenience class.

    Attributes:
        ...
    """

    gitlab_url: str = "https://gitlab.com"
    gitlab_key: str
    server: typing.Any | None = None
    root: pathlib.Path = pathlib.Path().resolve()
    flat: bool = False
    cfg: settings.Settings | None = None

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


class GitlabGroup(GitlabInstance):
    """A Gitlab Group convenience class.

    Attributes:
        ...
    """
       
    name: str
    gitlab_key: str
    gitlab_url: str = "https://gitlab.com"
    fullname: str = ""
    group: typing.Any | None = None
    projects: list[str] = Field(default_factory=list)
    subgroups: list[str] = Field(default_factory=list)
    subgroup: bool = False

    def model_post_init(self, __context: str | None = None) -> None:
        """Post-init function calls."""
        self.server = gitlab.Gitlab(self.gitlab_url, private_token=self.gitlab_key)
        self.root = self.root.resolve()
        self.group = self.server.groups.get(self.fullname)
        self.build()

    @property
    def path(self) -> pathlib.Path:
        """Auto-generated path.

        Returns:
            pathlib.Path:       Project path.
        """
        return self.root / self.fullname.replace(os.sep, "-") if self.flat else self.root / self.fullname

    # @path.setter
    # def path(self, new_value):
    #     self._path = pathlib.Path(new_value)

    @property
    def members(self) -> list:
        """Get members.

        Returns:
            int:        Number of members.
        """
        self.group = self.server.groups.get(self.group.id)
        return self.group.members_all.list(all=True)

    def build(self) -> None:
        """Build each project object.

        Returns:
            None
        """
        # Loop through projects in the group, set up GitlabProject instance for the project
        for project in sorted(self.group.projects.list(all=True), key=lambda x: x.path):
            proj = GitlabProject(gitlab_url=self.gitlab_url, gitlab_key=self.gitlab_key, project=project, root=self.root, flat=self.flat)
            fullname = self.path.parent / f"{self.path.name}-{project.path}" if self.flat else self.path / project.path
            fullname = str(fullname.relative_to(self.root))
            proj.fullname = fullname
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

    def rebuild(self, cfg: pathlib.Path) -> None:
        """Rebuild the objects when reloaded (new directories, etc.).

        Arguments:
            cfg (pathlib.Path):         Serialised .pkl file.

        Returns:
            None
        """
        self.root = cfg.resolve().parent.parent
        for project in self.projects:
            project.root = self.root
            project.git = git.Repo(project.path)

        for group in self.subgroups:
            group.root = self.root
            group.rebuild(cfg)

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
        """Recursively walk down group tree, finding projects and executing commands.

        Arguments:
            command (str):      Command to execute.
            kwargs (*):         Keyword args to each recursive command.

        Returns:
            None
        """
        if not self.subgroup:
            output.PROGRESS_TOTAL.update(output.TASK_TOTAL, description=self.name, total=self.count)
        else:
            output.PROGRESS_TOTAL.update(output.TASK_TOTAL, description=self.name)
        for project in self.projects:
            project.rows = []
            if hasattr(project, command):
                getattr(project, command)(**kwargs)
                for row in project.rows:
                    output.TABLE.add_row(*row)
                output.PROGRESS_TOTAL.update(output.TASK_TOTAL, description=project.name)
                output.PROGRESS_TOTAL.advance(output.TASK_TOTAL)
                if command == "clone":
                    output.LIVE.update(
                        rich.console.Group(output.TABLE, output.PROGRESS_PROJECT, output.PROGRESS_TOTAL),
                        refresh=True,
                    )
                else:
                    output.LIVE.update(
                        rich.console.Group(output.TABLE),
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
    gitlab_key: str
    gitlab_url: str = "https://gitlab.com"
    name: str = ""
    git: typing.Any | None = None
    rows: list = Field(default_factory=list)
    _path: pathlib.Path = pathlib.Path()
    fullname: str = ""

    def model_post_init(self, __context: str | None = None) -> None:
        """Post-init function calls."""
        self.server = gitlab.Gitlab(self.gitlab_url, private_token=self.gitlab_key)
        if self.path is None:
            self.path = pathlib.Path() / self.project.path

    @property
    def path(self) -> pathlib.Path:
        """Auto-generated path.

        Returns:
            pathlib.Path:       Project path.
        """
        return self.root / self.fullname

    @property
    def members(self) -> list:
        """Get members.

        Returns:
            int:        Number of members.
        """
        self.project = self.server.projects.get(self.project.id)
        return self.project.members_all.list(all=True)

    def clone(self) -> None:
        """Clone a repository.

        Returns:
            None
        """
        self.git = git.Repo.clone_from(self.project.ssh_url_to_repo, self.path, progress=output.CloneProgress())
        self.name = pathlib.Path(self.git.working_tree_dir).name

        self.rows.append(
            [
                self.name,
                # str(self.path.relative_to(self.root)),
                str(self.fullname),
                self.git.git.rev_parse("--abbrev-ref", "HEAD"),
                str(self.path.relative_to(self.root)),
                self.git.remote(name="origin").url,
            ]
        )

    def branch(self, name: str | None = None) -> None:
        """Make branch in a repository.

        Returns:
            None
        """
        if not self.path:
            raise Exception(f'Cannot find repository @ "{self.path}"')
        self.git = git.Repo(self.path)

        self.rows.append(
            [
                self.name,
                str(self.path.relative_to(self.root)),
                self.git.git.rev_parse("--abbrev-ref", "HEAD"),
                name,
            ]
        )
        self.git.create_head(name)

    def checkout(self, name: str | None = None) -> None:
        """Checkout a branch in a repository.

        Returns:
            None
        """
        if not self.path:
            raise Exception(f'Cannot find repository @ "{self.path}"')
        self.git = git.Repo(self.path)

        self.rows.append(
            [
                self.name,
                str(self.path.relative_to(self.root)),
                self.git.git.rev_parse("--abbrev-ref", "HEAD"),
                name,
            ]
        )
        self.git.heads[name].checkout()

    def add(self, fnames: tuple) -> None:
        """Add files to staging area.

        Returns:
            None
        """
        for fname in fnames:
            fname = pathlib.Path(fname).resolve()
            if fname.is_relative_to(self.path):
                rel_path = str(fname.relative_to(self.path))
                if rel_path in self.git.untracked_files or rel_path in [d.a_path for d in self.git.index.diff(None)]:
                    self.git.index.add(
                        [
                            fname.relative_to(self.path),
                        ]
                    )

                    self.rows.append(
                        [
                            self.name,
                            self.git.git.rev_parse("--abbrev-ref", "HEAD"),
                            str(fname),
                        ]
                    )

    def commit(self, message: str) -> None:
        """Add files to staging area.

        Returns:
            None
        """
        staged = self.git.index.diff("HEAD")
        fnames = [d.a_path for d in staged]
        if fnames:
            self.git.index.commit(message)

            for fname in fnames:
                self.rows.append(
                    [
                        self.name,
                        self.git.git.rev_parse("--abbrev-ref", "HEAD"),
                        str(fname),
                        message,
                    ]
                )

    def status(self) -> None:
        """Return git status.

        Returns:
            None
        """
        untracked = self.git.untracked_files
        modified = [d.a_path for d in self.git.index.diff(None)]
        added = [d.a_path for d in self.git.index.diff("HEAD")]

        for fname in sorted(added):
            entry = [self.fullname, fname, "Changes to be committed"]
            entry = [f"[green]{string}[/]" for string in entry]
            self.rows.append(entry)
        for fname in sorted(modified):
            entry = [self.fullname, fname, "Changes not staged for commit"]
            entry = [f"[red]{string}[/]" for string in entry]
            self.rows.append(entry)
        for fname in sorted(untracked):
            entry = [self.fullname, fname, "Untracked files"]
            entry = [f"[magenta]{string}[/]" for string in entry]
            self.rows.append(entry)

    def push(self) -> None:
        """Push recursively.

        Returns:
            None
        """
        self.git.remotes.origin.push()
