from abc import ABC, abstractmethod

from word_app.data.models import Definitions, Thesaurus


class BaseDataService(ABC):
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def get_word_definitions(self, word, **kwargs) -> Definitions:
        pass

    @abstractmethod
    def get_word_thesaurus(self, word, **kwargs) -> Thesaurus:
        pass
