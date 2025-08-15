from abc import ABC, abstractmethod

from word_app.data.models import Word


class AbstractWordProvider(ABC):
    @abstractmethod
    def get_word_details(self, word: str) -> Word:
        pass
