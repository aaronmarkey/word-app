from abc import ABC, abstractmethod
from typing import Callable

from word_app.data.models import Word


class AbstractWordDetailProvider(ABC):
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    async def get_details_for_word(
        self, word: str, on_failure: Callable[[Exception], None] | None = None
    ) -> Word | None:
        pass
