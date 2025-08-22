from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from textual.theme import Theme

import word_app.lib.darkdetect as darkdetect
from word_app.app.tui.screens.quick_search.suggestion_provider import (
    Provider,
)

if TYPE_CHECKING:
    from word_app.data.vo import DataSource as DataSourceInformation

from word_app.services.wdp.base import AbstractWordDetailProvider


class ThemeMode(StrEnum):
    AUTO = "-1"
    DARK = "0"
    LIGHT = "1"


class DataSource(BaseModel):
    """Base class for data source configurations."""

    enabled: bool = True


class DataMuse(DataSource):
    pass


class Wordnik(DataSource):
    api_key: str = ""


class DataSources(BaseModel):
    datamuse: DataMuse = DataMuse()
    wordnik: Wordnik = Wordnik()


class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__", env_prefix="WA_", extra="ignore"
    )

    data_sources: DataSources = DataSources()
    theme_mode: ThemeMode = ThemeMode.AUTO

    @classmethod
    def from_env_file(
        cls: type[ApplicationSettings], env_path: Path
    ) -> ApplicationSettings:
        """Initialize an ApplicationSettings object from an env var file."""
        return cls(
            _env_file=env_path,  # type: ignore
        )

    @classmethod
    def from_sources(
        cls: type[ApplicationSettings], *sources: Callable
    ) -> ApplicationSettings:
        source_values: list[ApplicationSettings] = [
            source() for source in sources
        ]
        main: dict[str, Any] = {}

        for sv in source_values:
            svd = sv.model_dump(
                mode="json",
                exclude_unset=True,
                exclude_defaults=True,
            )
            main |= svd
        return cls(**main)

    def update_ds_by_name(self, name: str, prop: str, value: Any) -> None:
        if ds := getattr(self.data_sources, name, None):
            setattr(ds, prop, value)
            return None
        raise ValueError(
            f"Cannot set property of unknown data source, '{name}'."
        )


@dataclass
class ApplicationDependencies:
    detail_provider: AbstractWordDetailProvider
    search_provider_cls: type[Provider]
    theme_dark: Theme
    theme_light: Theme

    @property
    def _theme_map(self) -> dict[ThemeMode, Theme]:
        return {
            ThemeMode.AUTO: self.theme_light
            if darkdetect.isLight()
            else self.theme_dark,
            ThemeMode.DARK: self.theme_dark,
            ThemeMode.LIGHT: self.theme_light,
        }

    @property
    def themes(self) -> tuple[Theme, ...]:
        return self.theme_dark, self.theme_light

    def theme_for_mode(self, mode: ThemeMode) -> Theme:
        return self._theme_map[mode]


class PathManager:
    @property
    def root(self) -> Path:
        return Path(__file__).parent.parent

    @property
    def usr(self) -> Path:
        return self.root / "../../usr"


@dataclass
class AppContext:
    data_sources: list[DataSourceInformation]
    deps: ApplicationDependencies
    path: PathManager
    settings: ApplicationSettings
