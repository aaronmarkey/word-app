"""Manages everything related to the application configuration."""

from __future__ import annotations

from pathlib import Path

from word_app.data.sources import DataSource

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataSourceConf(BaseModel):
    """Base class for data source configurations."""


class DataMuseConf(DataSourceConf):
    enabled: bool


class WordnikConf(DataSourceConf):
    enabled: bool
    api_key: str


class AppConf(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__", env_nested_max_split=1, env_prefix="WA__"
    )

    ds_datamuse: DataMuseConf
    ds_wordnik: WordnikConf

    @classmethod
    def from_env(cls: type[AppConf], env_path: Path) -> AppConf:
        """Get the application configuration."""
        full_path = env_path / ".env"
        return cls(_env_file=full_path)

    def conf_for_data_source(self, ds: DataSource) -> DataSourceConf:
        return getattr(self, f"ds_{ds.id.lower()}")
