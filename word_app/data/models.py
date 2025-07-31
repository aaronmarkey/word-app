from pydantic import BaseModel


class WordDetail(BaseModel):
    pass


class Definition(WordDetail):
    attribution: str = ""
    part_of_speech: str
    text: str


class Thesaurus(WordDetail):
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

    definitions: list[Definition] = []
    phrases: list[Phrase] = []
    thesaurus: Thesaurus = Thesaurus()
