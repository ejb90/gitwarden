"""Visualisation options."""

import rich.console
import rich.table
import rich.tree

from gitwarden.gitlab import GitlabGroup


def build_tree(group, tree):
    """Iteratively build the  tree.

    Args:
        group (gitlab.GitlabGroup):     Gitlab group instance.
        tree (rich.tree.Tree):          initial Tree instance.

    Returns:
        tree (rich.tree.Tree):          updated Tree instance.

    """
    for project in group.projects:
        branch = tree.add(project.name)
    for grp in group.subgroups:
        branch = tree.add(grp.shortname)
        build_tree(grp, branch)
    return tree


def build_table(group, rows=[], depth=0):
    """Iteratively build the table."""
    for project in group.projects:
        rows.append(project.row)
    for grp in group.subgroups:
        rows.extend(build_table(grp, rows, depth=depth+1))
    return rows


def tree(group: GitlabGroup):
    """Make a tree visualisation."""
    tree = rich.tree.Tree(group.shortname)
    tree = build_tree(group, tree)
    console = rich.console.Console()
    console.print(tree, crop=True)


def table(group: GitlabGroup):
    """Make a table visualisation."""
    rows = build_table(group)
    table = rich.table.Table()
    [table.add_column(c) for c in ["Name", "Tree", "Branch", "Path", "Remote"]]
    for row in rows:
        table.add_row(*row)
    console = rich.console.Console()
    console.print(table, crop=True)



