from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Footer, Header, Switch

from word_app.app.conf import AppConf
from word_app.data.sources import DataSource
from word_app.ext import WAScreen
from word_app.ui.containers import ContainerWithBorderLabel
from word_app.ui.navigation.common import POP_SCREEN
from word_app.ui.widgets import SwitchWithLabel
from word_app.ui.widgets.switch_with_label import SwitchWithInput


class SettingsScreen(WAScreen):
    WA_BINDING = "s"
    WA_DESCRIPTION = "Configure the application."
    WA_TITLE = "Settings"

    AUTO_FOCUS = ""
    BINDINGS = [POP_SCREEN.binding]
    TITLE = "⚙️ " + WA_TITLE

    def __init__(
        self, *, app_conf: AppConf, data_sources: list[DataSource]
    ) -> None:
        super().__init__()
        self._app_conf = app_conf
        self._data_sources = data_sources

    def _compose_switch_with_label(self) -> list[SwitchWithLabel]:
        # Get length of longest label name, to align labels properly.
        label_length = [len(ds.label_name) for ds in self._data_sources]
        longest_name = max(label_length)

        widgets: list[SwitchWithLabel] = []
        for ds in self._data_sources:
            if ds_conf := getattr(self._app_conf.ds, ds.id, None):
                widget = (
                    SwitchWithLabel(
                        id=ds.id,
                        label_text=ds.label_name,
                        label_format=True,
                        label_length=longest_name,
                        label_tooltip=ds.label_description,
                        switch_value=ds_conf.enabled,
                    )
                    if ds.authentication is DataSource.Authentication.NONE
                    else (
                        SwitchWithInput(
                            id=ds.id,
                            label_text=ds.label_name,
                            label_format=True,
                            label_length=longest_name,
                            label_tooltip=ds.label_description,
                            input_placeholder="Enter API Key",
                            input_value=ds_conf.api_key,
                            switch_value=ds_conf.enabled,
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

    @on(Switch.Changed, "#datamuse")
    def switch_changed(self, event: Switch.Changed) -> None:
        print(event.value)
