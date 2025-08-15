from textual.theme import Theme

from word_app.app.conf import (
    AppContext,
    ApplicationDependencies,
    ApplicationSettings,
)
from word_app.app.main import WordApp
from word_app.data.sources import DataSource
from word_app.data.word_providers.base import AbstractWordProvider
from word_app.io import ApplicationPath
from word_app.ui.screens.quick_search._providers import Provider


def create_app(
    *,
    dark_theme: Theme,
    data_sources: list[DataSource],
    light_theme: Theme,
    path: ApplicationPath,
    search_provider_cls: type[Provider],
    word_provider: AbstractWordProvider,
) -> WordApp:
    settings = ApplicationSettings.from_sources(
        lambda: ApplicationSettings(_env_file=(path.usr / ".env")),  # type: ignore
        ApplicationSettings,
    )

    deps = ApplicationDependencies(
        search_provider_cls=search_provider_cls,
        theme_dark=dark_theme,
        theme_light=light_theme,
        word_provider=word_provider,
    )

    ctx = AppContext(
        settings=settings,
        data_sources=data_sources,
        deps=deps,
        path=path,
    )

    return WordApp(ctx=ctx)
