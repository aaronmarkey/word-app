from __future__ import annotations

from typing import Self

from word_app.lib.datamuse.models import Suggestion, Word


class DatamuseTransformer:
    """Transform Datamuse API responses to Datamuse models."""

    _UNKNOWN_STR: str = "__UNKNOWN__"
    _UNKNOWN_INT: int = -1

    def suggestion(self: Self, data: dict) -> Suggestion:
        """Suggestion from API response data."""
        return Suggestion(
            word=data.get("word", self._UNKNOWN_STR),
            score=data.get("score", self._UNKNOWN_INT),
        )

    def word(self: Self, data: dict) -> Word:
        """Word from API response data."""
        return Word(
            word=data.get("word", self._UNKNOWN_STR),
            score=data.get("score", self._UNKNOWN_INT),
        )
