from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncGenerator

import httpx

from word_app.lib.datamuse.models import Suggestion, Word


def _error(name: str, value: str) -> None:
    raise ValueError(
        f"Invalid value of '{value} for Datamuse configration '{name}'."
    )


@dataclass(frozen=True, eq=True)
class LimitContainer:
    default: int
    max: int
    min: int

    def _validate(self, name: str, value: int) -> None:
        if not (self.min <= value and value <= self.max):
            _error(name, str(value))

    def validate(self) -> None:
        self._validate("default", self.default)

    def validate_limit(self, limit: int) -> None:
        self._validate("limit", limit)


@dataclass(frozen=True, eq=True)
class LocationContainer:
    root: str
    endpoint_suggest: str
    endpoint_words: str

    def validate(self) -> None:
        for name, value in [
            ("root", self.root),
            ("endpoint_suggest", self.endpoint_suggest),
            ("endpoint_words", self.endpoint_words),
        ]:
            if not value.strip():
                _error(name, value)

    def full_path(self, endpoint: str) -> str:
        endpoint = getattr(self, f"endpoint_{endpoint}")
        return f"{self.root}/{endpoint}"


@dataclass(frozen=True, eq=True)
class DatamuseClientParamsContainer:
    limit: LimitContainer
    location: LocationContainer
    timeout: float | None

    def _validate_timeout(self) -> None:
        if to := self.timeout:
            if to < 0.0:
                _error("timeout", str(to))

    def validate(self) -> None:
        self.limit.validate()
        self.location.validate()
        self._validate_timeout()


DatamuseClientParams = DatamuseClientParamsContainer(
    limit=LimitContainer(max=100, min=1, default=100),
    location=LocationContainer(
        root="https://api.datamuse.com",
        endpoint_suggest="sug",
        endpoint_words="words",
    ),
    timeout=1.0,
)


class DatamuseTransformer:
    _UNKNOWN_STR: str = "__UNKNOWN__"
    _UNKNOWN_INT: int = -1

    @classmethod
    def suggestion(cls: type[DatamuseTransformer], data: dict) -> Suggestion:
        return Suggestion(
            word=data.get("word", cls._UNKNOWN_STR),
            score=data.get("score", cls._UNKNOWN_INT),
        )

    @classmethod
    def word(cls: type[DatamuseTransformer], data: dict) -> Word:
        return Word(
            word=data.get("word", cls._UNKNOWN_STR),
            score=data.get("score", cls._UNKNOWN_INT),
        )


class DatamuseClient:
    def __init__(
        self,
        *,
        aclient: httpx.AsyncClient | None = None,
        client: httpx.Client | None = None,
        params: DatamuseClientParamsContainer = DatamuseClientParams,
        transformer_cls: type[DatamuseTransformer] = DatamuseTransformer,
    ) -> None:
        params.validate()
        self.params = params
        self.aclient = aclient or httpx.AsyncClient()
        self.client = client or httpx.Client()
        self.transformer_cls = transformer_cls

    async def aclean(self) -> None:
        self.clean()
        await self.aclient.aclose()

    def clean(self) -> None:
        self.client.close()

    async def aget_suggestions(
        self, value: str, *, limit: int = 0
    ) -> AsyncGenerator[Suggestion]:
        if limit > 0:
            self.params.limit.validate_limit(limit)
        else:
            limit = self.params.limit.default
        params: dict[str, str | int] = {"s": value, "max": limit}
        location = self.params.location.full_path("suggest")

        resp = await self.aclient.get(
            location, params=params, timeout=self.params.timeout
        )
        for data in resp.json():
            yield self.transformer_cls.suggestion(data)

    async def aget_words(
        self, *, means_like: str = "", limit: int = 0
    ) -> AsyncGenerator[Word]:
        if limit > 0:
            self.params.limit.validate_limit(limit)
        else:
            limit = self.params.limit.default

        location = self.params.location.full_path("words")
        arg_map = {"ml": means_like}
        params: dict[str, str | int] = {"max": limit}
        for name, value in arg_map.items():
            if v := value.strip().lower():
                params[name] = v

        resp = await self.aclient.get(
            location, params=params, timeout=self.params.timeout
        )
        for data in resp.json():
            yield self.transformer_cls.word(data)
