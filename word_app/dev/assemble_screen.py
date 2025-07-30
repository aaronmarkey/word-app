from word_app.data.models import Definition, Phrase, Word
from word_app.ui.screens import WordDetailScreen


def example_word_screen() -> WordDetailScreen:
    definition = Definition(
        part_of_speech="noun",
        text="The formation or use of words such as buzz or murmur that imitate the sounds associated with the objects or actions they refer to.",
    )
    phrase = Phrase(tokens=["Pokemon", "names", "are", "onomatopoeia"])

    word = Word(word="onomatopoeia", definitions=[definition], phrases=[phrase])

    return WordDetailScreen(word=word)
