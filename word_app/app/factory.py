from textual.theme import Theme

from word_app.app.conf import (
    AppContext,
    ApplicationDependencies,
    ApplicationSettings,
)
from word_app.app.main import WordApp
from word_app.data.sources import DataSource, get_available_data_sources
from word_app.dev.fake import FakerProvider, FakeWordProvider
from word_app.io import ApplicationPath
from word_app.ui.theme import DarkTheme, LightTheme


def create_app(
    *,
    dark_theme: Theme | None = None,
    data_sources: list[DataSource] | None = None,
    light_theme: Theme | None = None,
    path: ApplicationPath | None = None,
) -> WordApp:
    path = path or ApplicationPath()

    settings = ApplicationSettings.from_sources(
        lambda: ApplicationSettings(_env_file=(path.usr / ".env")),  # type: ignore
        ApplicationSettings,
    )

    deps = ApplicationDependencies(
        search_providers=[FakerProvider],
        theme_dark=dark_theme or DarkTheme,
        theme_light=light_theme or LightTheme,
        word_provider=FakeWordProvider(),
    )

    ctx = AppContext(
        settings=settings,
        data_sources=data_sources or get_available_data_sources(),
        deps=deps,
        path=path,
    )

    return WordApp(ctx=ctx)
