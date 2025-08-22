from word_app.app.base import ApplicationSettings, PathManager
from word_app.app.tui.factory import create_app
from word_app.app.tui.main import WordApp
from word_app.app.tui.theme import DarkTheme, LightTheme
from word_app.data.vo import get_available_data_sources
from word_app.dev.fake import FakerProvider, fake  # type: ignore
from word_app.dev.fake_detail_provider import FakeDetailProvider  # type: ignore
from word_app.infra.datamuse.suggestion_provider import (
    DatamuseSearchProvider,
)
from word_app.infra.factories import http_client_factory
from word_app.infra.worknik.transformers import WnToWaTransformer
from word_app.infra.worknik.wdp import MultisourceDetailProvider
from word_app.lib.datamuse.client import DEFAULT_API_CONF as DMC
from word_app.lib.datamuse.client import DatamuseApiClient
from word_app.lib.wordnik.client import DEFAULT_API_CONF, WordnikApiClient


def create_dummy_app() -> WordApp:
    path = PathManager()
    settings = ApplicationSettings.from_sources(
        lambda: ApplicationSettings(_env_file=(path.usr / ".env")),  # type: ignore
        ApplicationSettings,
    )
    return create_app(
        dark_theme=DarkTheme,
        data_sources=get_available_data_sources(),
        detail_provider=FakeDetailProvider(faker=fake),
        light_theme=LightTheme,
        path=path,
        search_provider_cls=FakerProvider,
        settings=settings,
    )


def create_real_app() -> WordApp:
    path = PathManager()
    settings = ApplicationSettings.from_sources(
        lambda: ApplicationSettings(_env_file=(path.usr / ".env")),  # type: ignore
        ApplicationSettings,
    )
    return create_app(
        dark_theme=DarkTheme,
        data_sources=get_available_data_sources(),
        detail_provider=MultisourceDetailProvider(
            datamuse_client=DatamuseApiClient(
                client=http_client_factory(), conf=DMC
            ),
            datamuse_transformer=WnToWaTransformer(),
            wordnik_client=WordnikApiClient(
                client=http_client_factory(),
                conf=DEFAULT_API_CONF(
                    api_key=settings.data_sources.wordnik.api_key,
                ),
            ),
            wordnik_transformer=WnToWaTransformer(),
        ),
        light_theme=LightTheme,
        path=path,
        search_provider_cls=DatamuseSearchProvider,
        settings=settings,
    )


def run(app: WordApp) -> None:
    app.run()
