from typing import TYPE_CHECKING

from textual.screen import Screen

if TYPE_CHECKING:
    from word_app.app.tui.main import WordApp


class WAScreen(Screen):
    WA_BINDING: str = ""
    WA_ICON: str = ""
    WA_DESCRIPTION: str = ""
    WA_TITLE: str = ""

    def __init__(self, *args, **kwargs) -> None:
        self.app: "WordApp"
        super().__init__(*args, **kwargs)
