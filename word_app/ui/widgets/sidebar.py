from textual.app import ComposeResult
from textual.widgets import Button, Static


def SidebarButton(text) -> Button:
    return Button(text, variant="primary")


class Sidebar(Static):
    def __init__(self, elements: list[Button], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._elements = elements

    def compose(self) -> ComposeResult:
        yield from super().compose()

        for element in self._elements:
            yield element
