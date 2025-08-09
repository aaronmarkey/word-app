from word_app.data.models import Definitions, Thesaurus
from word_app.data.services.base import BaseDataService
from word_app.data.wordnik.sources import AmericanHeritage
from word_app.data.wordnik.transformer import WordnikTransformer
from word_app.exceptions import WordAppException

from wordnik import WordApi, swagger

WORKNIK_API_URL = "http://api.wordnik.com/v4"


def create_wordnik_client(
    api_key: str, api_url: str = WORKNIK_API_URL
) -> WordApi.WordApi:
    client = swagger.ApiClient(api_key, api_url)
    return WordApi.WordApi(client)


class WordnikDataService(BaseDataService):
    DEFINITION_LIMIT: int = 500
    THESAURUS_LIMIT: int = 1_000

    def __init__(self, client: WordApi.WordApi, *args, **kwargs) -> None:
        self.client = client

    def get_word_definitions(self, word: str, *_, **kwargs) -> Definitions:
        limit = kwargs.get("limit", self.DEFINITION_LIMIT)
        source_dictionary = kwargs.get("source_dictionary", AmericanHeritage)

        try:
            responses = (
                self.client.getDefinitions(
                    word,
                    sourceDictionaries=source_dictionary.api_value,
                    limit=limit,
                )
                or []
            )
            definitions = Definitions(source=source_dictionary.title)
            for resp in responses:
                if d := WordnikTransformer.definition(resp):
                    definitions.definitions.append(d)
            return definitions
        except Exception as e:
            raise WordAppException() from e

    def get_word_thesaurus(self, word, *_, **kwargs) -> Thesaurus:
        limit = kwargs.get("limit", self.THESAURUS_LIMIT)

        try:
            responses = (
                self.client.getRelatedWords(
                    word,
                    limitPerRelationshipType=limit,
                )
                or []
            )
            thesaurus = Thesaurus()
            for resp in responses:
                if nyms := WordnikTransformer.nyms(resp):
                    thesaurus.nyms.extend(nyms)
            return thesaurus
        except Exception as e:
            raise WordAppException() from e
