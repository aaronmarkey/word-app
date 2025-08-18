from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, eq=True)
class SourceDictionary:
    api_value: str
    title: str

    def __str__(self) -> str:
        return self.api_value

    def __repr__(self) -> str:
        return str(self)


AmericanHeritage = SourceDictionary(
    api_value="ahd-5",
    title=(
        "The American Heritage® Dictionary of the English Language, 5th Edition"
    ),
)


class PartOfSpeech(StrEnum):
    NOUN = "noun"
    ADJECTIVE = "adjective"
    VERB = "verb"
    INTERJECTION = "interjection"
    PRONOUN = "pronoun"
    PREPOSITION = "preposition"
    ABBREVIATION = "abbreviation"
    AFFIX = "affix"
    ARTICLE = "article"
    AUXILIARY_VERB = "auxiliary-verb"
    CONJUNCTION = "conjunction"
    DEFINITE_ARTICLE = "definite-article"
    FAMILY_NAME = "family-name"
    GIVEN_NAME = "given-name"
    IDIOM = "idiom"
    IMPERATIVE = "imperative"
    NOUN_PLURAL = "noun-plural"
    NOUN_POSSESSIVE = "noun-posessive"
    PAST_PARTICIPLE = "past-participle"
    PHRASAL_PREFIX = "phrasal-prefix"
    PROPER_NOUN = "proper-noun"
    PROPER_NOUN_PLURAL = "proper-noun-plural"
    PROPER_NOUN_POSSESSIVE = "proper-noun-posessive"
    SUFFIX = "suffix"
    VERB_INTRANSITIVE = "verb-intransitive"
    VERB_TRANSITIVE = "verb-transitive"
