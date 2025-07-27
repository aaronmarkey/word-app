from dataclasses import dataclass
from typing import Callable

from textual.app import SystemCommand
from textual.screen import Screen

from word_app.data.sources import DATA_SOURCES
from word_app.ui.navigation.core import Navigateable
from word_app.ui.screens.settings import SettingsScreen


@dataclass
class NavigateableScreen(Navigateable):
    callable: Callable[[], Screen]
    discoverable: bool = False

    @property
    def callable_str(self) -> str:
        return f"push_screen('{self.id}')"

    @property
    def system_command(self) -> SystemCommand:
        return SystemCommand(
            self.name,
            self.description,
            self.callable,
            discover=self.discoverable,
        )


SETTINGS = NavigateableScreen(
    action="",
    callable=(lambda: SettingsScreen(data_sources=DATA_SOURCES)),
    id="settings",
    name="Settings",
    description="Configure the application.",
    kb_binding="s",
    discoverable=True,
)
