from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Footer, Header, Input, Switch

from word_app.app.conf import AppConf
from word_app.data.sources import DataSource
from word_app.ext import WAScreen
from word_app.lex import EN_LANG
from word_app.ui.containers import ContainerWithBorderLabel
from word_app.ui.navigation.common import POP_SCREEN
from word_app.ui.widgets import SwitchWithInput, SwitchWithLabel


class WidgetId:
    sep: ClassVar[str] = "--"

    @classmethod
    def generate(cls, id: str, prop: str) -> str:
        return f"{id}{cls.sep}{prop}"

    @classmethod
    def parse(cls, id: str) -> tuple[str, str]:
        values = id.split(cls.sep)
        if len(values) != 2:
            raise ValueError(f"Invalid widget ID: {id}")
        return values[0], values[1]


class SettingsScreen(WAScreen):
    WA_BINDING = "s"
    WA_DESCRIPTION = EN_LANG.SETTINGS_SCREEN_DESC
    WA_ICON = "⚙️"
    WA_TITLE = EN_LANG.SETTINGS_SCREEN_TITLE

    AUTO_FOCUS = ""
    BINDINGS = [POP_SCREEN.binding]
    TITLE = WA_ICON + " " + WA_TITLE

    def __init__(
        self, *, app_conf: AppConf, data_sources: list[DataSource]
    ) -> None:
        super().__init__()
        self._app_conf = app_conf
        self._data_sources = data_sources

    def _compose_data_sources_section(self) -> list[SwitchWithLabel]:
        # Get length of longest label name, to align labels properly.
        label_length = [len(ds.label_name) for ds in self._data_sources]
        longest_name = max(label_length)

        widgets: list[SwitchWithLabel] = []
        for ds in self._data_sources:
            if ds_conf := getattr(self._app_conf.ds, ds.id, None):
                widget = (
                    SwitchWithLabel(
                        label_text=ds.label_name,
                        label_format=True,
                        label_length=longest_name,
                        label_tooltip=ds.label_description,
                        switch_value=ds_conf.enabled,
                        switch_id=WidgetId.generate(ds.id, "enabled"),
                    )
                    if ds.authentication is DataSource.Authentication.NONE
                    else (
                        SwitchWithInput(
                            label_text=ds.label_name,
                            label_format=True,
                            label_length=longest_name,
                            label_tooltip=ds.label_description,
                            input_placeholder=EN_LANG.INPUT_API_KEY_PLACEHOLDER,
                            input_value=ds_conf.api_key,
                            switch_value=ds_conf.enabled,
                            switch_id=WidgetId.generate(ds.id, "enabled"),
                            input_id=WidgetId.generate(ds.id, "api_key"),
                        )
                    )
                )
                widgets.append(widget)

        return widgets

    def compose(self) -> ComposeResult:
        h = Header(icon="")
        h.disabled = True
        yield h

        yield ContainerWithBorderLabel(
            EN_LANG.SETTINGS_SCREEN_SECTION_DS_TITLE,
            VerticalGroup,
            *self._compose_data_sources_section(),
        )

        yield Footer()

    @on(Switch.Changed)
    def switch_changed(self, event: Switch.Changed) -> None:
        event.stop()
        _id = event.switch.id or ""
        ds, prop = WidgetId.parse(_id)
        self._app_conf.update_ds_by_name(ds, prop, event.switch.value)

    @on(Input.Changed)
    def input_changed(self, event: Input.Changed) -> None:
        event.stop()
        _id = event.input.id or ""
        ds, prop = WidgetId.parse(_id)
        self._app_conf.update_ds_by_name(ds, prop, event.input.value)
