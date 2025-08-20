import asyncio
from typing import AsyncGenerator, Callable

from word_app.data.detail_providers.base import AbstractWordDetailProvider
from word_app.data.models import (
    Definition,
    Definitions,
    Example,
    Examples,
    Nym,
    Phrase,
    Phrases,
    Thesaurus,
    Word,
)
from word_app.data.transformers import WnToWaTransformer
from word_app.lib.datamuse.client import DatamuseApiClient
from word_app.lib.wordnik.client import WordnikApiClient
from word_app.lib.wordnik.conf import Definitions as WnDefintions
from word_app.lib.wordnik.conf import Examples as WnExamples
from word_app.lib.wordnik.conf import Phrases as WnPhrases
from word_app.lib.wordnik.conf import RelatedWords as WnRelatedWords
from word_app.lib.wordnik.models import (
    AmericanHeritage,
    RelationshipType,
)


class MultisourceDetailProvider(AbstractWordDetailProvider):
    def __init__(self, *_, **kwargs) -> None:
        datamuse_client: DatamuseApiClient | None = kwargs.pop(
            "datamuse_client", None
        )
        wordnik_client: WordnikApiClient | None = kwargs.pop(
            "wordnik_client", None
        )
        datamuse_transformer: WnToWaTransformer | None = kwargs.pop(
            "datamuse_transformer", ""
        )
        wordnik_transformer: WnToWaTransformer | None = kwargs.pop(
            "wordnik_transformer", None
        )

        if datamuse_client is None or wordnik_client is None:
            raise ValueError(
                "Missing required clients for MultisourceDetailProvider object."
            )
        if datamuse_transformer is None or wordnik_transformer is None:
            raise ValueError(
                "Missing required transformers for "
                "MultisourceDetailProvider object."
            )
        self._datamuse_client: DatamuseApiClient = datamuse_client
        self._datamuse_transformer: WnToWaTransformer = datamuse_transformer
        self._wordnik_client: WordnikApiClient = wordnik_client
        self._wordnik_transformer: WnToWaTransformer = wordnik_transformer

    async def _wn_bigrams(self, word: str) -> AsyncGenerator:
        async for bigram in self._wordnik_client.get_phrases(
            word=word,
            endpoint=WnPhrases(
                word=WnPhrases.Word(value=word),
                limit=WnPhrases.Limit(value=50),
                wlmi=WnPhrases.Wlmi(value=10),
            ),
        ):
            yield bigram

    async def _wn_definitions(self, word: str) -> AsyncGenerator:
        async for definition in self._wordnik_client.get_definitions(
            word=word,
            endpoint=WnDefintions(
                word=WnDefintions.Word(value=word),
                limit=WnDefintions.Limit(value=10),
                include_related=WnDefintions.IncludeRelated(value=True),
                source_dictionaries=WnDefintions.SourceDictionaries(
                    value=[AmericanHeritage]
                ),
            ),
        ):
            yield definition

    async def _wn_examples(self, word: str) -> AsyncGenerator:
        async for example in self._wordnik_client.get_examples(
            word=word,
            endpoint=WnExamples(
                word=WnExamples.Word(value=word),
                limit=WnExamples.Limit(value=10),
            ),
        ):
            yield example

    async def _wn_thesaurus(self, word: str) -> AsyncGenerator:
        async for rl in self._wordnik_client.get_related_words(
            word=word,
            endpoint=WnRelatedWords(
                word=WnRelatedWords.Word(value=word),
                limit_per_relationship_type=WnRelatedWords.LimitPerRelationshipType(
                    value=1000
                ),
                relationship_types=WnRelatedWords.RelationshipTypes(
                    value=RelationshipType.all()
                ),
            ),
        ):
            yield rl

    async def _definitions(self, word: str) -> Definitions:
        definitions: list[Definition] = []
        async for wnd in self._wn_definitions(word):
            definitions.append(self._wordnik_transformer.defintion(wnd))
        return Definitions(definitions=definitions)

    async def _examples(self, word: str) -> Examples:
        examples: list[Example] = []
        async for wne in self._wn_examples(word):
            examples.append(self._wordnik_transformer.example(wne))
        return Examples(examples=examples)

    async def _phrases(self, word: str) -> Phrases:
        phrases: list[Phrase] = []
        async for wnb in self._wn_bigrams(word):
            phrases.append(self._wordnik_transformer.phrase(wnb))
        return Phrases(phrases=phrases)

    async def _thesaurus(self, word: str) -> Thesaurus:
        nyms: list[Nym] = []
        async for wnr in self._wn_thesaurus(word):
            nyms.extend(self._wordnik_transformer.thesaurus(wnr))
        return Thesaurus(nyms=nyms)

    async def clean(self) -> None:
        await self._wordnik_client.clean()

    async def get_details_for_word(
        self, word: str, on_failure: Callable[[Exception], None] | None = None
    ) -> Word | None:
        if on_failure is None:

            def _on_failure(e: Exception) -> None:
                raise e

            on_failure = _on_failure

        try:
            objs: tuple[
                Definitions, Thesaurus, Examples, Phrases
            ] = await asyncio.gather(
                self._definitions(word),
                self._thesaurus(word),
                self._examples(word),
                self._phrases(word),
            )
        except Exception as e:
            return on_failure(e)
        else:
            return Word(
                word=word,
                definitions=objs[0],
                thesaurus=objs[1],
                examples=objs[2],
                phrases=objs[3],
            )
