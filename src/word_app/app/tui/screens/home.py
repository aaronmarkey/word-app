from textual.app import ComposeResult
from textual.widgets import Footer

from word_app.app.tui.ext import WAScreen
from word_app.app.tui.screens.settings import SettingsScreen
from word_app.app.tui.screens.word_detail import WordDetailScreen


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

    async def action_push_word(self) -> None:
        if word := await self.app.ctx.deps.detail_provider.get_details_for_word(
            ""
        ):
            self.app.push_screen(WordDetailScreen(word=word))
