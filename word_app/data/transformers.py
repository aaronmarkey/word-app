from typing import ClassVar

from word_app.data import grammar
from word_app.data.models import Definition, Nym
from word_app.lib.wordnik.models import Definition as WnDefinition
from word_app.lib.wordnik.models import PartOfSpeech, RelationshipType
from word_app.lib.wordnik.models import Related as WnRelated


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
    _RT_TO_GRAMMAR: ClassVar[dict[RelationshipType, grammar.Grammar]] = {
        RelationshipType.SYNONYM: grammar.Synonym,
        RelationshipType.ANTONYM: grammar.Antonym,
        RelationshipType.VARIANT: grammar.Variant,
        RelationshipType.EQUIVALENT: grammar.Equivalent,
        RelationshipType.CROSS_REFERENCE: grammar.CrossReference,
        RelationshipType.RELATED_WORD: grammar.RelatedWord,
        RelationshipType.RHYME: grammar.Rhyme,
        RelationshipType.FORM: grammar.Form,
        RelationshipType.ETYMOLOGLYCALY_RELATED_TERM: grammar.EtmologicallyRelatedTerm,
        RelationshipType.HYPERNYM: grammar.Hypernym,
        RelationshipType.HYPONYM: grammar.Hyponym,
        RelationshipType.INFLECTED_FORM: grammar.InflectedForm,
        RelationshipType.PRIMARY: grammar.Primary,
        RelationshipType.SAME_CONTEXT: grammar.SameContext,
        RelationshipType.VERB_FORM: grammar.VerbForm,
        RelationshipType.VERB_STEM: grammar.VerbStem,
        RelationshipType.HAS_TOPIC: grammar.HasTopic,
    }

    def defintion(self, inp: WnDefinition) -> Definition:
        g = self._POS_TO_GRAMMER.get(inp.partOfSpeech, grammar.Miscellaneous)
        return Definition(
            attribution=inp.attributionText or "", type=g, text=inp.text
        )

    def thesaurus(self, inp: WnRelated) -> list[Nym]:
        return [
            Nym(
                attribution="",
                type=self._RT_TO_GRAMMAR.get(
                    inp.relationshipType, grammar.Miscellaneous
                ),
                text=w,
            )
            for w in inp.words
        ]
