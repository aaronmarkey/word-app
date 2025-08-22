from dataclasses import dataclass
from typing import AsyncGenerator

import httpx

from word_app.lib._shr.utils import make_value_error
from word_app.lib.datamuse._models import Suggestion, Word
from word_app.lib.datamuse._transformer import DatamuseTransformer
from word_app.lib.datamuse.endpoints import (
    DatamuseEndpoint,
    SuggestionsEndpoint,
    WordsEndpoint,
)
from word_app.lib.datamuse.exceptions import FailedToRefetchResult


@dataclass(frozen=True, eq=True)
class DatamuseApiConf:
    """Datamuse API configuration."""

    root: str
    """The base URL of the Datamuse API."""
    timeout: float | None
    """Default timeout to use on requests to API, in seconds."""

    def __post_init__(self) -> None:
        if to := self.timeout:
            if to < 0.0:
                make_value_error("timeout", str(to))

    def full_path(self, endpoint: DatamuseEndpoint) -> str:
        return f"{self.root}/{endpoint.endpoint}"


DEFAULT_API_CONF = DatamuseApiConf(
    root="https://api.datamuse.com",
    timeout=1.0,
)


class DatamuseApiClient:
    """API client for Datamuse.

    https://www.datamuse.com/api/
    """

    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        conf: DatamuseApiConf = DEFAULT_API_CONF,
    ) -> None:
        self.client = client
        self.conf = conf
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
    ) -> AsyncGenerator[Suggestion, None]:
        """Yield Suggestion objects. for the provided value."""
        try:
            max = DatamuseEndpoint.Max(value=limit)
        except ValueError:
            max = DatamuseEndpoint.Max()

        endpoint = SuggestionsEndpoint(
            s=SuggestionsEndpoint.Prefix(value=value),
            max=max,
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
    ) -> AsyncGenerator[Word, None]:
        """Yield Word objects. for the provided 'likes'."""
        try:
            max = DatamuseEndpoint.Max(value=limit)
        except ValueError:
            max = DatamuseEndpoint.Max()

        params: WordsEndpoint.ParamsType = {
            "ml": WordsEndpoint.MeansLike(value=means_like.strip().lower()),
            "sl": WordsEndpoint.SoundsLike(value=sounds_like.strip().lower()),
            "sp": WordsEndpoint.SpelledLike(value=spelled_like.strip().lower()),
        }

        endpoint = WordsEndpoint(max=max, **params)

        resp = await self._request(endpoint=endpoint)

        for data in resp.json():
            yield self.transformer.word(data)
