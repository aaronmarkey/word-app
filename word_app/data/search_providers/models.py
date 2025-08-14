from enum import StrEnum


class SearchSuggestionType(StrEnum):
    SUGGESTION = "autocomplete"
    SOUNDS_LIKE = "sounds-like"
    MEANS_LIKE = "means-like"

    @property
    def display(self) -> str:
        return self.capitalize()
