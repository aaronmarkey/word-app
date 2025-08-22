from dataclasses import dataclass


@dataclass
class DatamuseModel:
    """Base class for Datamuse API objects."""

    word: str
    score: int


@dataclass
class Suggestion(DatamuseModel):
    """Object representation from /sug responses."""

    pass


@dataclass
class Word(DatamuseModel):
    """Object representation from /words responses."""

    pass
