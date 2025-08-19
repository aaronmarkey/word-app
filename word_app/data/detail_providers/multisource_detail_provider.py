import asyncio
from typing import AsyncGenerator

from word_app.data.detail_providers.base import AbstractWordDetailProvider
from word_app.data.models import Definition, Definitions, Word
from word_app.data.transformers import WnToWaTransformer
from word_app.lib.datamuse.client import DatamuseApiClient
from word_app.lib.wordnik.client import WordnikApiClient
from word_app.lib.wordnik.conf import Definitions as WnDefintions
from word_app.lib.wordnik.models import (
    AmericanHeritage,
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
                "Mission required clients for MultisourceDetailProvider object."
            )
        if datamuse_transformer is None or wordnik_transformer is None:
            raise ValueError(
                "Mission required transformers for "
                "MultisourceDetailProvider object."
            )
        self._datamuse_client: DatamuseApiClient = datamuse_client
        self._datamuse_transformer: WnToWaTransformer = datamuse_transformer
        self._wordnik_client: WordnikApiClient = wordnik_client
        self._wordnik_transformer: WnToWaTransformer = wordnik_transformer

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

    async def get_details_for_word(self, word: str) -> Word:
        async def definitions() -> Definitions:
            definitions: list[Definition] = []
            async for wnd in self._wn_definitions(word):
                definitions.append(self._wordnik_transformer.defintion(wnd))
            return Definitions(definitions=definitions)

        objs: tuple[Definitions] = await asyncio.gather(definitions())
        await self._wordnik_client.clean()
        return Word(word=word, definitions=objs[0])
