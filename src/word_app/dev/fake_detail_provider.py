from typing import Callable

from faker import Faker

from word_app.data.models import Word
from word_app.dev.fake import WordFactory
from word_app.services.wdp.base import AbstractWordDetailProvider


class FakeDetailProvider(AbstractWordDetailProvider):
    def __init__(self, *_, **kwargs) -> None:
        if fake := kwargs.get("faker", None):
            self._fake: Faker = fake
        else:
            raise ValueError("Missing faker kwargs to FakeDetailProvider.")
        self._word_factory_cls = WordFactory

    async def get_details_for_word(
        self, word: str, on_failure: Callable[[Exception], None] | None = None
    ) -> Word:
        word = word.strip() or self._fake.word()
        return self._word_factory_cls(word=word)  # type: ignore
