import asyncio
from typing import AsyncGenerator, Callable

from word_app.data.models import (
    Definition,
    Definitions,
    Example,
    Examples,
    FrequencyGraph,
    FrequencyInterval,
    Nym,
    Phrase,
    Phrases,
    Syllable,
    Syllables,
    Thesaurus,
    Word,
)
from word_app.infra.worknik.transformers import WnToWaTransformer
from word_app.lib.wordnik.client import WordnikApiClient
from word_app.lib.wordnik.endpoints import (
    DefinitionsEndpoint,
    ExamplesEndpoint,
    FrequencyEndpoint,
    HyphenationEndpoint,
    PhrasesEndpoint,
    RelatedWordsEndpoint,
)
from word_app.lib.wordnik.models import FrequencySummary
from word_app.lib.wordnik.vo import AmericanHeritage, RelationshipType
from word_app.services.wdp.base import AbstractWordDetailProvider


class MultisourceDetailProvider(AbstractWordDetailProvider):
    def __init__(self, *_, **kwargs) -> None:
        try:
            wordnik_client: WordnikApiClient = kwargs["wordnik_client"]
            wordnik_transformer: WnToWaTransformer = kwargs[
                "wordnik_transformer"
            ]
        except KeyError as e:
            raise ValueError(
                "Missing initialization argument for "
                f"'{self.__class__.__name__}'."
            ) from e

        self._wordnik_client: WordnikApiClient = wordnik_client
        self._wordnik_transformer: WnToWaTransformer = wordnik_transformer

    async def _wn_bigrams(self, word: str) -> AsyncGenerator:
        async for bigram in self._wordnik_client.get_phrases(
            word=word,
            endpoint=PhrasesEndpoint(
                word=PhrasesEndpoint.Word(value=word),
                limit=PhrasesEndpoint.Limit(value=50),
                wlmi=PhrasesEndpoint.Wlmi(value=10),
            ),
        ):
            yield bigram

    async def _wn_definitions(self, word: str) -> AsyncGenerator:
        async for definition in self._wordnik_client.get_definitions(
            word=word,
            endpoint=DefinitionsEndpoint(
                word=DefinitionsEndpoint.Word(value=word),
                limit=DefinitionsEndpoint.Limit(value=10),
                include_related=DefinitionsEndpoint.IncludeRelated(value=True),
                source_dictionaries=DefinitionsEndpoint.SourceDictionaries(
                    value=[AmericanHeritage]
                ),
            ),
        ):
            yield definition

    async def _wn_examples(self, word: str) -> AsyncGenerator:
        async for example in self._wordnik_client.get_examples(
            word=word,
            endpoint=ExamplesEndpoint(
                word=ExamplesEndpoint.Word(value=word),
                limit=ExamplesEndpoint.Limit(value=10),
            ),
        ):
            yield example

    async def _wn_frequency(self, word: str) -> FrequencySummary:
        return await self._wordnik_client.get_frequency(
            word=word,
            endpoint=FrequencyEndpoint(
                word=FrequencyEndpoint.Word(value=word),
            ),
        )

    async def _wn_syllables(self, word: str) -> AsyncGenerator:
        async for syllable in self._wordnik_client.get_hyphenation(
            word=word,
            endpoint=HyphenationEndpoint(
                word=HyphenationEndpoint.Word(value=word),
                limit=HyphenationEndpoint.Limit(value=1),
                source_dictionaries=HyphenationEndpoint.SourceDictionaries(
                    value=[AmericanHeritage]
                ),
            ),
        ):
            yield syllable

    async def _wn_thesaurus(self, word: str) -> AsyncGenerator:
        async for rl in self._wordnik_client.get_related_words(
            word=word,
            endpoint=RelatedWordsEndpoint(
                word=RelatedWordsEndpoint.Word(value=word),
                limit_per_relationship_type=RelatedWordsEndpoint.LimitPerRelationshipType(
                    value=1000
                ),
                relationship_types=RelatedWordsEndpoint.RelationshipTypes(
                    value=RelationshipType.all()
                ),
            ),
        ):
            yield rl

    async def _definitions(self, word: str) -> Definitions:
        definitions: list[Definition] = []
        async for wnd in self._wn_definitions(word):
            if d := self._wordnik_transformer.defintion(wnd):
                definitions.append(d)
        return Definitions(definitions=definitions)

    async def _examples(self, word: str) -> Examples:
        examples: list[Example] = []
        async for wne in self._wn_examples(word):
            examples.append(self._wordnik_transformer.example(wne))
        return Examples(examples=examples)

    async def _frequency(self, word: str) -> FrequencyGraph:
        fi: list[FrequencyInterval] = []
        freq = await self._wn_frequency(word)
        highest_value = max(*freq.frequency, key=lambda f: f.count).count
        for i in freq.frequency:
            fi.append(
                FrequencyInterval(
                    start=i.year,
                    end=i.year,
                    value=float(i.count / highest_value),
                )
            )
        return FrequencyGraph(intervals=fi)

    async def _phrases(self, word: str) -> Phrases:
        phrases: list[Phrase] = []
        async for wnb in self._wn_bigrams(word):
            phrases.append(self._wordnik_transformer.phrase(wnb))
        return Phrases(phrases=phrases)

    async def _syllables(self, word: str) -> Syllables:
        syllables: list[Syllable] = []
        async for wns in self._wn_syllables(word):
            syllables.append(self._wordnik_transformer.syllable(wns))
        return Syllables(syllables=syllables)

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
                Definitions,
                Thesaurus,
                Examples,
                Phrases,
                Syllables,
                FrequencyGraph,
            ] = await asyncio.gather(
                self._definitions(word),
                self._thesaurus(word),
                self._examples(word),
                self._phrases(word),
                self._syllables(word),
                self._frequency(word),
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
                syllables=objs[4],
                frequency_graph=objs[5],
            )
