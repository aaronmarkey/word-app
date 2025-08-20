from __future__ import annotations

from typing import AsyncGenerator

import httpx

from word_app.lib.datamuse.conf import (
    DEFAULT_API_CONF,
    DatamuseApiConf,
    DatamuseEndpoint,
    Suggestions,
    Words,
)
from word_app.lib.datamuse.exceptions import FailedToRefetchResult
from word_app.lib.datamuse.models import Suggestion, Word
from word_app.lib.datamuse.transformer import DatamuseTransformer
from word_app.lib.utils import http_client_factory


class DatamuseApiClient:
    """API client for Datamuse.

    https://www.datamuse.com/api/
    """

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        conf: DatamuseApiConf | None = None,
    ) -> None:
        self.conf = conf or DEFAULT_API_CONF
        self.client = client or http_client_factory()
        self.transformer = DatamuseTransformer()

    async def _request(self, *, endpoint: DatamuseEndpoint) -> httpx.Response:
        """Helper to make the actual HTTP request."""
        location = self.conf.full_path(endpoint)

        kwargs: dict[str, float | dict | None] = {"timeout": self.conf.timeout}
        kwargs["params"] = endpoint.params

        try:
            resp = await self.client.get(
                location,
                **kwargs,  # type: ignore
            )
            resp.raise_for_status()
            return resp
        except (httpx.RequestError, httpx.HTTPError) as exc:
            raise FailedToRefetchResult() from exc

    async def clean(self) -> None:
        """Clean up operations after done."""
        await self.client.aclose()

    async def get_suggestions(
        self, value: str, *, limit: int = 0
    ) -> AsyncGenerator[Suggestion]:
        """Yield Suggestion objects. for the provided value."""
        try:
            max = DatamuseEndpoint.Max(value=limit)
        except ValueError:
            max = DatamuseEndpoint.Max()

        endpoint = Suggestions(
            param_s=Suggestions.Prefix(value=value),
            param_max=max,
        )
        resp = await self._request(endpoint=endpoint)

        for data in resp.json():
            yield self.transformer.suggestion(data)

    async def get_words(
        self,
        *,
        means_like: str = "",
        spelled_like: str = "",
        sounds_like: str = "",
        limit: int = 0,
    ) -> AsyncGenerator[Word]:
        """Yield Word objects. for the provided 'likes'."""
        try:
            max = DatamuseEndpoint.Max(value=limit)
        except ValueError:
            max = DatamuseEndpoint.Max()

        params: Words.ParamsType = {
            "param_ml": Words.MeansLike(value=means_like.strip().lower()),
            "param_sl": Words.SoundsLike(value=sounds_like.strip().lower()),
            "param_sp": Words.SpelledLike(value=spelled_like.strip().lower()),
        }

        endpoint = Words(param_max=max, **params)

        resp = await self._request(endpoint=endpoint)

        for data in resp.json():
            yield self.transformer.word(data)
