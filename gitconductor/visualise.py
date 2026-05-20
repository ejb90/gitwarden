"""Visualisation options."""

import pathlib

import gitlab
import rich.box
import rich.console
import rich.table
import rich.tree

from gitconductor.gitlab import GitlabGroup, GitlabProject

CODE_TO_ACCESS = {
    0: "No Access",
    10: "Guest",
    20: "Reporter",
    30: "Developer",
    40: "Maintainer",
    50: "Owner",
}
CODE_TO_COLOUR = {
    0: "white",
    10: "red",
    20: "bright_magenta",
    30: "orange1",
    40: "green",
    50: "blue",
}
ACCESS_WARNING_LEVEL = "[yellow]Unavailable[/]"
ACCESS_WARNING_USER = "[yellow]Members hidden[/]"


def membership_warning(group: GitlabGroup | GitlabProject, error: Exception) -> list[str]:
    """Build a warning row for hidden membership.

    Args:
        group (GitlabGroup | GitlabProject): GitLab group or project.
        error (Exception): Error raised while listing members.

    Returns:
        list[str]: Warning row.
    """
    message = str(error).strip() or "your token cannot list members here"
    return [
        str(group.path),
        ACCESS_WARNING_USER,
        ACCESS_WARNING_LEVEL,
        "",
        message,
        group.visibility,
    ]


def visible_members(group: GitlabGroup | GitlabProject) -> tuple[list, list[str] | None]:
    """Safely list visible members.

    Args:
        group (GitlabGroup | GitlabProject): GitLab group or project.

    Returns:
        tuple[list, list[str] | None]: Members plus a warning row when access is hidden.
    """
    try:
        return group.members, None
    except (
        gitlab.exceptions.GitlabAuthenticationError,
        gitlab.exceptions.GitlabGetError,
        gitlab.exceptions.GitlabListError,
    ) as exc:
        return [], membership_warning(group, exc)


def build_tree(group: GitlabGroup, tree: rich.tree.Tree) -> rich.tree.Tree:
    """Iteratively build the  tree.

    Args:
        group (gitlab.GitlabGroup):     GitLab group instance.
        tree (rich.tree.Tree):          Initial Tree instance.

    Returns:
        rich.tree.Tree:                 Updated Tree instance.

    """
    for project in group.projects:
        branch = tree.add(project.name)
    for grp in group.subgroups:
        branch = tree.add(grp.name)
        build_tree(grp, branch)
    return tree


