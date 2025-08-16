import asyncio
from typing import Callable

from cachetools import FIFOCache
from textual.fuzzy import Matcher

from word_app.data.search_providers.models import SearchSuggestionType
from word_app.data.search_providers.parser import (
    ParseResult,
    RegexSearchTermParser,
    SearchTermType,
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
        sug_type: SearchSuggestionType,
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

    def _parse_query(self, query: str) -> ParseResult:
        query = query.strip().lower()
        parser = RegexSearchTermParser()
        result = parser.parse(query)

        if len(query) < self._MIN_CHARACTERS:
            if result.type is SearchTermType.SPELLED_LIKE:
                return result
            return ParseResult(type=SearchTermType.UNKNOWN, text=query)
        return result

    async def _fetch_means_like(self, query: str) -> list[Hit]:
        matcher = self.matcher(query)
        words: list[Word] = []
        try:
            async for suggestion in self.client.get_words(
                means_like=query, limit=self._API_LIMIT
            ):
                words.append(suggestion)
        except DatamuseError:
            pass

        highest_score = max(*words, key=lambda w: w.score).score
        lowest_score = min(*words, key=lambda w: w.score).score
        return [
            self._make_hit(
                w,
                SearchSuggestionType.MEANS_LIKE,
                matcher,
                highest_score,
                lowest_score,
            )
            for w in words
        ]

    async def _fetch_sounds_like(self, query: str) -> list[Hit]:
        matcher = self.matcher(query)
        words: list[Word] = []

        try:
            async for suggestion in self.client.get_words(
                sounds_like=query, limit=self._API_LIMIT
            ):
                words.append(suggestion)
        except DatamuseError:
            pass

        highest_score = max(*words, key=lambda w: w.score).score
        lowest_score = min(*words, key=lambda w: w.score).score
        return [
            self._make_hit(
                w,
                SearchSuggestionType.SOUNDS_LIKE,
                matcher,
                highest_score,
                lowest_score,
            )
            for w in words
        ]

    async def _fetch_spelled_like(self, query: str) -> list[Hit]:
        query = query.replace("*", "#").replace("?", "*").replace("#", "?")
        matcher = self.matcher(query)
        words: list[Word] = []

        try:
            async for suggestion in self.client.get_words(spelled_like=query):
                words.append(suggestion)
        except DatamuseError:
            pass

        highest_score = max(*words, key=lambda w: w.score).score
        lowest_score = min(*words, key=lambda w: w.score).score
        return [
            self._make_hit(
                w,
                SearchSuggestionType.SPELLED_LIKE,
                matcher,
                highest_score,
                lowest_score,
            )
            for w in words
        ]

    async def _fetch_suggestions(self, query: str) -> list[Hit]:
        matcher = self.matcher(query)
        suggestions: list[Suggestion] = []

        try:
            async for suggestion in self.client.get_suggestions(
                query, limit=self._API_LIMIT
            ):
                suggestions.append(suggestion)
        except DatamuseError:
            pass

        highest_score = max(suggestions, key=lambda s: s.score).score
        lowest_score = min(suggestions, key=lambda s: s.score).score
        return [
            self._make_hit(
                sug,
                SearchSuggestionType.SUGGESTION,
                matcher,
                highest_score,
                lowest_score,
            )
            for sug in suggestions
        ]

    async def _fetch(self, query: str, *fetchers: Callable) -> list[list[Hit]]:
        results: list[list[Hit]] = await asyncio.gather(
            *[fetcher(query) for fetcher in fetchers]
        )
        return results

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
