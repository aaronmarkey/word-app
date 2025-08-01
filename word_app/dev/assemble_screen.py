from word_app.data.models import Definition, Definitions, Phrase, Word
from word_app.ui.screens import WordDetailScreen


def example_word_screen() -> WordDetailScreen:
    definition = Definition(
        part_of_speech="noun",
        text="The formation or use of words such as buzz or murmur that imitate the sounds associated with the objects or actions they refer to.",
    )
    phrase = Phrase(tokens=["Pokemon", "names", "are", "onomatopoeia"])

    definitions = Definitions(definitions=[definition])

    word = Word(word="onomatopoeia", definitions=definitions, phrases=[phrase])

    return WordDetailScreen(word=word)
