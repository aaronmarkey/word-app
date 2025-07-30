from word_app.data.models import Word
from word_app.ext import WAScreen
from word_app.ui.navigation.common import POP_SCREEN


class WordDetailScreen(WAScreen):
    AUTO_FOCUS = ""
    BINDINGS = [POP_SCREEN.binding]

    def __init__(self, *, word: Word) -> None:
        super().__init__()
        self._word = word

    @property
    def word(self) -> Word:
        return self._word
