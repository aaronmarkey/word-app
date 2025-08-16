from enum import StrEnum


class SearchSuggestionType(StrEnum):
    SPELLED_LIKE = "spelled-like"
    SOUNDS_LIKE = "sounds-like"
    MEANS_LIKE = "means-like"
    SUGGESTION = "autocomplete"

    @property
    def display(self) -> str:
        return self.capitalize()
