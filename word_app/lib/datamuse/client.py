from __future__ import annotations

from copy import deepcopy
from typing import AsyncGenerator

import httpx

from word_app.lib.datamuse.conf import (
    DatamuseClientParamsContainer,
    DatamuseClientParams,
)
from word_app.lib.datamuse.exceptions import FailedToRefetchResult
from word_app.lib.datamuse.models import Suggestion, Word
from word_app.lib.datamuse.transformer import DatamuseTransformer


class DatamuseApiClient:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        params: DatamuseClientParamsContainer = DatamuseClientParams,
        transformer_cls: type[DatamuseTransformer] = DatamuseTransformer,
    ) -> None:
        params.validate()
        self.params = params
        self.client = client or httpx.AsyncClient()
        self.transformer_cls = transformer_cls

    async def _request(
        self, *, endpoint: str, params: dict = dict(), limit: int = 0
    ) -> httpx.Response:
        iparams = deepcopy(params)

        if limit > 0:
            self.params.limit.validate_limit(limit)
        else:
            limit = self.params.limit.default
        location = self.params.location.full_path(endpoint)

        iparams["max"] = limit

        kwargs: dict[str, float | dict | None] = {
            "timeout": self.params.timeout
        }
        if params:
            kwargs["params"] = params

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
        await self.client.aclose()

    async def get_suggestions(
        self, value: str, *, limit: int = 0
    ) -> AsyncGenerator[Suggestion]:
        resp = await self._request(
            endpoint="suggest",
            params={"s": value},
            limit=limit,
        )

        for data in resp.json():
            yield self.transformer_cls.suggestion(data)

    async def get_words(
        self,
        *,
        means_like: str = "",
        spelled_like: str = "",
        sounds_like: str = "",
        limit: int = 0,
    ) -> AsyncGenerator[Word]:
        arg_map = {"ml": means_like, "sl": sounds_like, "sp": spelled_like}
        params: dict[str, str | int] = {}
        for name, value in arg_map.items():
            if v := value.strip().lower():
                params[name] = v

        resp = await self._request(
            endpoint="words",
            params=params,
            limit=limit,
        )

        for data in resp.json():
            yield self.transformer_cls.word(data)
