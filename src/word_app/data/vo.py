"""Value objects. Objects which hold constants."""

from copy import deepcopy
from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum, auto

from word_app.lex import LEX


@dataclass(frozen=True, eq=True)
class DataSource:
    class Authentication(IntEnum):
        NONE = 0
        BASIC = 1

    id: str
    label_description: str
    label_name: str
    authentication: Authentication


@dataclass(frozen=True, eq=True)
class Grammar:
    title: str

    @property
    def title_display(self) -> str:
        return self.title.title()


class SearchResultType(StrEnum):
    SPELLED_LIKE = "spelled-like"
    SOUNDS_LIKE = "sounds-like"
    MEANS_LIKE = "means-like"
    SUGGESTION = "autocomplete"

    @property
    def display(self) -> str:
        return self.capitalize()


class SearchTermType(Enum):
    SPELLED_LIKE = auto()
    SUGGEST_SOUNDS_LIKE = auto()
    SUGGEST_MEANS_LIKE = auto()
    UNKNOWN = auto()


Abbreviation = Grammar(title="abbreviation")
Adjective = Grammar(title="adjective")
Affix = Grammar(title="affix")
Article = Grammar(title="article")
AuxiliaryVerb = Grammar(title="auxiliary verb")
Conjunction = Grammar(title="conjunction")
DefiniteArticle = Grammar(title="definite article")
FamilyName = Grammar(title="family name")
GivenName = Grammar(title="given name")
Idiom = Grammar(title="idiom")
Imperative = Grammar(title="imperative")
Interjection = Grammar(title="interjection")
Noun = Grammar(title="noun")
NounPlural = Grammar(title="noun plural")
NounPosessive = Grammar(title="noun posessive")
PastParticiple = Grammar(title="past participle")
PhrasalPrefix = Grammar(title="phrasal prefix")
Preposition = Grammar(title="preposition")
Pronoun = Grammar(title="pronoun")
ProperNoun = Grammar(title="proper noun")
ProperNounPlural = Grammar(title="proper noun plural")
ProperNounPosessive = Grammar(title="proper noun posessive")
Suffix = Grammar(title="suffix")
Verb = Grammar(title="verb")
VerbIntransitive = Grammar(title="verb intransitive")
VerbTransitive = Grammar(title="verb transitive")

Antonym = Grammar(title="antonym")
CrossReference = Grammar(title="cross reference")
Equivalent = Grammar(title="equivalent")
EtmologicallyRelatedTerm = Grammar(title="etymologically related term")
Form = Grammar(title="form")
HasTopic = Grammar(title="has topic")
Hypernym = Grammar(title="hypernym")
Hyponym = Grammar(title="hyponym")
InflectedForm = Grammar(title="inflected form")
Primary = Grammar(title="primary")
RelatedWord = Grammar(title="related word")
Rhyme = Grammar(title="rhyme")
SameContext = Grammar(title="same context")
Synonym = Grammar(title="synonym")
Variant = Grammar(title="variant")
VerbForm = Grammar(title="verb form")
VerbStem = Grammar(title="verb stem")

Miscellaneous = Grammar(title="miscellaneous")
Nothing = Grammar(title="nothing")
Sentence = Grammar(title="sentence")

DataMuseDataSource = DataSource(
    id="datamuse",
    label_description=LEX.service.datamuse.desc,
    label_name=LEX.service.datamuse.name,
    authentication=DataSource.Authentication.NONE,
)

WordnikDataSource = DataSource(
    id="wordnik",
    label_description=LEX.service.worknik.desc,
    label_name=LEX.service.worknik.name,
    authentication=DataSource.Authentication.BASIC,
)

DICTIONARY_GRAMMARS = [
    Abbreviation,
    Adjective,
    Affix,
    Article,
    AuxiliaryVerb,
    Conjunction,
    DefiniteArticle,
    FamilyName,
    GivenName,
    Idiom,
    Imperative,
    Interjection,
    Miscellaneous,
    Nothing,
    Noun,
    NounPlural,
    NounPosessive,
    PastParticiple,
    PhrasalPrefix,
    Preposition,
    Pronoun,
    ProperNoun,
    ProperNounPlural,
    ProperNounPosessive,
    Sentence,
    Suffix,
    Verb,
    VerbIntransitive,
    VerbTransitive,
]

THESAURUS_GRAMMARS = [
    Antonym,
    CrossReference,
    Equivalent,
    EtmologicallyRelatedTerm,
    Form,
    HasTopic,
    Hypernym,
    Hyponym,
    InflectedForm,
    Primary,
    RelatedWord,
    Rhyme,
    SameContext,
    Synonym,
    Variant,
    VerbForm,
    VerbStem,
]

ALL_GRAMMARS = [
    *DICTIONARY_GRAMMARS,
    *THESAURUS_GRAMMARS,
]

_AVAILABLE_DATA_SOURCES = [DataMuseDataSource, WordnikDataSource]


def get_available_data_sources(
    sources: list[DataSource] = _AVAILABLE_DATA_SOURCES,
) -> list[DataSource]:
    return deepcopy(sources)
