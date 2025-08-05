from collections import defaultdict

from pydantic import BaseModel

from word_app.data.grammar import Grammar


class WordDetail(BaseModel):
    attribution: str = ""
    type: Grammar
    text: str


class WordDetailContainer(BaseModel):
    source: str = ""

    @property
    def has_value(self) -> bool:
        return False

    @property
    def by_type(self) -> dict[Grammar, list[WordDetail]]:
        return {}


class Definition(WordDetail):
    pass


class Definitions(WordDetailContainer):
    definitions: list[Definition] = []

    @property
    def has_value(self) -> bool:
        return bool(self.definitions)

    @property
    def by_type(self) -> dict[Grammar, list[WordDetail]]:
        defs: dict[Grammar, list[WordDetail]] = defaultdict(list)

        for d in self.definitions:
            defs[d.type].append(d)

        return dict(defs)


class Nym(WordDetail):
    pass


class Thesaurus(WordDetailContainer):
    nyms: list[Nym] = []

    @property
    def has_value(self) -> bool:
        return bool(self.nyms)

    @property
    def by_type(self) -> dict[Grammar, list[WordDetail]]:
        nyms: dict[Grammar, list[WordDetail]] = defaultdict(list)

        for n in self.nyms:
            nyms[n.type].append(n)

        return dict(nyms)


class Word(BaseModel):
    word: str

    definitions: Definitions = Definitions()
    thesaurus: Thesaurus = Thesaurus()
