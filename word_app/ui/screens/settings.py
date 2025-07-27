from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.screen import Screen
from textual.widgets import Footer, Header

from word_app.data.sources import DataSource
from word_app.ui.containers import ContainerWithBorderLabel
from word_app.ui.navigation.common import POP_SCREEN
from word_app.ui.widgets import SwitchWithLabel
from word_app.ui.widgets.switch_with_label import SwitchWithInput


class SettingsScreen(Screen):
    BINDINGS = [POP_SCREEN.binding]

    def __init__(self, *, data_sources: list[DataSource]) -> None:
        super().__init__()
        self._data_sources = data_sources

        self.title = "⚙️ Settings"

    def _compose_switch_with_label(self) -> list[SwitchWithLabel]:
        # Get length of longest label name, to align labels properly.
        label_length = [len(ds.label_name) for ds in self._data_sources]
        longest_name = max(label_length)

        widgets: list[SwitchWithLabel] = []
        for ds in self._data_sources:
            widget = (
                SwitchWithLabel(
                    label_text=ds.label_name,
                    switch_value=True,
                    label_format=True,
                    label_length=longest_name,
                    label_tooltip=ds.label_description,
                )
                if ds.authentication is DataSource.Authentication.NONE
                else (
                    SwitchWithInput(
                        label_text=ds.label_name,
                        switch_value=True,
                        label_format=True,
                        label_length=longest_name,
                        label_tooltip=ds.label_description,
                        input_placeholder="Enter API Key",
                    )
                )
            )
            widgets.append(widget)

        return widgets

    def compose(self) -> ComposeResult:
        yield Header(icon="")

        yield ContainerWithBorderLabel(
            "Data Sources", VerticalGroup, *self._compose_switch_with_label()
        )

        yield Footer()
