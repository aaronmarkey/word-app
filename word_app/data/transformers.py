from typing import ClassVar

from word_app.data import grammar
from word_app.data.models import Definition
from word_app.lib.wordnik.models import Definition as WnDefinition
from word_app.lib.wordnik.models import PartOfSpeech


class WnToWaTransformer:
    _POS_TO_GRAMMER: ClassVar[dict[PartOfSpeech, grammar.Grammar]] = {
        PartOfSpeech.NOUN: grammar.Noun,
        PartOfSpeech.ADJECTIVE: grammar.Adjective,
        PartOfSpeech.VERB: grammar.Verb,
        PartOfSpeech.INTERJECTION: grammar.Interjection,
        PartOfSpeech.PRONOUN: grammar.Pronoun,
        PartOfSpeech.PREPOSITION: grammar.Preposition,
        PartOfSpeech.ABBREVIATION: grammar.Abbreviation,
        PartOfSpeech.AFFIX: grammar.Affix,
        PartOfSpeech.ARTICLE: grammar.Article,
        PartOfSpeech.AUXILIARY_VERB: grammar.AuxiliaryVerb,
        PartOfSpeech.CONJUNCTION: grammar.Conjunction,
        PartOfSpeech.DEFINITE_ARTICLE: grammar.DefiniteArticle,
        PartOfSpeech.FAMILY_NAME: grammar.FamilyName,
        PartOfSpeech.GIVEN_NAME: grammar.GivenName,
        PartOfSpeech.IDIOM: grammar.Idiom,
        PartOfSpeech.IMPERATIVE: grammar.Imperative,
        PartOfSpeech.NOUN_PLURAL: grammar.NounPlural,
        PartOfSpeech.NOUN_POSSESSIVE: grammar.NounPosessive,
        PartOfSpeech.PAST_PARTICIPLE: grammar.PastParticiple,
        PartOfSpeech.PHRASAL_PREFIX: grammar.PhrasalPrefix,
        PartOfSpeech.PROPER_NOUN: grammar.ProperNoun,
        PartOfSpeech.PROPER_NOUN_PLURAL: grammar.ProperNounPlural,
        PartOfSpeech.PROPER_NOUN_POSSESSIVE: grammar.ProperNounPosessive,
        PartOfSpeech.SUFFIX: grammar.Suffix,
        PartOfSpeech.VERB_INTRANSITIVE: grammar.VerbIntransitive,
        PartOfSpeech.VERB_TRANSITIVE: grammar.VerbTransitive,
    }

    def defintion(self, inp: WnDefinition) -> Definition:
        g = self._POS_TO_GRAMMER.get(inp.partOfSpeech, grammar.Miscellaneous)
        return Definition(
            attribution=inp.attributionText or "", type=g, text=inp.text
        )
