import os
from collections.abc import Mapping

from textual.theme import Theme

from word_app.app.conf import UsrConf, AppContext, CommandLineConf, SessionConf
from word_app.app.main import WordApp
from word_app.data.sources import DataSource, get_available_data_sources
from word_app.io import ApplicationPath
from word_app.ui.theme import DarkTheme, LightTheme


def create_app(
    *,
    cmd_env: Mapping | None = None,
    dark_theme: Theme | None = None,
    data_sources: list[DataSource] | None = None,
    light_theme: Theme | None = None,
    path: ApplicationPath | None = None,
) -> WordApp:
    path = path or ApplicationPath()

    ctx = AppContext(
        conf_cmd=CommandLineConf(cmd_env or os.environ),
        conf_session=SessionConf(),
        conf_usr=UsrConf.from_env(path.usr),
        data_sources=data_sources or get_available_data_sources(),
        path=path,
        theme_dark=dark_theme or DarkTheme,
        theme_light=light_theme or LightTheme,
    )

    return WordApp(ctx=ctx)
