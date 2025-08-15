from textual.fuzzy import Matcher
from word_app.data.search_providers.models import SearchSuggestionType
from word_app.lib.datamuse.client import DatamuseClient
from word_app.lib.datamuse.models import DatamuseModel, Suggestion, Word
from word_app.search.parser import (
    ParseResult,
    RegexSearchTermParser,
    SearchTermType,
)
from word_app.ui.screens.quick_search._models import Hit, Hits
from word_app.ui.screens.quick_search._providers import Provider
from word_app.ui.screens.word_detail import WordDetailScreen


def _min_max_normalize(
    value: int | float, min: int | float, max: int | float
) -> float:
    """https://en.wikipedia.org/wiki/Feature_scaling"""
    return (value - min) / (max - min)


class DatamuseSearchProvider(Provider):
    _MIN_CHARACTERS: int = 3
    _API_LIMIT: int = 10

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.dm_client: DatamuseClient = kwargs.get(
            "dm_client", DatamuseClient()
        )

    def _action(self, word: str):
        async def __action():
            details = self.app.ctx.deps.word_provider.get_word_details(word)
            self.app.push_screen(WordDetailScreen(word=details))

        return __action

    def _parse_query(self, query: str) -> ParseResult:
        query = query.strip().lower()
        if len(query) < self._MIN_CHARACTERS:
            return ParseResult(type=SearchTermType.UNKNOWN, text=query)

        parser = RegexSearchTermParser()
        return parser.parse(query)

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

    async def _get_suggestions(self, query: str) -> list[Hit]:
        matcher = self.matcher(query)
        suggestions: list[Suggestion] = []
        async for suggestion in self.dm_client.aget_suggestions(
            query, limit=self._API_LIMIT
        ):
            suggestions.append(suggestion)

        highest_score = max(*suggestions, key=lambda s: s.score).score
        lowest_score = min(*suggestions, key=lambda s: s.score).score
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

    async def _get_sounds_like(self, query: str) -> list[Hit]:
        matcher = self.matcher(query)
        words: list[Word] = []
        async for suggestion in self.dm_client.aget_words(
            means_like=query, limit=self._API_LIMIT
        ):
            words.append(suggestion)

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

    async def search(self, query: str) -> Hits:
        parse_result = self._parse_query(query)

        if parse_result.type is SearchTermType.SUGGEST_SOUNDS_LIKE:
            suggestions = await self._get_suggestions(parse_result.text)
            words = await self._get_sounds_like(parse_result.text)

            hits = sorted(
                suggestions + words, key=lambda sw: sw.score, reverse=True
            )
            for hit in hits:
                yield hit

        return

    async def shutdown(self) -> None:
        await self.dm_client.aclean()
