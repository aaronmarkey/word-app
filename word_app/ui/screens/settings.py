from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from word_app.data.sources import DataSource
from word_app.ui.navigation.common import POP_SCREEN
from word_app.ui.widgets import SectionStatic, SwitchWithLabel


class SettingsScreen(Screen):

    BINDINGS = [POP_SCREEN.binding]

    def __init__(self, *, data_sources: list[DataSource]) -> None:
        super().__init__()
        self._data_sources = data_sources

        self.title = "⚙️ Settings"

    def compose(self) -> ComposeResult:
        yield Header(icon="")
        yield SectionStatic("Data Sources")
        for source in self._data_sources:
            yield SwitchWithLabel(
                label_text=source.label_name,
                label_tooltip=source.label_description,
                switch_value=False,
            )
        yield Footer()
