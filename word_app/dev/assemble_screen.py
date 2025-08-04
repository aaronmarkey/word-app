from word_app.data.models import Word
from word_app.ui.screens.word_detail import WordDetailScreen

from word_app.data.services.wordnik import WordnikService, create_wordnik_client


def example_word_screen(conf) -> WordDetailScreen:
    wnc = create_wordnik_client(conf.ds.wordnik.api_key)
    service = WordnikService(wnc)
    word = "paper"

    definitions = service.get_word_definitions(word)
    thesaurus = service.get_word_thesaurus(word)

    word = Word(word=word, definitions=definitions, thesaurus=thesaurus)

    return WordDetailScreen(word=word)
