from enum import Enum, StrEnum, auto


class SearchResultType(StrEnum):
    SPELLED_LIKE = "spelled-like"
    SOUNDS_LIKE = "sounds-like"
    MEANS_LIKE = "means-like"
    SUGGESTION = "autocomplete"

    @property
    def display(self) -> str:
        return self.capitalize()


class SearchTermType(Enum):
    SPELLED_LIKE = auto()
    SUGGEST_SOUNDS_LIKE = auto()
    SUGGEST_MEANS_LIKE = auto()
    UNKNOWN = auto()
