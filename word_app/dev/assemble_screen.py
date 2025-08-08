from word_app.dev import fake
from word_app.ui.screens.word_detail import WordDetailScreen


def example_word_screen() -> WordDetailScreen:
    word = fake.WordFactory()
    return WordDetailScreen(word=word)
