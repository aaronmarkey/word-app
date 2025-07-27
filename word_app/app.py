from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.screen import Screen
from textual.widgets import Footer

from word_app.ui.navigation.screens import SETTINGS


class WordApp(App):
    CSS_PATH = "app.css"
    BINDINGS = [SETTINGS.binding]
    SCREENS = {
        SETTINGS.id: SETTINGS.callable,
    }

    def compose(self) -> ComposeResult:
        yield Footer()

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SETTINGS.system_command