def build_table(
    group: GitlabGroup, rows: None | list[str] = None, depth: int = 0, maxdepth: int | None = None
) -> list[str]:
    """Iteratively build the table.

    Args:
        group (gitlab.GitlabGroup):     GitLab group instance.
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
            rows.extend(project.rows)
        for grp in group.subgroups:
            rows = build_table(grp, rows, depth=depth + 1, maxdepth=maxdepth)
    return rows


def build_access(
    group: GitlabGroup | GitlabProject,
    rows: None | list[str] = None,
    depth: int = 0,
    unique_ids: list[str] | None = None,
    explicit: bool = False,
    root: pathlib.Path = pathlib.Path(),
    maxdepth: int | None = None,
    colour_only: bool = False,
) -> list[str]:
    """Iteratively build access lists.

    Args:
        group (gitlab.GitlabGroup):     GitLab group instance.
        rows (None, list):              Previous table rows.
        depth (int):                    Depth inside the tree.
        unique_ids (list):              List of all unique IDs printed
        explicit (bool):                Explicitly show all members of all groups/projects?
        root (pathlib.Path):            Top level directory.
        maxdepth (int):                 Maximum recursion depth (0=PWD).
        colour_only (bool):             Only return the colour code for the access level.

    Returns:
        list:                           New row to print to table.
    """
    if rows is None:
        rows = []
    if unique_ids is None:
        unique_ids = []

    members, warning = visible_members(group)
    if warning:
        warning[0] = str(group.path.relative_to(root.parent))
        rows.append(warning)

    if members:
        members = [member for member in members if member.id not in unique_ids or explicit]
        for i, member in enumerate(members):
            rows.append(
                [
                    str(group.path.relative_to(root.parent)) if (not i or colour_only) else "",
                    member.name,
                    f"[{CODE_TO_COLOUR[member.access_level]}]{CODE_TO_ACCESS[member.access_level]}"
                    if not colour_only
                    else f"[{CODE_TO_COLOUR[member.access_level]}]",
                    member.public_email,
                    member.expires_at,
                    group.visibility,
                ]
            )
            unique_ids.append(member.id)

    if isinstance(group, GitlabGroup) and (maxdepth is None or depth < maxdepth):
        for project in group.projects:
            rows = build_access(
                project,
                rows,
                depth=depth + 1,
                unique_ids=unique_ids,
                explicit=explicit,
                maxdepth=maxdepth,
                root=root,
                colour_only=colour_only,
            )
        for grp in group.subgroups:
            rows = build_access(
                grp,
                rows,
                depth=depth + 1,
                unique_ids=unique_ids,
                explicit=explicit,
                maxdepth=maxdepth,
                root=root,
                colour_only=colour_only,
            )

    return rows


def tree(group: GitlabGroup) -> None:
    """Make a tree visualisation.

    Args:
        group (gitlab.GitlabGroup):     GitLab group instance.

    Returns:
        None
    """
    tree = rich.tree.Tree(group.name)
    tree = build_tree(group, tree)
    console = rich.console.Console()
    console.print(tree, crop=True)


def table(group: GitlabGroup, maxdepth: int | None = None) -> None:
    """Make a table visualisation.

    Args:
        group (gitlab.GitlabGroup):     GitLab group instance.
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
    """Make an access visualisation.

    Args:
        group (gitlab.GitlabGroup):     GitLab group instance.
        explicit (bool):                Explicitly show all members of all groups/projects?
        maxdepth (int):                 Maximum recursion depth (0=PWD).

    Returns:
        None
    """
    rows = build_access(group, explicit=explicit, maxdepth=maxdepth, root=group.path)
    table = rich.table.Table()
    [table.add_column(c) for c in ["Group/Project", "User", "Access Level", "Public Email", "Expiry"]]
    for row in rows:
        table.add_row(*row[:5])
    console = rich.console.Console()
    console.print(table, crop=True)


def access_matrix(group: GitlabGroup, maxdepth: int | None = None) -> None:
    """Make an access matrix visualisation.

    Args:
        group (gitlab.GitlabGroup):     GitLab group instance.
        maxdepth (int):                 Maximum recursion depth (0=PWD).

    Returns:
        None
    """
    rows = build_access(group, explicit=True, maxdepth=maxdepth, root=group.path, colour_only=True)
    warnings = [r for r in rows if r[1] == ACCESS_WARNING_USER]
    member_rows = [r for r in rows if r[1] != ACCESS_WARNING_USER]
    entries = {r[0] for r in member_rows if r[0]}
    users = {r[1] for r in member_rows if r[1]}

    # Main table
    table = rich.table.Table(show_lines=True, box=rich.box.SQUARE)
    table.add_column("Group/Project", style="bold")
    [table.add_column(c) for c in sorted(users)]

    for entry in sorted(entries):
        visibility = next(r for r in member_rows if r[0] == entry)[-1]
        row = [
            entry,
        ]
        for user in sorted(users):
            access = next((r[2] for r in member_rows if r[0] == entry and r[1] == user), None)
            if access is None:
                access = "[red]" if visibility == "public" else "[white]"
            block = f"[on {access[1:-1]}]{' ' * len(user)}"
            row.append(block)

        table.add_row(*row)

    console = rich.console.Console()
    console.print(table, crop=True)

    # Legend table
    table = rich.table.Table()
    table.add_column("Access Level", style="bold")
    for code, access in CODE_TO_ACCESS.items():
        block = f"[on {CODE_TO_COLOUR[code]}]{' ' * 10}"
        table.add_row(f"{access:<10} {block}")

    console.print(table, crop=True)

    if warnings:
        table = rich.table.Table()
        [table.add_column(c) for c in ["Group/Project", "Warning", "Detail"]]
        for warning in warnings:
            table.add_row(warning[0], warning[1], warning[4])
        console.print(table, crop=True)
