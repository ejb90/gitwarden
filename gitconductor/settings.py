"""Stub of core.Settings."""

import pathlib
import tomllib

from pydantic import BaseModel, Field


class Settings(BaseModel):
    cfg: pathlib.Path

    def model_post_init(self, context):
        return super().model_post_init(context)
        self.load()
    
    def load(self) -> None:
        """Load cfg."""
        if self._cfg.is_file():
            with open(self._cfg, "rb") as fobj: 
                raw_data = tomllib.load(fobj)
                for key, val in raw_data.items():
                    setattr(self, key, val)
            