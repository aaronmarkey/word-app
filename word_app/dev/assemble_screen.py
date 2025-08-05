from word_app.data.models import Word
from word_app.data.wordnik.service import (
    WordnikDataService,
    create_wordnik_client,
)
from word_app.dev import fake
from word_app.ui.screens.word_detail import WordDetailScreen


def example_word_screen(conf) -> WordDetailScreen:
    # w = "paper"
    # wnc = create_wordnik_client(conf.ds.wordnik.api_key)
    # service = WordnikDataService(wnc)
    # definitions = service.get_word_definitions(w)
    # thesaurus = service.get_word_thesaurus(w)
    # word = Word(word=word, definitions=definitions, thesaurus=thesaurus)

    word = fake.WordFactory()

    return WordDetailScreen(word=word)
