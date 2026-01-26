"""Stub of core.Settings."""

import pathlib
import typing

import tomllib
from pydantic import BaseModel


class Settings(BaseModel):
    """Settings class."""

    cfg: pathlib.Path

    def model_post_init(self, context: typing.Any) -> None:  # noqa: ANN401
        """Post init hook to load cfg."""
        self.load()
        return super().model_post_init(context)

    def load(self) -> None:
        """Load cfg."""
        if self.cfg.is_file():
            with open(self.cfg, "rb") as fobj:
                raw_data = tomllib.load(fobj)
                for key, val in raw_data.items():
                    setattr(self, key, val)
