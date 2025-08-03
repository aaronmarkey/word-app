from enum import StrEnum

from wordnik import *

from word_app.data.models import Definition, Definitions, Nym, Thesaurus
from word_app.data.language import WordDetailType
from word_app.exceptions import WordAppException


WORKNIK_API_URL = "http://api.wordnik.com/v4"


def create_wordnik_client(
    api_key: str, api_url: str = WORKNIK_API_URL
) -> WordApi.WordApi:
    client = swagger.ApiClient(api_key, api_url)
    return WordApi.WordApi(client)


class WordnikTransformer:
    HTML_TO_TAG = {
        "<em>": "[i]",
        "</em>": "[/i]",
        "<strong>": "[b]",
        "</strong>": "[/b]",
    }

    @classmethod
    def html_to_tag(cls, text: str) -> str:
        new_text = text
        for html, tag in cls.HTML_TO_TAG.items():
            new_text = new_text.replace(html, tag)

        return new_text

    @classmethod
    def definition(cls, response) -> Definition | None:
        if response.partOfSpeech and response.text:
            text = cls.html_to_tag(response.text)
            return Definition(part_of_speech=response.partOfSpeech, text=text)
        return None

    @classmethod
    def nyms(cls, response) -> list[Nym]:
        nyms: list[Nym] = []
        _type = response.relationshipType.lower()
        if _type:
            for word in response.words:
                if word:
                    nyms.append(
                        Nym(
                            text=word,
                            type=_type,
                        )
                    )
        return nyms


class WordnikService:
    DEFINITION_LIMIT: int = 500
    THESAURUS_LIMIT: int = 1_000

    class SourceDictionary(StrEnum):
        AMERICAN_HERITAGE = "ahd-5"

    def __init__(self, client: WordApi.WordApi) -> None:
        self.client = client

    def get_word_definitions(
        self,
        word: str,
        *,
        limit: int = DEFINITION_LIMIT,
        source_dictionary: SourceDictionary = SourceDictionary.AMERICAN_HERITAGE,
    ) -> Definitions:
        try:
            responses = self.client.getDefinitions(
                word,
                sourceDictionaries=source_dictionary,
                limit=limit,
            )
            definitions = Definitions()
            for resp in responses:
                if d := WordnikTransformer.definition(resp):
                    definitions.definitions.append(d)
            return definitions
        except Exception as e:
            raise WordAppException() from e

    def get_word_thesaurus(
        self,
        word: str,
        *,
        limit: int = THESAURUS_LIMIT,
        types: list[WordDetailType] = WordDetailType.all(),
    ) -> Thesaurus:
        try:
            responses = self.client.getRelatedWords(
                word,
                # relationshipTypes=[type.value for type in types],
                limitPerRelationshipType=limit,
            )
            thesaurus = Thesaurus()
            for resp in responses:
                if nyms := WordnikTransformer.nyms(resp):
                    thesaurus.nyms.extend(nyms)
            return thesaurus
        except Exception as e:
            raise WordAppException() from e
