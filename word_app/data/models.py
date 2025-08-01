from collections import defaultdict

from pydantic import BaseModel


class WordDetail(BaseModel):
    attribution: str = ""


class WordDetailContainer(BaseModel):
    @property
    def has_value(self) -> bool:
        return False


class Definition(WordDetail):
    part_of_speech: str
    text: str


class Definitions(WordDetailContainer):
    definitions: list[Definition] = []

    @property
    def has_value(self) -> bool:
        return bool(self.definitions)

    @property
    def by_part_of_speech(self) -> dict[str, list[Definition]]:
        defs: dict[str, list[Definition]] = defaultdict(list)

        for d in self.definitions:
            defs[d.part_of_speech.lower()].append(d)

        return dict(defs)


class Thesaurus(WordDetailContainer):
    pass

    @property
    def has_data(self) -> bool:
        return False


class Phrase(WordDetail):
    tokens: list[str]

    def __str__(self):
        return " ".join(self.tokens)


class Word(BaseModel):
    word: str

    definitions: Definitions = Definitions()
    phrases: list[Phrase] = []
    thesaurus: Thesaurus = Thesaurus()
