from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Button

from word_app.ui.constants import BOUND_KEY, HELP_HOVER_ICON


def SidebarButton(
    text: str, *, desc: str = "", key_binding: str = "", **kwargs
) -> Button:
    if key_binding:
        text = f"{BOUND_KEY.format(key=key_binding)} {text}"
    if desc:
        text += f" {HELP_HOVER_ICON}"

    button = Button(text, variant="default", compact=False, **kwargs)

    if desc:
        button.tooltip = desc

    return button


class Sidebar(VerticalScroll):
    DEFAULT_CSS = """
    Sidebar {
        dock: left;
        width: 25%;
        height: 100vh;
        background: $background-lighten-1;

        &.wide {
            width: 40%;
        }

        &.with-footer {
            padding-bottom: 2;
        }

        &.with-header {
            offset: 0 1;
        }
        & > Button {
            width: 100%;
        }
    }
    """

    def __init__(self, elements: list[Widget], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._elements = elements

    def compose(self) -> ComposeResult:
        yield from super().compose()

        for element in self._elements:
            yield element
