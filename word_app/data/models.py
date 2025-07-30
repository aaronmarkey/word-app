from pydantic import BaseModel


class Definition(BaseModel):
    attribution: str = ""
    part_of_speech: str
    text: str


class Phrase(BaseModel):
    tokens: list[str]

    def __str__(self):
        return " ".join(self.tokens)


class Word(BaseModel):
    word: str

    definitions: list[Definition] = []
    phrases: list[Phrase] = []
