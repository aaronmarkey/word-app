from copy import deepcopy
from typing import Any

import httpx

from word_app.lib.wordnik.conf import WordnikApiConf, WordnikEndpoint
from word_app.lib.wordnik.exceptions import FailedToRefetchResult


class WordnikApiClient:
    def __init__(
        self, *, conf: WordnikApiConf, client: httpx.AsyncClient | None = None
    ) -> None:
        self.conf = conf
        self.client = client or httpx.AsyncClient()
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
        except (httpx.RequestError, httpx.HTTPError) as exc:
            raise FailedToRefetchResult() from exc

    async def clean(self) -> None:
        """Clean up operations after done."""
        await self.client.aclose()
