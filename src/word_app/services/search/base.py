from abc import ABC, abstractmethod
from dataclasses import dataclass

from word_app.data.vo import SearchTermType


@dataclass(frozen=True, eq=True)
class ParseResult:
    type: SearchTermType
    text: str


class AbstractSearchTermParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> ParseResult:
        pass
