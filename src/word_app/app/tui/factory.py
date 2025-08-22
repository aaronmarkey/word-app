from textual.theme import Theme

from word_app.app.base import (
    AppContext,
    ApplicationDependencies,
    ApplicationSettings,
    PathManager,
)
from word_app.app.tui.main import WordApp
from word_app.app.tui.screens.quick_search.suggestion_provider import (
    Provider,
)
from word_app.data.vo import DataSource
from word_app.services.wdp.base import AbstractWordDetailProvider


def create_app(
    *,
    dark_theme: Theme,
    data_sources: list[DataSource],
    detail_provider: AbstractWordDetailProvider,
    light_theme: Theme,
    path: PathManager,
    search_provider_cls: type[Provider],
    settings: ApplicationSettings,
) -> WordApp:
    deps = ApplicationDependencies(
        detail_provider=detail_provider,
        search_provider_cls=search_provider_cls,
        theme_dark=dark_theme,
        theme_light=light_theme,
    )

    ctx = AppContext(
        settings=settings,
        data_sources=data_sources,
        deps=deps,
        path=path,
    )

    return WordApp(ctx=ctx)
