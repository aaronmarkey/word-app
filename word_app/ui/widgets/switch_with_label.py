from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widget import Widget
from textual.widgets import Input, Label, Switch

from word_app.ui.constants import TOOLTIP_ICON


class SwitchWithLabel(Widget):
    def __init__(
        self,
        *,
        id: str,
        label_text: str,
        switch_value: bool,
        label_length: int = -1,
        label_format: bool = True,
        label_separator: str = ":",
        label_tooltip: str = "",
    ) -> None:
        super().__init__()
        self.id = id
        self.label_text = label_text
        self.label_length = label_length
        self.label_format = label_format
        self.label_separator = label_separator
        self.label_tooltip = label_tooltip

        self.switch_value = switch_value

    def _build_label(self) -> Label:
        diff = self.label_length - len(self.label_text)
        padding = 0 if diff < 0 else diff
        lt = f"{' ' * padding}{self.label_text}"

        if self.label_tooltip:
            lt += f" {TOOLTIP_ICON}"

        if self.label_format:
            lt += self.label_separator

        label = Label(lt)

        if self.label_tooltip:
            label.tooltip = self.label_tooltip

        return label

    def _build_switch(self) -> Switch:
        return Switch(animate=False, id=self.id, value=self.switch_value)

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
        id: str,
        label_text: str,
        input_placeholder: str,
        switch_value: bool,
        input_value: str = "",
        label_length: int = -1,
        label_format: bool = True,
        label_separator: str = ":",
        label_tooltip: str = "",
    ) -> None:
        super().__init__(
            id=id,
            label_text=label_text,
            switch_value=switch_value,
            label_length=label_length,
            label_format=label_format,
            label_separator=label_separator,
            label_tooltip=label_tooltip,
        )
        self.input_placeholder = input_placeholder
        self.input_value = input_value
        self.child_input = self._build_input()

    def _build_input(self) -> Input:
        inp = Input(self.input_value, placeholder=self.input_placeholder)
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
