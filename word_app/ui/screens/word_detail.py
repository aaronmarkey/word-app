from textual.app import ComposeResult
from textual.widgets import Header, Footer
from word_app.data.models import Word
from word_app.ext import WAScreen
from word_app.ui.navigation.common import POP_SCREEN
from word_app.ui.widgets import Sidebar, SidebarButton


class WordDetailScreen(WAScreen):
    AUTO_FOCUS = ""
    BINDINGS = [POP_SCREEN.binding]

    WA_BINDING = "w"
    WA_ICON = "🗣️"
    WA_TITLE = "Word Details"

    def __init__(self, *, word: Word) -> None:
        super().__init__()
        self._word = word
        self.title = f"{self.WA_ICON}  {self._word.word}"

    @property
    def word(self) -> Word:
        return self._word

    def compose(self) -> ComposeResult:
        yield Sidebar([SidebarButton("Definitions")], classes="with-header")

        h = Header(icon="")
        h.disabled = True
        yield h

        yield Footer()
