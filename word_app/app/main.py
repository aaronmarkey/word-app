from __future__ import annotations

from typing import Iterable

from textual.app import App, SystemCommand
from textual.screen import Screen
from textual.theme import BUILTIN_THEMES

from word_app.app.conf import AppContext
from word_app.ui.screens.home import HomeScreen
from word_app.ui.screens.settings import SettingsScreen


class WordApp(App):
    CSS_PATH = "main.css"
    SCREENS = {"home": HomeScreen}
    TOOLTIP_DELAY = 0.2

    def __init__(self, *args, **kwargs) -> None:
        try:
            ctx = kwargs.pop("ctx")
        except KeyError:
            raise SystemError("Application context was not provided.")

        self.ctx: AppContext = ctx
        super().__init__(*args, **kwargs)

    # Base Class Methods.
    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand(
            SettingsScreen.WA_TITLE,
            SettingsScreen.WA_DESCRIPTION,
            lambda: self.push_screen(SettingsScreen(), wait_for_dismiss=False),
            discover=True,
        )

    # Event handlers.
    def on_mount(self) -> None:
        for theme in self.ctx.themes:
            self.register_theme(theme)
        for theme in BUILTIN_THEMES:
            self.unregister_theme(theme)

        self.theme = self.ctx.theme.name
        self.push_screen("home")
