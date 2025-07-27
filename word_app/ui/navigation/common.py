from word_app.ui.navigation.core import Navigateable

POP_SCREEN = Navigateable(
    action="app.pop_screen",
    id="back",
    name="Back",
    description="Go back to the previous screen.",
    kb_binding="escape"
)
