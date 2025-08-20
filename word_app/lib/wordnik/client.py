from copy import deepcopy
from http import HTTPStatus
from typing import Any

import httpx
from typing_extensions import AsyncGenerator

from word_app.lib.wordnik.conf import (
    Definitions,
    RelatedWords,
    WordnikApiConf,
    WordnikEndpoint,
)
from word_app.lib.wordnik.exceptions import FailedToRefetchResult, Unauthorized
from word_app.lib.wordnik.models import Definition, Related
from word_app.lib.wordnik.transformer import WordnikTransformer


class WordnikApiClient:
    def __init__(
        self, *, conf: WordnikApiConf, client: httpx.AsyncClient | None = None
    ) -> None:
        self.conf = conf
        self.client = client or httpx.AsyncClient()
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

    async def get_definitions(
        self, *, word: str, endpoint: Definitions
    ) -> AsyncGenerator[Definition]:
        resp = await self._request(word, endpoint)
        for definition in self.transformer.defintions(resp.json()):
            yield definition

    async def get_related_words(
        self, *, word: str, endpoint: RelatedWords
    ) -> AsyncGenerator[Related]:
        resp = await self._request(word, endpoint)
        for related in self.transformer.related(resp.json()):
            yield related

    async def clean(self) -> None:
        """Clean up operations after done."""
        await self.client.aclose()
