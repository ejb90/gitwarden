"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import sys
from pathlib import Path

import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


# -- Load information --------------------------------------------------------
pyproject = Path().resolve().parent.parent / "pyproject.toml"
with pyproject.open("rb") as f:
    data = tomllib.load(f)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "gitwarden"
copyright = "2025, ejb90"
author = "ejb90"
release = data.get("project", {}).get("version", "0.0.0")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = []

nitpicky = True
napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
