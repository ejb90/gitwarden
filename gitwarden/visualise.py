"""Visualisation options."""

import pathlib

import rich.console
import rich.table
import rich.tree

from gitwarden.gitlab import GitlabGroup, GitlabProject

CODE_TO_ACCESS = {
    10: "Guest",
    20: "Reporter",
    30: "Developer",
    40: "Maintainer",
    50: "Owner",
}
CODE_TO_COLOUR = {
    10: "red",
    20: "bright_magenta",
    30: "orange1",
    40: "green",
    50: "blue",
}


def build_tree(group: GitlabGroup, tree: rich.tree.Tree) -> rich.tree.Tree:
    """Iteratively build the  tree.

    Args:
        group (gitlab.GitlabGroup):     Gitlab group instance.
        tree (rich.tree.Tree):          Initial Tree instance.

    Returns:
        rich.tree.Tree:                 Updated Tree instance.

    """
    for project in group.projects:
        branch = tree.add(project.name)
    for grp in group.subgroups:
        branch = tree.add(grp.shortname)
        build_tree(grp, branch)
    return tree


def build_table(
    group: GitlabGroup, rows: None | list[str] = None, depth: int = 0, maxdepth: int | None = None
) -> list[str]:
    """Iteratively build the table.

    Args:
        group (gitlab.GitlabGroup):     Gitlab group instance.
        rows (None, list):              Previous table rows.
        depth (int):                    Depth inside the tree.
        maxdepth (int):                 Maximum recursion depth (0=PWD).

    Returns:
        list:                           New row to print to table.
    """
    if rows is None:
        rows = []
    if maxdepth is None or depth <= maxdepth:
        for project in group.projects:
            rows.append(project.row)
        for grp in group.subgroups:
            rows.extend(build_table(grp, rows, depth=depth + 1, maxdepth=maxdepth))
    return rows


def build_access(
    group: GitlabGroup | GitlabProject,
    rows: None | list[str] = None,
    depth: int = 0,
    unique_ids: list[str] | None = None,
    explicit: bool = False,
    root: pathlib.Path = pathlib.Path(),
    maxdepth: int | None = None,
) -> list[str]:
    """Iteratively build access lists.

    Args:
        group (gitlab.GitlabGroup):     Gitlab group instance.
        rows (None, list):              Previous table rows.
        depth (int):                    Depth inside the tree.
        unique_ids (list):              List of all unique IDs printed
        explicit (bool):                Explicitly show all members of all groups/projects?
        root (pathlib.Path):            Top level directory.
        maxdepth (int):                 Maximum recursion depth (0=PWD).

    Returns:
        list:                           New row to print to table.
    """
    if rows is None:
        rows = []
    if unique_ids is None:
        unique_ids = []

    members = group.members
    if members:
        members = [member for member in members if member.id not in unique_ids or explicit]
        for i, member in enumerate(members):
            rows.append(
                [
                    str(group.path.relative_to(root.parent)) if not i else "",
                    member.name,
                    f"[{CODE_TO_COLOUR[member.access_level]}]{CODE_TO_ACCESS[member.access_level]}",
                    member.public_email,
                    member.expires_at,
                ]
            )
            unique_ids.append(member.id)

    if isinstance(group, GitlabGroup) and (maxdepth is None or depth < maxdepth):
        for project in group.projects:
            rows = build_access(
                project, rows, depth=depth + 1, unique_ids=unique_ids, explicit=explicit, maxdepth=maxdepth, root=root
            )
        for grp in group.subgroups:
            rows = build_access(
                grp, rows, depth=depth + 1, unique_ids=unique_ids, explicit=explicit, maxdepth=maxdepth, root=root
            )

    return rows


def tree(group: GitlabGroup) -> None:
    """Make a tree visualisation.

    Args:
        group (gitlab.GitlabGroup):     Gitlab group instance.

    Returns:
        None
    """
    tree = rich.tree.Tree(group.shortname)
    tree = build_tree(group, tree)
    console = rich.console.Console()
    console.print(tree, crop=True)


def table(group: GitlabGroup, maxdepth: int | None = None) -> None:
    """Make a table visualisation.

    Args:
        group (gitlab.GitlabGroup):     Gitlab group instance.
        maxdepth (int):                 Maximum recursion depth (0=PWD).

    Returns:
        None
    """
    rows = build_table(group, maxdepth=maxdepth)
    table = rich.table.Table()
    [table.add_column(c, "bold cyan") for c in ["Name", "Tree", "Branch", "Path", "Remote"]]
    for row in rows:
        table.add_row(*row)
    console = rich.console.Console()
    console.print(table, crop=True)


def access(group: GitlabGroup, explicit: bool = False, maxdepth: int | None = None) -> None:
    """Make a acess visualisation.

    Args:
        group (gitlab.GitlabGroup):     Gitlab group instance.
        explicit (bool):                Explicitly show all members of all groups/projects?
        maxdepth (int):                 Maximum recursion depth (0=PWD).

    Returns:
        None
    """
    rows = build_access(group, explicit=explicit, maxdepth=maxdepth, root=group.path)
    table = rich.table.Table()
    [table.add_column(c) for c in ["Group/Project", "User", "Access Level", "Public Email", "Expiry"]]
    for row in rows:
        table.add_row(*row)
    console = rich.console.Console()
    console.print(table, crop=True)
