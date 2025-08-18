import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from word_app.data.search_providers.models import SearchTermType


@dataclass(frozen=True, eq=True)
class ParseResult:
    type: SearchTermType
    text: str


class AbstractSearchTermParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> ParseResult:
        pass


class RegexSearchTermParser(AbstractSearchTermParser):
    _TYPE_REGEX_MAP: dict[SearchTermType, re.Pattern] = {
        SearchTermType.SPELLED_LIKE: re.compile(r"[?*]+"),
        SearchTermType.SUGGEST_SOUNDS_LIKE: re.compile(r"^[a-z0-9]+$"),
        SearchTermType.SUGGEST_MEANS_LIKE: re.compile(r"^[a-z0-9\s\-]+$"),
    }

    def parse(self, text: str) -> ParseResult:
        text = text.lower()
        for type, pattern in self._TYPE_REGEX_MAP.items():
            if _ := pattern.search(text):
                return ParseResult(type=type, text=text)
        return ParseResult(type=SearchTermType.UNKNOWN, text=text)
