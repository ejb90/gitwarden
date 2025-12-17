"""Visualisation options."""

import rich.console
import rich.table
import rich.tree

from gitwarden.gitlab import GitlabGroup


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


def build_table(group: GitlabGroup, rows: None | list[str] = None, depth: int = 0) -> list[str]:
    """Iteratively build the table.

    Args:
        group (gitlab.GitlabGroup):     Gitlab group instance.
        rows (None, list):              Previous table rows.
        depth (int):                    Depth inside the tree.

    Returns:
        list:                           New row to print to table.
    """
    if rows is None:
        rows = []
    for project in group.projects:
        rows.append(project.row)
    for grp in group.subgroups:
        rows.extend(build_table(grp, rows, depth=depth + 1))
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


def table(group: GitlabGroup) -> None:
    """Make a table visualisation.

    Args:
        group (gitlab.GitlabGroup):     Gitlab group instance.

    Returns:
        None
    """
    rows = build_table(group)
    table = rich.table.Table()
    [table.add_column(c) for c in ["Name", "Tree", "Branch", "Path", "Remote"]]
    for row in rows:
        table.add_row(*row)
    console = rich.console.Console()
    console.print(table, crop=True)
