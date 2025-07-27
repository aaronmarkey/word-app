from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widget import Widget
from textual.widgets import Label, Switch


class SwitchWithLabel(Widget):

    _label_separator: ClassVar[str] = ":"

    def __init__(
        self,
        *,
        label_text: str,
        switch_value: bool,
        label_format: bool = True,
        label_tooltip: str = "",
    ) -> None:
            self.label_text = label_text
            self.label_format = label_format
            self.label_tooltip = label_tooltip

            self.switch_value = switch_value
            super().__init__()

    def _build_label(self) -> Label:
        lt = self.label_text

        if self.label_tooltip:
            lt += " (?)"

        if self.label_format:
            lt += self._label_separator

        label = Label(lt)

        if self.label_tooltip:
            label.tooltip = self.label_tooltip

        return label

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            self._build_label(),
            Switch(animate=True, value=self.switch_value)
        )
