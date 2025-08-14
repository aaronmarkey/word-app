from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widget import Widget
from textual.widgets import Input, Label, Switch

from word_app.ui.widgets.labels import WALabel


class SwitchWithLabel(Widget):
    DEFAULT_CSS = """
    SwitchWithLabel {
        height: auto;
        layout: horizontal;
        width: auto;
        margin-bottom: 1;
        margin-top: 1;
        padding-right: 2;
        padding-left: 2;

        Label {
            padding-right: 1;
            padding-top: 1;
        }
    }
    """

    def __init__(
        self,
        *,
        label_text: str,
        switch_value: bool,
        switch_id: str,
        label_length: int = -1,
        label_format: bool = True,
        label_separator: str = ":",
        label_tooltip: str = "",
    ) -> None:
        super().__init__()
        self.label_text = label_text
        self.label_length = label_length
        self.label_format = label_format
        self.label_separator = label_separator
        self.label_tooltip = label_tooltip

        self.switch_id = switch_id
        self.switch_value = switch_value

    def _build_label(self) -> Label:
        diff = self.label_length - len(self.label_text)
        padding = 0 if diff < 0 else diff

        return WALabel(
            self.label_text,
            lpadding=padding,
            tooltip=self.label_tooltip,
            separator=self.label_separator,
        )

    def _build_switch(self) -> Switch:
        return Switch(animate=False, id=self.switch_id, value=self.switch_value)

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            self._build_label(),
            self._build_switch(),
        )

    def on_switch_changed(self, event: Switch.Changed) -> None:
        self.switch_value = event.value


class SwitchWithInput(SwitchWithLabel):
    def __init__(
        self,
        *,
        label_text: str,
        input_placeholder: str,
        switch_value: bool,
        switch_id: str,
        input_id: str,
        input_value: str = "",
        label_length: int = -1,
        label_format: bool = True,
        label_separator: str = ":",
        label_tooltip: str = "",
    ) -> None:
        super().__init__(
            label_text=label_text,
            switch_id=switch_id,
            switch_value=switch_value,
            label_length=label_length,
            label_format=label_format,
            label_separator=label_separator,
            label_tooltip=label_tooltip,
        )
        self.input_id = input_id
        self.input_placeholder = input_placeholder
        self.input_value = input_value
        self.child_input = self._build_input()

    def _build_input(self) -> Input:
        inp = Input(
            self.input_value,
            id=self.input_id,
            placeholder=self.input_placeholder,
        )
        inp.display = self.switch_value
        return inp

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            self._build_label(),
            self._build_switch(),
            self.child_input,
        )

    def on_switch_changed(self, event: Switch.Changed) -> None:
        super().on_switch_changed(event)
        self.child_input.display = self.switch_value
