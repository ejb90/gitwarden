"""Python-specific CLI arguments.

1. py-installer: Install python packages in the cloned repository tree.
2. py-requirements: Generate requirements.txt files for python packages in the cloned repository tree.
3. py-wheeler: Build wheels for python packages in the cloned repository tree.
"""

import logging
import pathlib

import click

from gitconductor import misc, output

from .cli import cli


@cli.command()
@click.pass_context
@click.option("-f", "--fname", type=pathlib.Path, default=None)
@click.option("-p", "--pyproject", is_flag=True, default=False)
@click.option("-F", "--force", is_flag=True, default=False)
def py_requirements(ctx: click.Context, fname: pathlib.Path | None, pyproject: bool, force: bool) -> None:
    """Generate requirements.txt file for python packages in the cloned repository tree.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        fname (pathlib.Path | None):        Path to the requirements.txt file. (default: requirements.txt)
        pyproject (bool):                   Generate pyproject.toml file instead of requirements.txt.
        force (bool):                       Force overwrite of existing file.

    Returns:
        None
    """
    group = misc.load_cfg(ctx.obj["state"])
    [output.TABLE.add_column(c) for c in ["Name", " Path", "Package Name"]]
    reqs = group.recursive_command("pyreqs")

    if fname is None:
        fname = pathlib.Path("pyproject.toml") if pyproject else pathlib.Path("requirements.txt")

    if fname.is_file() and not force:
        logging.warning(f"File already exists: {fname}. Use --force to overwrite.")
        write = False
    elif fname.is_file() and force:
        logging.warning(f"Overwriting existing file: {fname}")
        write = True
    elif not fname.is_file() or force:
        write = True
    else:
        raise NotImplementedError("This should never happen.")

    if write:
        with open(fname, "w") as fobj:
            # pyproject style
            if pyproject:
                fobj.write("dependencies = [\n")
                for req in reqs:
                    fobj.write(f'    "{req}",\n')
                fobj.write("]\n")
            # requirements.txt style
            else:
                for req in reqs:
                    fobj.write(req + "\n")


@cli.command()
@click.pass_context
@click.option("--package-manager", type=str, default="uv pip")
@click.option("-e", "--editable", type=bool, is_flag=True, default=False)
@click.option("--index", type=str, default=None)
def py_installer(ctx: click.Context, editable: bool, index: str | None, package_manager: str = "uv pip") -> None:
    """Install python packages in the cloned repository tree.

    Arguments:
        ctx (click.Context):                Top level CLI flags.
        editable (bool):                    Install in editable mode?
        index (str | None):                 Index URL to use for installation.
        package_manager (str):              Package manager to use for installation (default: "uv pip").

    Returns:
        None
    """
    group = misc.load_cfg(ctx.obj["state"])

    [output.TABLE.add_column(c) for c in ["Name", "Path"]]
    group.recursive_command("pyinstall", pm=package_manager, editable=editable, index=index)


@cli.command()
@click.pass_context
def py_wheeler(ctx: click.Context) -> None:
    """Install python packages in the cloned repository tree.

    Arguments:
        ctx (click.Context):                Top level CLI flags.

    Returns:
        None
    """
    # group = misc.load_cfg(ctx.obj["state"])

    # [output.TABLE.add_column(c) for c in ["Name", "Path"]]
    # group.recursive_command("pyinstall", editable=editable, index=index)
    raise NotImplementedError("Wheel building is not implemented yet.")