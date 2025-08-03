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


class Nym(WordDetail):
    type: str
    text: str


class Thesaurus(WordDetailContainer):
    nyms: list[Nym] = []

    @property
    def has_value(self) -> bool:
        return bool(self.nyms)

    @property
    def by_type(self) -> dict[str, list[Nym]]:
        nyms: dict[str, list[Nym]] = defaultdict(list)

        for n in self.nyms:
            nyms[n.type.lower()].append(n)

        return dict(nyms)


class Phrase(WordDetail):
    tokens: list[str]

    def __str__(self):
        return " ".join(self.tokens)


class Word(BaseModel):
    word: str

    definitions: Definitions = Definitions()
    phrases: list[Phrase] = []
    thesaurus: Thesaurus = Thesaurus()
