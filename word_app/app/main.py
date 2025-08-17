from __future__ import annotations

from textual.app import App
from textual.theme import BUILTIN_THEMES

from word_app.app.conf import AppContext
from word_app.lex import LEX
from word_app.ui.screens.home import HomeScreen
from word_app.ui.screens.quick_search.search import SuggestionPalette


class WordApp(App):
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("f", "push_suggestion", LEX.ui.btn.quick_find),
    ]

    CSS_PATH = "main.css"
    SCREENS = {"home": HomeScreen}
    TOOLTIP_DELAY = 0.2

    def __init__(self, *args, **kwargs) -> None:
        try:
            ctx = kwargs.pop("ctx")
        except KeyError:
            raise SystemError("Application context was not provided.")

        self.ctx: AppContext = ctx
        super().__init__(*args, **kwargs)

    # Base Class Methods.
    def get_theme_variable_defaults(self) -> dict[str, str]:
        # Change variables in word_app.ui.theme when doing updates.
        return {
            "footer-key-foreground": "#3376CD",
            "user-action": "#3376CD",
        }

    # Action Methods.
    def action_push_suggestion(self) -> None:
        self.app.push_screen(
            SuggestionPalette(
                placeholder=LEX.screen.quick_search.placeholder,
                providers=[self.ctx.deps.search_provider_cls],
            )
        )

    # Event handlers.
    def on_mount(self) -> None:
        for theme in self.ctx.deps.themes:
            self.register_theme(theme)
        for theme_name in BUILTIN_THEMES:
            self.unregister_theme(theme_name)

        self.theme = self.ctx.deps.theme_for_mode(
            self.ctx.settings.theme_mode
        ).name
        self.push_screen("home")
