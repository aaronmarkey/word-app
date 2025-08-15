from dataclasses import dataclass


@dataclass
class DatamuseModel:
    word: str
    score: int


@dataclass
class Suggestion(DatamuseModel):
    pass


@dataclass
class Word(DatamuseModel):
    pass
