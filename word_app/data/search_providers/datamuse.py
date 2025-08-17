import asyncio
from typing import Callable

from cachetools import FIFOCache
from textual.fuzzy import Matcher

from word_app.data.search_providers.models import (
    SearchResultType,
    SearchTermType,
)
from word_app.data.search_providers.parser import (
    ParseResult,
    RegexSearchTermParser,
)
from word_app.lib.datamuse.exceptions import DatamuseError
from word_app.lib.datamuse.client import DatamuseApiClient
from word_app.lib.datamuse.models import DatamuseModel, Suggestion, Word
from word_app.ui.screens.quick_search._models import Hit, Hits
from word_app.ui.screens.quick_search._providers import Provider
from word_app.ui.screens.word_detail import WordDetailScreen


def _min_max_normalize(
    value: int | float, min: int | float, max: int | float
) -> float:
    """https://en.wikipedia.org/wiki/Feature_scaling"""
    try:
        return (value - min) / (max - min)
    except ZeroDivisionError:
        return 0.0


class DatamuseSearchProvider(Provider):
    _API_LIMIT: int = 10
    _CACHE_MAX_SIZE: int = 50
    _MIN_CHARACTERS: int = 3
    _SCORE_THRESHHOLD: float = 0.01

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.client: DatamuseApiClient = kwargs.get(
            "client", DatamuseApiClient()
        )
        self._cache: FIFOCache

    def _action(self, word: str):
        async def __action():
            details = self.app.ctx.deps.word_provider.get_word_details(word)
            self.app.push_screen(WordDetailScreen(word=details))

        return __action

    def _clean_hits(self, hits: list[Hit]) -> list[Hit]:
        """Clean up a list of hits.

        Notes:
            - Remove duplicates, the one with a higher score stays.
            - Sort hits, remove ones with score below class threshhold.
        """
        as_dict: dict[str | None, Hit] = {}
        for hit in hits:
            current = as_dict.get(hit.text, None)
            if current is None or hit.score > current.score:
                as_dict[hit.text] = hit

        return sorted(
            [h for h in as_dict.values() if h.score >= self._SCORE_THRESHHOLD],
            key=lambda hit: hit.score,
            reverse=True,
        )

    def _make_hit(
        self,
        dm: DatamuseModel,
        sug_type: SearchResultType,
        matcher: Matcher,
        highest_score: int | float,
        lowest_score: int | float,
    ) -> Hit:
        score = _min_max_normalize(dm.score, lowest_score, highest_score)

        return Hit(
            score=score,
            match_display=matcher.highlight(dm.word),
            action=self._action(dm.word),
            text=dm.word,
            help=f"{sug_type.display} ({round(score, 4)})",
        )

    def _make_hits(
        self, query: str, objs: list[DatamuseModel], str: SearchResultType
    ) -> list[Hit]:
        matcher = self.matcher(query)
        highest_score = max(objs, key=lambda o: o.score).score
        lowest_score = min(objs, key=lambda o: o.score).score
        return [
            self._make_hit(
                o,
                str,
                matcher,
                highest_score,
                lowest_score,
            )
            for o in objs
        ]

    def _parse_query(self, query: str) -> ParseResult:
        query = query.strip().lower()
        parser = RegexSearchTermParser()
        result = parser.parse(query)

        if len(query) < self._MIN_CHARACTERS:
            if result.type is SearchTermType.SPELLED_LIKE:
                return result
            return ParseResult(type=SearchTermType.UNKNOWN, text=query)
        return result

    async def _fetch(self, query: str, *fetchers: Callable) -> list[list[Hit]]:
        objs: list[
            tuple[SearchResultType, list[DatamuseModel]]
        ] = await asyncio.gather(*[fetcher(query) for fetcher in fetchers])

        results: list[list[Hit]] = []

        for srt, obj in objs:
            results.append(self._make_hits(query, obj, srt))

        return results

    async def _fetch_means_like(
        self, query: str
    ) -> tuple[SearchResultType, list[Word]]:
        words: list[Word] = []
        try:
            async for suggestion in self.client.get_words(
                means_like=query, limit=self._API_LIMIT
            ):
                words.append(suggestion)
        except DatamuseError:
            pass

        return SearchResultType.MEANS_LIKE, words

    async def _fetch_sounds_like(
        self, query: str
    ) -> tuple[SearchResultType, list[Word]]:
        words: list[Word] = []
        try:
            async for suggestion in self.client.get_words(
                sounds_like=query, limit=self._API_LIMIT
            ):
                words.append(suggestion)
        except DatamuseError:
            pass

        return SearchResultType.SOUNDS_LIKE, words

    async def _fetch_spelled_like(
        self, query: str
    ) -> tuple[SearchResultType, list[Word]]:
        query = query.replace("*", "#").replace("?", "*").replace("#", "?")
        words: list[Word] = []

        try:
            async for suggestion in self.client.get_words(spelled_like=query):
                words.append(suggestion)
        except DatamuseError:
            pass

        return SearchResultType.SPELLED_LIKE, words

    async def _fetch_suggestions(
        self, query: str
    ) -> tuple[SearchResultType, list[Suggestion]]:
        suggestions: list[Suggestion] = []

        try:
            async for suggestion in self.client.get_suggestions(
                query, limit=self._API_LIMIT
            ):
                suggestions.append(suggestion)
        except DatamuseError:
            pass

        return SearchResultType.SUGGESTION, suggestions

    async def search(self, query: str) -> Hits:
        parse_result = self._parse_query(query)
        if parse_result.type is SearchTermType.UNKNOWN:
            return

        if cached_hits := self._cache.get(parse_result.text, None):
            for ch in cached_hits:
                yield ch

        results: list[list[Hit]] = []
        if parse_result.type is SearchTermType.SUGGEST_SOUNDS_LIKE:
            results = await self._fetch(
                parse_result.text,
                self._fetch_suggestions,
                self._fetch_sounds_like,
            )
        elif parse_result.type is SearchTermType.SUGGEST_MEANS_LIKE:
            results = await self._fetch(
                parse_result.text,
                self._fetch_suggestions,
                self._fetch_means_like,
            )
        elif parse_result.type is SearchTermType.SPELLED_LIKE:
            results = await self._fetch(
                parse_result.text, self._fetch_spelled_like
            )

        hits: list[Hit] = self._clean_hits(sum(results, []))
        self._cache[parse_result.text] = hits
        for hit in hits:
            yield hit

    async def shutdown(self) -> None:
        for _ in range(len(self._cache)):
            self._cache.popitem()
        del self._cache
        await self.client.clean()

    async def startup(self) -> None:
        self._cache = FIFOCache(maxsize=self._CACHE_MAX_SIZE)
