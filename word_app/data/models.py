from collections import defaultdict

from pydantic import BaseModel


class WordDetail(BaseModel):
    attribution: str = ""
    type: str
    text: str


class WordDetailContainer(BaseModel):
    source: str = ""

    @property
    def has_value(self) -> bool:
        return False

    @property
    def by_type(self) -> dict[str, list[WordDetail]]:
        return {}


class Definition(WordDetail):
    pass


class Definitions(WordDetailContainer):
    definitions: list[Definition] = []

    @property
    def has_value(self) -> bool:
        return bool(self.definitions)

    @property
    def by_type(self) -> dict[str, list[WordDetail]]:
        defs: dict[str, list[WordDetail]] = defaultdict(list)

        for d in self.definitions:
            defs[d.type.lower()].append(d)

        return dict(defs)


class Nym(WordDetail):
    pass


class Thesaurus(WordDetailContainer):
    nyms: list[Nym] = []

    @property
    def has_value(self) -> bool:
        return bool(self.nyms)

    @property
    def by_type(self) -> dict[str, list[WordDetail]]:
        nyms: dict[str, list[WordDetail]] = defaultdict(list)

        for n in self.nyms:
            nyms[n.type.lower()].append(n)

        return dict(nyms)


# class Phrase(WordDetail):
#     tokens: list[str]

#     def __str__(self):
#         return " ".join(self.tokens)


class Word(BaseModel):
    word: str

    definitions: Definitions = Definitions()
    # phrases: list[Phrase] = []
    thesaurus: Thesaurus = Thesaurus()
