from word_app.lex import EN_LANG
from word_app.ui.navigation.core import Navigateable

POP_SCREEN = Navigateable(
    action="app.pop_screen",
    kb_binding="escape",
    name=EN_LANG.BACK,
)
