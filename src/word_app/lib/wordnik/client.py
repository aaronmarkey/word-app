from copy import deepcopy
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, AsyncGenerator

import httpx

from word_app.lib._shr.utils import make_value_error
from word_app.lib.wordnik._transformer import WordnikTransformer
from word_app.lib.wordnik.endpoints import (
    DefinitionsEndpoint,
    ExamplesEndpoint,
    FrequencyEndpoint,
    HyphenationEndpoint,
    PhrasesEndpoint,
    RelatedWordsEndpoint,
    WordnikEndpoint,
)
from word_app.lib.wordnik.exceptions import (
    FailedToRefetchResult,
    Unauthorized,
)
from word_app.lib.wordnik.models import (
    Bigram,
    Definition,
    Example,
    FrequencySummary,
    Related,
    Syllable,
)


@dataclass(frozen=True, eq=True)
class WordnikApiConf:
    api_key: str
    root: str
    timeout: float | None

    def __post_init__(self) -> None:
        if to := self.timeout:
            if to < 0.0:
                make_value_error("timeout", str(to))

    def full_path(self, word: str, endpoint: WordnikEndpoint) -> str:
        return f"{self.root}/{endpoint.endpoint_fmt(word)}"


def DEFAULT_API_CONF(*, api_key: str) -> WordnikApiConf:
    return WordnikApiConf(
        api_key=api_key,
        root="https://api.wordnik.com/v4",
        timeout=1.0,
    )


class WordnikApiClient:
    def __init__(
        self, *, conf: WordnikApiConf, client: httpx.AsyncClient
    ) -> None:
        self.conf = conf
        self.client = client
        self.transformer = WordnikTransformer()
        self._cookie: str | None = None

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-type": "application/json",
        }
        if self._cookie:
            headers["Cookie"] = self._cookie
        return headers

    async def _request(
        self, word: str, endpoint: WordnikEndpoint
    ) -> httpx.Response:
        ep = deepcopy(endpoint)
        ep.api_key.value = self.conf.api_key
        location = self.conf.full_path(word, ep)
        headers = self._headers()
        kwargs: dict[str, Any] = {
            "timeout": self.conf.timeout,
            "headers": headers,
        }
        kwargs["params"] = ep.params

        try:
            resp = await self.client.get(location, **kwargs)
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == HTTPStatus.UNAUTHORIZED:
                raise Unauthorized() from exc
            raise FailedToRefetchResult() from exc
        except (httpx.RequestError, httpx.HTTPError) as exc:
            raise FailedToRefetchResult() from exc

    async def clean(self) -> None:
        """Clean up operations after done."""
        await self.client.aclose()

    async def get_definitions(
        self, *, word: str, endpoint: DefinitionsEndpoint
    ) -> AsyncGenerator[Definition, None]:
        resp = await self._request(word, endpoint)
        for definition in self.transformer.defintions(resp.json()):
            yield definition

    async def get_examples(
        self, *, word: str, endpoint: ExamplesEndpoint
    ) -> AsyncGenerator[Example, None]:
        resp = await self._request(word, endpoint)
        for example in self.transformer.example_search_result(resp.json()):
            yield example

    async def get_frequency(
        self, *, word: str, endpoint: FrequencyEndpoint
    ) -> FrequencySummary:
        resp = await self._request(word, endpoint)
        return self.transformer.frequency_summary(resp.json())

    async def get_hyphenation(
        self, *, word: str, endpoint: HyphenationEndpoint
    ) -> AsyncGenerator[Syllable, None]:
        resp = await self._request(word, endpoint)
        for syllable in self.transformer.syllable(resp.json()):
            yield syllable

    async def get_phrases(
        self, *, word: str, endpoint: PhrasesEndpoint
    ) -> AsyncGenerator[Bigram, None]:
        resp = await self._request(word, endpoint)
        for bigram in self.transformer.bigrams(resp.json()):
            yield bigram

    async def get_related_words(
        self, *, word: str, endpoint: RelatedWordsEndpoint
    ) -> AsyncGenerator[Related, None]:
        resp = await self._request(word, endpoint)
        for related in self.transformer.related(resp.json()):
            yield related
