"""Dummy for tests."""

from setuptools import find_packages, setup

setup(
    name="gitconductor",
    version="0.3.1",
    description="Manage nested git repositories in Gitlab seemlessly(ish)",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(where="."),
    install_requires=[
        "click",
        "gitpython",
        "pydantic",
        "python-gitlab",
        "rich",
        "rich-click",
    ],
)
