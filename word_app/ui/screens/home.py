from textual.app import ComposeResult
from textual.widgets import Footer

from word_app.ext import WAScreen
from word_app.ui.screens.settings import SettingsScreen
from word_app.ui.screens.word_detail import WordDetailScreen


class HomeScreen(WAScreen):
    AUTO_FOCUS = ""
    BINDINGS = [
        (SettingsScreen.WA_BINDING, "push_settings", SettingsScreen.WA_TITLE),
        (WordDetailScreen.WA_BINDING, "push_word", WordDetailScreen.WA_TITLE),
    ]

    # Base Class Methods
    def compose(self) -> ComposeResult:
        yield Footer()

    # Action Methods
    def action_push_settings(self) -> None:
        self.app.push_screen(SettingsScreen(), wait_for_dismiss=False)

    def action_push_word(self) -> None:
        word = self.app.ctx.deps.word_provider.get_word_details("")
        self.app.push_screen(WordDetailScreen(word=word))
