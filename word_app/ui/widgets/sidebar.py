from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Button, Static

from word_app.ui.constants import BOUND_KEY, TOOLTIP_ICON


def SidebarButton(
    text: str, *, desc: str = "", key_binding: str = ""
) -> Button:
    if key_binding:
        text = f"{BOUND_KEY.format(key=key_binding)} {text}"
    if desc:
        text += f" {TOOLTIP_ICON}"

    button = Button(text, variant="primary", compact=True)

    if desc:
        button.tooltip = desc

    return button


class Sidebar(VerticalScroll):
    def __init__(self, elements: list[Button], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._elements = elements

    def compose(self) -> ComposeResult:
        yield from super().compose()

        for element in self._elements:
            yield element
