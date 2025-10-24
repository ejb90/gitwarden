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
git 
"""
import os
import pathlib

import click
import git
import gitlab


class GitlabGroup:
    """A Gitlab Group convenience class."""
    def __init__(self, gitlab_group):
        self.gitlab_group = gitlab_group
        self.projects = []
        self.subgroups = []

        self.build_projects()

    def build_projects(self) -> None:
        """Build each project object."""
        for project in self.gitlab_group.projects.list(all=True):
            self.projects.append(GitlabProject(project))
        for group in self.gitlab_group.subgroups.list(all=True):
            self.subgroups.append(GitlabGroup(project))

    # def recursive_command(self, command):
    #     """Recursively walk down group tree, finding projects and executing commands."""
    #     for project in self.projects:
    #         if hasattr(project, command):
    #             project.getattr(command)()
        
    #     for subgroup in self.subgroups:
    #         subgroup.recursive_command()
    
    def clone(self, directory: pathlib.Path) -> None:
        """"""
        for entry in (self.projects + self.subgroups):
            entry.clone(directory)



class GitlabProject:
    """A Gitlab Project convenience class."""
    def __init__(self, gitlab_project):
        self.gitlab_project = gitlab_project
        self.path = pathlib.Path() / self.gitlab_project.path
        self.git = None
    
    def build_local_repo(self):
        """Clone/check local repo."""
        if not self.path.is_dir():
            self.git = git.Repo.clone_from(self.gitlab_project.ssh_url_to_repo, self.gitlab_project.path)
        else:
            self.git = git.Repo(self.path)
    
    def clone(self, directory):
        """"""
        self.path = directory
        self.build_local_repo()

    def branch(self):
        """"""

    

def get_gitlab_group(
        group: str, 
        url: str="https://gitlab.com", 
        key: str=os.environ.get("GITLAB_PRIVATE_KEY")
    ) -> GitlabGroup:
    """Get GitlabGroup object.
    
    Arguments:
        ...

    Returns:
        ...
    """
    gtlb = gitlab.Gitlab(
        url,
        private_token=key
    )
    group = gtlb.groups.get(group)

    # # Now store metadata like git
    # config_dir = pathlib.Path(".gitwarden")
    # if not config_dir.is_dir():
        
    return GitlabGroup(group)


@click.group()
def main():
    """Dummy for click"""
    pass


@main.command()
@click.argument("group")
@click.argument(
    "directory", 
    type=pathlib.Path,
    default=pathlib.Path(),
)
def clone(group: str, directory: click.Path) -> None:
    """Clone repos recursively.
    
    Arguments:
        ...
    
    Returns:
        ...
    """
    group = get_gitlab_group(group)
    group.clone(pathlib.Path(directory))


@main.command()
def branch():
    """Branch repos recursively."""
