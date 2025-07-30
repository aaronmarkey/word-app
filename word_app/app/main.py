from __future__ import annotations

import os

from dataclasses import dataclass
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.screen import Screen
from textual.widgets import Footer

from word_app.app.conf import AppConf
from word_app.data.sources import DataSource
from word_app.io import ApplicationPath
from word_app.ui.screens import SettingsScreen


@dataclass
class WordAppContext:
    conf: AppConf
    data_sources: list[DataSource]
    path: ApplicationPath


class WordApp(App):
    BINDINGS = [
        (SettingsScreen.WA_BINDING, "push_settings", SettingsScreen.WA_TITLE)
    ]
    CSS_PATH = "main.css"
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
            (
                lambda: self.push_screen(
                    self.assemble_settings_screen(),
                    wait_for_dismiss=False,
                )
            ),
            discover=True,
        )

    def compose(self) -> ComposeResult:
        yield Footer()

    # Dynamically Generated Methods.
    def action_push_settings(self) -> None:
        self.push_screen(
            self.assemble_settings_screen(), wait_for_dismiss=False
        )

    # My Functions
    def assemble_settings_screen(self) -> SettingsScreen:
        return SettingsScreen(
            app_conf=self.ctx.conf,
            data_sources=self.ctx.data_sources,
        )


def create_app(*, ctx: WordAppContext) -> WordApp:
    try:
        should_persist = bool(int(os.environ.get("WA_PERSIST_DATA", "0")))
    except Exception:
        should_persist = False

    app = WordApp(ctx=ctx, should_persist=should_persist)
    return app
