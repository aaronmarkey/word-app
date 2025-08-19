from collections import defaultdict
from typing import Generic, TypeVar

from pydantic import BaseModel

from word_app.data.grammar import Grammar, Nothing

WordDetailType = TypeVar("WordDetailType", bound="WordDetail")


class WordDetail(BaseModel):
    attribution: str = ""
    type: Grammar
    text: str


class Definition(WordDetail):
    pass


class Etymology(WordDetail):
    type: Grammar = Nothing


class Example(WordDetail):
    pass


class FrequencyInterval(BaseModel):
    start: int
    end: int
    value: float

    def as_percentage(self, denominator: float) -> float:
        return round(self.value / denominator, 4)


class Nym(WordDetail):
    pass


class Phrase(WordDetail):
    pass


class Syllable(BaseModel):
    text: str


class WordDetailContainer(BaseModel, Generic[WordDetailType]):
    source: str = ""

    @property
    def _details(self) -> list[WordDetailType]:
        return []

    @property
    def details(self) -> list[WordDetailType]:
        return self._details

    @property
    def has_value(self) -> bool:
        return bool(self._details)

    @property
    def by_type(self) -> dict[Grammar, list[WordDetailType]]:
        values: dict[Grammar, list[WordDetailType]] = defaultdict(list)

        for detail in self._details:
            values[detail.type].append(detail)

        return dict(values)


class Definitions(WordDetailContainer[Definition]):
    definitions: list[Definition] = []

    @property
    def _details(self) -> list[Definition]:
        return self.definitions


class Etymologies(WordDetailContainer[Etymology]):
    etymologies: list[Etymology] = []

    @property
    def _details(self) -> list[Etymology]:
        return self.etymologies


class Examples(WordDetailContainer[Example]):
    examples: list[Example] = []

    @property
    def _details(self) -> list[Example]:
        return self.examples


class FrequencyGraph(BaseModel):
    intervals: list[FrequencyInterval] = []

    @property
    def has_value(self) -> bool:
        return bool(self.intervals)

    @property
    def in_order(self) -> list[FrequencyInterval]:
        return sorted(self.intervals, key=lambda x: x.start)


class Phrases(WordDetailContainer[Phrase]):
    phrases: list[Phrase] = []

    @property
    def _details(self) -> list[Phrase]:
        return self.phrases


class Syllables(BaseModel):
    source: str = ""
    syllables: list[Syllable] = []

    @property
    def has_value(self) -> bool:
        return bool(self.syllables)

    @property
    def as_string(self) -> str:
        return (
            "-".join(syllable.text for syllable in self.syllables)
            if len(self.syllables) > 1
            else self.syllables[0].text
        )


class Thesaurus(WordDetailContainer[Nym]):
    nyms: list[Nym] = []

    @property
    def _details(self) -> list[Nym]:
        return self.nyms


class Word(BaseModel):
    word: str

    definitions: Definitions = Definitions()
    etymologies: Etymologies = Etymologies()
    examples: Examples = Examples()
    frequency_graph: FrequencyGraph = FrequencyGraph()
    phrases: Phrases = Phrases()
    syllables: Syllables = Syllables()
    thesaurus: Thesaurus = Thesaurus()
