from functools import partial

from word_app.app.factory import create_app
from word_app.app.main import WordApp
from word_app.data.search_providers.datamuse import DatamuseSearchProvider
from word_app.data.sources import get_available_data_sources
from word_app.dev.fake import FakeWordProvider, FakerProvider  # type: ignore
from word_app.io import ApplicationPath
from word_app.ui.theme import DarkTheme, LightTheme


def create_dummy_app() -> WordApp:
    return create_app(
        dark_theme=DarkTheme,
        data_sources=get_available_data_sources(),
        light_theme=LightTheme,
        path=ApplicationPath(),
        search_provider_cls=FakerProvider,
        word_provider=FakeWordProvider(),
    )


def create_real_app() -> WordApp:
    return create_app(
        dark_theme=DarkTheme,
        data_sources=get_available_data_sources(),
        light_theme=LightTheme,
        path=ApplicationPath(),
        search_provider_cls=DatamuseSearchProvider,
        word_provider=FakeWordProvider(),
    )


def run() -> None:
    app = create_real_app()
    app.run()
