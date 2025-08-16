from __future__ import annotations

from word_app.lib.datamuse.models import Suggestion, Word


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
