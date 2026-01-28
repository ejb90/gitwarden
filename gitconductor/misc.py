"""Miscellaneous."""

from importlib.resources import files
import pathlib
import pickle
import re

from gitconductor import gitlab


def load_cfg(cfg: pathlib.Path | None) -> gitlab.GitlabGroup | gitlab.GitlabProject:
    """Load Group/Project instance.

    Arguments:
        cfg (pathlib.Path, None):                   Path to cfg serialised pickle, or None.

    Returns:
        gitlab.GitlabGroup, gitlab.GitlabProject:   Returned instance.
    """
    if cfg is None:
        cfg = gitlab.GROUP_FNAME
        if not cfg.is_file():
            for parent in pathlib.Path().resolve().parents:
                cfg = parent / gitlab.GROUP_FNAME
                if cfg.is_file():
                    print(cfg)
                    break
            else:
                raise FileNotFoundError(f'No gitconductor configuration file "{gitlab.GROUP_FNAME}" found up to root.')
    elif isinstance(cfg, pathlib.Path):
        if not cfg.is_file():
            raise FileNotFoundError(f'The provided gitconductor configuration file "{cfg}" does not exist.')
    else:
        raise TypeError("Expected pathlib.Path or None for `cfg`.")

    with open(cfg, "rb") as fobj:
        group = pickle.load(fobj)
        group.rebuild(cfg)

    # Now down-select to the subgroup/project in the pwd
    grp = find_subgroup(group)
    return grp


def find_subgroup(group: gitlab.GitlabGroup | gitlab.GitlabProject) -> gitlab.GitlabGroup | gitlab.GitlabProject:
    """Find subgroup in pwd of Group structure.

    Arguments:
        group (gitlab.GitlabGroup):     Gitlab group instance.

    Returns:
        gitlab.GitlabGroup, None:       Gitlab group instance.

    """
    pwd = pathlib.Path().resolve()
    if group.path.resolve() == pwd:
        return group
    for project in group.projects:
        if project.path.resolve() == pwd:
            return project

    for grp in group.subgroups:
        if grp.path.resolve() == pwd:
            return grp
        return find_subgroup(grp)
    else:
        return group


def readme_header() -> str:
    """Read README.md for CLI help string.

    Returns:
        str:    README.md header contents.
    """
    chunks = readme()
    header = [line for line in chunks.get("gitconductor", {}).splitlines() if line.strip()]
    header = [line for line in header if not line.strip().startswith("[![")]
    header = "\n".join(header)
    return header


def readme() -> dict[str, str]:
    """Read README.md for CLI help string.

    Returns:
        str:    README.md contents.
    """
    help_str = (
        files("gitconductor")
        .joinpath("_data/README.md")
        .read_text(encoding="utf-8")
    )
    # readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    # with open(readme_path, "r", encoding="utf-8") as fobj:
        # help_str = fobj.read()

    chunks = re.split(r"(?<!#)#\s+", help_str)
    chunks = {chunk.splitlines()[0]: "\n".join(chunk.splitlines()[1:]) for chunk in chunks if chunk}
    return chunks
    
    