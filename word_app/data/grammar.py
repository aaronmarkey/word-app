from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class Grammar:
    title: str

    @property
    def title_display(self) -> str:
        return self.title.title()


Noun = Grammar(title="noun")
Adjective = Grammar(title="adjective")
Verb = Grammar(title="verb")
Interjection = Grammar(title="interjection")
Pronoun = Grammar(title="pronoun")
Preposition = Grammar(title="preposition")
Abbreviation = Grammar(title="abbreviation")
Affix = Grammar(title="affix")
Article = Grammar(title="article")
AuxiliaryVerb = Grammar(title="auxiliary verb")
Conjunction = Grammar(title="conjunction")
DefiniteArticle = Grammar(title="definite article")
FamilyName = Grammar(title="family name")
GivenName = Grammar(title="given name")
Idiom = Grammar(title="idiom")
Imperative = Grammar(title="imperative")
NounPlural = Grammar(title="noun plural")
NounPosessive = Grammar(title="noun posessive")
PastParticiple = Grammar(title="past participle")
PhrasalPrefix = Grammar(title="phrasal prefix")
ProperNoun = Grammar(title="proper noun")
ProperNounPlural = Grammar(title="proper noun plural")
ProperNounPosessive = Grammar(title="proper noun posessive")
Suffix = Grammar(title="suffix")
VerbIntransitive = Grammar(title="verb intransitive")
VerbTransitive = Grammar(title="verb transitive")

Miscellaneous = Grammar(title="miscellaneous")
Nothing = Grammar(title="nothing")

Synonym = Grammar(title="synonym")
Antonym = Grammar(title="antonym")
Variant = Grammar(title="variant")
Equivalent = Grammar(title="equivalent")
CrossReference = Grammar(title="cross reference")
RelatedWord = Grammar(title="related word")
Rhyme = Grammar(title="rhyme")
Form = Grammar(title="form")
EtmologicallyRelatedTerm = Grammar(title="etymologically related term")
Hypernym = Grammar(title="hypernym")
Hyponym = Grammar(title="hyponym")
InflectedForm = Grammar(title="inflected form")
Primary = Grammar(title="primary")
SameContext = Grammar(title="same context")
VerbForm = Grammar(title="verb form")
VerbStem = Grammar(title="verb stem")
HasTopic = Grammar(title="has topic")


DICTIONARY_GRAMMARS = [
    Noun,
    Adjective,
    Verb,
    Interjection,
    Pronoun,
    Preposition,
    Abbreviation,
    Affix,
    Article,
    AuxiliaryVerb,
    Conjunction,
    DefiniteArticle,
    FamilyName,
    GivenName,
    Idiom,
    Imperative,
    NounPlural,
    NounPosessive,
    PastParticiple,
    PhrasalPrefix,
    ProperNoun,
    ProperNounPlural,
    ProperNounPosessive,
    Suffix,
    VerbIntransitive,
    VerbTransitive,
    Miscellaneous,
    Nothing,
]

THESAURUS_GRAMMARS = [
    Synonym,
    Antonym,
    Variant,
    Equivalent,
    CrossReference,
    RelatedWord,
    Rhyme,
    Form,
    EtmologicallyRelatedTerm,
    Hypernym,
    Hyponym,
    InflectedForm,
    Primary,
    SameContext,
    VerbForm,
    VerbStem,
    HasTopic,
]

ALL_GRAMMARS = [
    *DICTIONARY_GRAMMARS,
    *THESAURUS_GRAMMARS,
]
