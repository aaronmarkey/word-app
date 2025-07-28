from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.screen import Screen
from textual.widgets import Footer

from word_app.app_conf import AppConf
from word_app.data.sources import DataSource
from word_app.io import ApplicationPath
from word_app.ui.screens.settings import SettingsScreen


@dataclass
class WordAppContext:
    conf: AppConf
    data_sources: list[DataSource]
    path: ApplicationPath


class WordApp(App):
    CSS_PATH = "app.css"
    BINDINGS = [
        (SettingsScreen.WA_BINDING, "push_settings", SettingsScreen.WA_TITLE)
    ]

    def __init__(self, ctx: WordAppContext, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ctx = ctx

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand(
            SettingsScreen.WA_TITLE,
            SettingsScreen.WA_DESCRIPTION,
            (
                lambda: self.push_screen(
                    SettingsScreen(
                        app_conf=self.ctx.conf,
                        data_sources=self.ctx.data_sources,
                    ),
                    wait_for_dismiss=False,
                )
            ),
            discover=True,
        )

    def compose(self) -> ComposeResult:
        yield Footer()

    def action_push_settings(self) -> None:
        screen = SettingsScreen(
            app_conf=self.ctx.conf,
            data_sources=self.ctx.data_sources,
        )
        self.push_screen(screen, wait_for_dismiss=False)


def create_app(ctx: WordAppContext) -> WordApp:
    app = WordApp(ctx)
    return app
