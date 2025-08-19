from word_app.app.factory import create_app
from word_app.app.main import WordApp
from word_app.data.detail_providers.multisource_detail_provider import (
    MultisourceDetailProvider,
)
from word_app.data.search_providers.datamuse import DatamuseSearchProvider
from word_app.data.sources import get_available_data_sources
from word_app.data.transformers import WnToWaTransformer
from word_app.dev.fake import FakerProvider, fake  # type: ignore
from word_app.dev.fake_detail_provider import FakeDetailProvider  # type: ignore
from word_app.io import ApplicationPath
from word_app.lib.wordnik.client import WordnikApiClient
from word_app.lib.wordnik.conf import WordnikApiConf
from word_app.ui.theme import DarkTheme, LightTheme


def create_dummy_app() -> WordApp:
    return create_app(
        dark_theme=DarkTheme,
        data_sources=get_available_data_sources(),
        detail_provider=FakeDetailProvider(faker=fake),
        light_theme=LightTheme,
        path=ApplicationPath(),
        search_provider_cls=FakerProvider,
    )


def create_real_app() -> WordApp:
    return create_app(
        dark_theme=DarkTheme,
        data_sources=get_available_data_sources(),
        detail_provider=MultisourceDetailProvider(
            datamuse_client="",
            datamuse_transformer="",
            wordnik_client=WordnikApiClient(conf=WordnikApiConf(api_key="")),
            wordnik_transformer=WnToWaTransformer(),
        ),
        light_theme=LightTheme,
        path=ApplicationPath(),
        search_provider_cls=DatamuseSearchProvider,
    )


def run() -> None:
    app = create_real_app()
    app.run()
