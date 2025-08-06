from collections import defaultdict

from pydantic import BaseModel

from word_app.data.grammar import Grammar, Nothing


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


class WordDetailContainer(BaseModel):
    source: str = ""

    @property
    def _details(self) -> list[WordDetail]:
        return []

    @property
    def has_value(self) -> bool:
        return bool(self._details)

    @property
    def by_type(self) -> dict[Grammar, list[WordDetail]]:
        values: dict[Grammar, list[WordDetail]] = defaultdict(list)

        for detail in self._details:
            values[detail.type].append(detail)

        return dict(values)


class Definitions(WordDetailContainer):
    definitions: list[Definition] = []

    @property
    def _details(self) -> list[WordDetail]:
        return self.definitions


class Etymologies(WordDetailContainer):
    etymologies: list[Etymology] = []

    @property
    def _details(self) -> list[WordDetail]:
        return self.etymologies


class Examples(WordDetailContainer):
    examples: list[Example] = []

    @property
    def _details(self) -> list[WordDetail]:
        return self.examples


class FrequencyGraph(BaseModel):
    intervals: list[FrequencyInterval] = []

    @property
    def has_value(self) -> bool:
        return bool(self.intervals)

    @property
    def in_order(self) -> list[FrequencyInterval]:
        return sorted(self.intervals, key=lambda x: x.start)


class Phrases(WordDetailContainer):
    phrases: list[Phrase] = []

    @property
    def _details(self) -> list[WordDetail]:
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


class Thesaurus(WordDetailContainer):
    nyms: list[Nym] = []

    @property
    def _details(self) -> list[WordDetail]:
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
