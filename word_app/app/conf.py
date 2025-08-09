"""Manages everything related to the application configuration."""

from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from textual.theme import Theme

if TYPE_CHECKING:
    from word_app.data.sources import DataSource

import word_app.lib.darkdetect as darkdetect
from word_app.io import ApplicationPath


class AppThemeMode(StrEnum):
    AUTO = "-1"
    DARK = "0"
    LIGHT = "1"


class DataSourceConf(BaseModel):
    """Base class for data source configurations."""

    enabled: bool


class DataMuseConf(DataSourceConf):
    pass


class WordnikConf(DataSourceConf):
    api_key: str


class DataSourceConfContainer(BaseModel):
    datamuse: DataMuseConf
    wordnik: WordnikConf


class CommandLineConf:
    CmdArg = namedtuple("CmdArg", ["name", "default"])
    CmdValue = namedtuple("CmdValue", ["value", "was_set"])

    _should_persist = CmdArg("WA_SHOULD_PERSIST", "0")
    _theme_mode = CmdArg("WA_THEME_MODE", "-1")

    def __init__(self, environ) -> None:
        self.environ = environ

    @property
    def should_persist(self) -> CmdValue:
        try:
            return self.CmdValue(self.environ[self._should_persist.name], True)
        except KeyError:
            return self.CmdValue(self._should_persist.default, False)

    @property
    def theme_mode(self) -> CmdValue:
        was_set: bool
        value: str
        try:
            value = self.environ[self._theme_mode.name]
            was_set = True
        except KeyError:
            value = self._theme_mode.default
            was_set = False

        mode: AppThemeMode
        try:
            mode = AppThemeMode(value)
        except Exception:
            mode = AppThemeMode.AUTO

        return self.CmdValue(mode, was_set)


class SessionConf(BaseModel):
    theme_mode: AppThemeMode | None = None


class UsrConf(BaseSettings):  # TODO: Rename to UsrConf or something.
    model_config = SettingsConfigDict(
        env_nested_delimiter="__", env_prefix="WA_"
    )

    ds: DataSourceConfContainer
    should_persist: bool
    theme_mode: AppThemeMode

    @classmethod
    def from_env(cls: type[UsrConf], env_path: Path) -> UsrConf:
        """Get the application configuration."""
        full_path = env_path / ".env"

        # Once again, mypy is a fucking failure of a library.
        # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#dotenv-env-support
        # _env_file _is_ an expected keyword argument, mypy is just dogshit.
        return cls(_env_file=full_path)  # type: ignore

    def conf_for_data_source(self, ds: DataSource) -> DataSourceConf:
        return getattr(self, f"ds_{ds.id.lower()}")

    def update_ds_by_name(self, name: str, prop: str, value: Any) -> None:
        ds = getattr(self.ds, name)
        setattr(ds, prop, value)


@dataclass
class AppContext:
    conf_cmd: CommandLineConf
    conf_session: SessionConf
    conf_usr: UsrConf
    data_sources: list[DataSource]
    path: ApplicationPath
    theme_dark: Theme
    theme_light: Theme

    @property
    def _theme_map(self) -> dict[AppThemeMode, Theme]:
        return {
            AppThemeMode.AUTO: self.theme_light
            if darkdetect.isLight()
            else self.theme_dark,
            AppThemeMode.DARK: self.theme_dark,
            AppThemeMode.LIGHT: self.theme_light,
        }

    @property
    def theme(self) -> Theme:
        return self._theme_map[self.theme_mode]

    @property
    def themes(self) -> tuple[Theme, ...]:
        return self.theme_dark, self.theme_light

    @property
    def theme_mode(self) -> AppThemeMode:
        cmd_value, cmd_was_set = self.conf_cmd.theme_mode
        session_value = self.conf_session.theme_mode
        usr_value = self.conf_usr.theme_mode

        if session_value is not None:
            return session_value
        if cmd_was_set:
            return cmd_value
        return usr_value
