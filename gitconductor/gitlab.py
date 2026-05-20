"""GitLab-related constructs."""

from __future__ import annotations

import os
import pathlib
import pickle
import re
import shlex
import subprocess
import typing
import urllib.parse

import git
import gitlab
import rich
import rich.console
import tomllib
from pydantic import BaseModel, Field

from gitconductor import output, settings

GROUP_FNAME = pathlib.Path(".gitconductor.pkl")
SCP_URL_PATTERN = re.compile(r"^(?:(?P<user>[^@/:]+)@)?(?P<host>[^:/]+):(?P<path>.+)$")


def parse_gitlab_remote(remote: str) -> tuple[str, str]:
    """Parse a GitLab group or project URL into API URL and full path.

    Args:
        remote (str): HTTPS, HTTP, SSH, or scp-style GitLab URL.

    Returns:
        tuple[str, str]: GitLab API base URL and group or project full path.
    """
    parsed = urllib.parse.urlparse(remote)
    if parsed.scheme in {"http", "https"}:
        api_url = f"{parsed.scheme}://{parsed.netloc}"
        full_path = parsed.path
    elif parsed.scheme == "ssh":
        if not parsed.hostname:
            raise ValueError(f'Cannot determine GitLab host from "{remote}".')
        api_url = f"https://{parsed.hostname}"
        full_path = parsed.path
    else:
        match = SCP_URL_PATTERN.match(remote)
        if not match:
            raise ValueError(f'Clone target must be a full GitLab URL, got "{remote}".')
        api_url = f"https://{match.group('host')}"
        full_path = match.group("path")

    full_path = full_path.strip("/")
    if full_path.endswith(".git"):
        full_path = full_path.removesuffix(".git")

    if not full_path:
        raise ValueError(f'Cannot determine GitLab group or project path from "{remote}".')
    return api_url, full_path


def clone_target_path(remote: str, directory: pathlib.Path, flat: bool) -> pathlib.Path:
    """Determine the path a clone command will manage.

    Args:
        remote (str): HTTPS, HTTP, SSH, or scp-style GitLab URL.
        directory (pathlib.Path): Directory passed to ``gitconductor clone``.
        flat (bool): Whether clone output will use a flat layout.

    Returns:
        pathlib.Path: Path to check before cloning.
    """
    _, full_path = parse_gitlab_remote(remote)
    root = directory.resolve()
    if flat:
        return root / GROUP_FNAME
    return root / pathlib.PurePosixPath(full_path).parts[0]


