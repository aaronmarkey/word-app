from __future__ import annotations

import os

from dataclasses import dataclass
from typing import Iterable

from textual.app import App, SystemCommand
from textual.screen import Screen
from textual.theme import BUILTIN_THEMES, Theme

import word_app.lib.darkdetect as darkdetect
from word_app.app.conf import AppConf
from word_app.data.sources import DataSource
from word_app.io import ApplicationPath
from word_app.ui.screens.home import HomeScreen
from word_app.ui.screens.settings import SettingsScreen
from word_app.ui.theme import DarkTheme, LightTheme


class CMD_LINE_VARS:
    """Command line variables

    Each variable is a tuple of (name, default_value).
        tuple[str, str]
    """

    persist_data = ("WA_PERSIST_DATA", "0")
    theme = ("WA_THEME", "-1")


def get_theme(light: Theme, dark: Theme) -> Theme:
    cmd_thm = os.environ.get(CMD_LINE_VARS.theme[0], CMD_LINE_VARS.theme[1])

    if cmd_thm not in ("0", "1"):
        cmd_thm = CMD_LINE_VARS.theme[1]
    cmd_thm = int(cmd_thm)

    thm_map = {
        int(CMD_LINE_VARS.theme[1]): light if darkdetect.isLight() else dark,
        0: dark,
        1: light,
    }
    return thm_map[cmd_thm]


@dataclass
class WordAppContext:
    conf: AppConf
    data_sources: list[DataSource]
    path: ApplicationPath


class WordApp(App):
    CSS_PATH = "main.css"
    SCREENS = {"home": HomeScreen}
    TOOLTIP_DELAY = 0.2

    def __init__(self, *args, **kwargs) -> None:
        try:
            ctx = kwargs.pop("ctx")
        except KeyError:
            raise SystemError("Application context was not provided.")

        should_persist = kwargs.pop("should_persist", False)
        super().__init__(*args, **kwargs)
        self.ctx = ctx
        self.should_persist = should_persist

    # Base Class Methods.
    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand(
            SettingsScreen.WA_TITLE,
            SettingsScreen.WA_DESCRIPTION,
            lambda: self.push_screen(SettingsScreen(), wait_for_dismiss=False),
            discover=True,
        )

    def on_mount(self) -> None:
        self.register_theme(DarkTheme)
        self.register_theme(LightTheme)
        for theme in BUILTIN_THEMES:
            self.unregister_theme(theme)

        self.theme = get_theme(LightTheme, DarkTheme).name
        self.push_screen("home")


def create_app(*, ctx: WordAppContext) -> WordApp:
    try:
        should_persist = bool(
            int(
                os.environ.get(
                    CMD_LINE_VARS.persist_data[0], CMD_LINE_VARS.persist_data[1]
                )
            )
        )
    except Exception:
        should_persist = False

    app = WordApp(ctx=ctx, should_persist=should_persist)
    return app