class GitlabInstance(BaseModel):
    """A GitLab generic instance convenience class.

    Attributes:
        ...
    """

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
    """A GitLab group convenience class.

    Attributes:
        ...
    """

    name: str
    gitlab_key: str
    fullname: str = ""
    source: str | None = None
    group: typing.Any | None = None
    projects: list[str] = Field(default_factory=list)
    subgroups: list[str] = Field(default_factory=list)
    subgroup: bool = False
    cfg: settings.Settings | None = None

    def model_post_init(self, __context: str | None = None) -> None:
        """Post-init function calls."""
        kwargs = self.cfg.gitlab if self.cfg else {}
        if self.server is None:
            if not self.source:
                raise ValueError("A GitLab server or clone source URL is required.")
            api_url, self.fullname = parse_gitlab_remote(self.source)
            self.server = gitlab.Gitlab(api_url, private_token=self.gitlab_key, **kwargs)
        if not self.name:
            self.name = pathlib.PurePosixPath(self.fullname).name
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

    @property
    def visibility(self) -> str:
        """Project visibility.

        Returns:
            str:        Project visibility (private, internal, public).
        """
        return self.group.attributes["visibility"]

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
        # Loop through projects in the group, set up GitlabProject instance for the project.
        for project in sorted(self.group.projects.list(all=True), key=lambda x: x.path):
            proj = GitlabProject(
                gitlab_key=self.gitlab_key,
                server=self.server,
                project=project,
                root=self.root,
                flat=self.flat,
                cfg=self.cfg,
            )
            fullname = self.path.parent / f"{self.path.name}-{project.path}" if self.flat else self.path / project.path
            fullname = str(fullname.relative_to(self.root))
            proj.fullname = fullname
            self.projects.append(proj)

        # Loop through subgroups in the group, set up GitlabGroup instance for each subgroup.
        for group in self.group.subgroups.list(all=True):
            grp = GitlabGroup(
                gitlab_key=self.gitlab_key,
                server=self.server,
                fullname=group.full_path,
                name=pathlib.Path(group.full_path).name,
                root=self.root,
                flat=self.flat,
                subgroup=True,
                cfg=self.cfg,
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
            list:               List of returns from each command execution.
        """
        returns = []
        if not self.subgroup:
            output.PROGRESS_TOTAL.update(output.TASK_TOTAL, description=self.name, total=self.count)
        else:
            output.PROGRESS_TOTAL.update(output.TASK_TOTAL, description=self.name)
        for project in self.projects:
            project.rows = []
            if hasattr(project, command):
                returns.append(getattr(project, command)(**kwargs))
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
            returns.extend(subgroup.recursive_command(command, **kwargs))

        if not self.subgroup:
            output.LIVE.update(rich.console.Group(output.TABLE), refresh=True)
        self.dump()
        return returns

    def dump(self) -> None:
        """Dump to file."""
        with open(self.toplevel_dir / GROUP_FNAME, "wb") as fobj:
            pickle.dump(self, fobj)


class GitlabProject(GitlabInstance):
    """A GitLab project convenience class."""

    project: typing.Any
    gitlab_key: str
    name: str = ""
    git: typing.Any | None = None
    rows: list = Field(default_factory=list)
    _path: pathlib.Path = pathlib.Path()
    fullname: str = ""

    def model_post_init(self, __context: str | None = None) -> None:
        """Post-init function calls."""
        if self.server is None:
            raise ValueError("A GitLab server is required.")
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
    def visibility(self) -> str:
        """Project visibility.

        Returns:
            str:        Project visibility (private, internal, public).
        """
        return self.project.attributes["visibility"]

    @property
    def members(self) -> list:
        """Get members.

        Returns:
            int:        Number of members.
        """
        self.project = self.server.projects.get(self.project.id)
        return self.project.members_all.list(all=True)

    @property
    def is_python_package(self) -> bool:
        """Is this project a Python package?

        Returns:
            bool:       Is this project a Python package?
        """
        return (self.path / "setup.py").exists() or (self.path / "pyproject.toml").exists()

    @property
    def python_package_name(self) -> str:
        """What is the name of the Python package?

        Returns:
            str:        Name of the Python package.
        """
        if (self.path / "setup.py").exists():
            with open(self.path / "setup.py") as fobj:
                for line in fobj:
                    if line.strip().startswith("name="):
                        return line.strip().split("name=")[1].split(",")[0].strip().strip('"').strip("'")
        elif (self.path / "pyproject.toml").exists():
            with open(self.path / "pyproject.toml", "rb") as fobj:
                pyproject = tomllib.load(fobj)
                return pyproject.get("project", {}).get("name", "")
        else:
            raise Exception(f'Cannot determine Python package name for project "{self.name}".')

    def recursive_command(self, command: str, **kwargs: dict) -> None:
        """Trick to execute a command recursively on a project to keep code the same elsewhere.

        Arguments:
            command (str):      Command to execute.
            kwargs (*):         Keyword args to each recursive command.

        Returns:
            list:               List of returns from each command execution.
        """
        if hasattr(self, command):
            return getattr(self, command)(**kwargs)
        else:
            raise Exception(f'Command "{command}" not recognised.')

    def clone(self, resume: bool = False) -> None:
        """Clone a repository.

        Args:
            resume (bool): Reuse an existing matching repository when present.

        Returns:
            None
        """
        if resume and self.path.exists():
            self.git = self.validate_existing_clone()
        else:
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

    def validate_existing_clone(self) -> git.Repo:
        """Validate an existing clone can be reused.

        Returns:
            git.Repo: Existing repository.
        """
        try:
            repo = git.Repo(self.path)
        except git.InvalidGitRepositoryError as exc:
            message = f'Cannot resume clone because "{self.path}" exists but is not a git repository.'
            raise FileExistsError(message) from exc

        origin = repo.remote(name="origin").url
        expected_urls = {self.project.ssh_url_to_repo}
        http_url = getattr(self.project, "http_url_to_repo", None)
        if http_url:
            expected_urls.add(http_url)

        if origin not in expected_urls:
            expected = '" or "'.join(sorted(expected_urls))
            raise ValueError(
                f'Cannot resume clone at "{self.path}" because origin is "{origin}", expected "{expected}".'
            )
        return repo

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

    def add(self, fnames: tuple, all_: bool) -> None:
        """Add files to staging area.

        Returns:
            None
        """
        if all_:
            untracked = [self.path / fname for fname in self.git.untracked_files]
            modified = [self.path / d.a_path for d in self.git.index.diff(None)]
            fnames = untracked + modified

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
        self.rows.append(
            [self.name, self.git.git.rev_parse("--abbrev-ref", "HEAD"), self.git.remote(name="origin").url]
        )

    def pyinstall(self, pm: str = "uv pip", editable: bool = False, index: str | None = None) -> None:
        """Install Python package.

        Returns:
            None
        """
        if self.is_python_package:
            cmd = [*shlex.split(pm), "install"]
            if editable:
                cmd.append("--editable")
            if index:
                cmd.extend(["--index", index])
            cmd.append(str(self.path))

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode:
                raise Exception(f'Failed to install Python package at "{self.path}". Command: {" ".join(cmd)}')
            self.rows.append([self.python_package_name, str(self.path.relative_to(self.root))])

    def pyreqs(self) -> None:
        """Generate requirements.txt file for Python package.

        Returns:
            None
        """
        if self.is_python_package:
            self.rows.append(
                [
                    self.name,
                    str(self.path.relative_to(self.root)),
                    self.python_package_name,
                ]
            )
            return f"{self.python_package_name} @ {self.git.remotes.origin.url}@{self.git.head.commit.hexsha}"

        else:
            return ""

    def pywheel(self) -> None:
        """Generate wheel file for Python package.

        Returns:
            None
        """
        if self.is_python_package:
            cmd = [*shlex.split("uv build"), str(self.path), "--wheel", "--out-dir", str(self.path / "dist")]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode:
                print(result.stdout)
                print(result.stderr)
                raise Exception(f'Failed to build Python package at "{self.path}". Command: {" ".join(cmd)}')
            self.rows.append([self.python_package_name, str(self.path.relative_to(self.root))])
