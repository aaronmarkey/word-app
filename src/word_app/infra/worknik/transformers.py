from typing import ClassVar

from markdown_it import MarkdownIt

from word_app.app.tui.utils import HtmlToMarkup
from word_app.data import vo
from word_app.data.models import Definition as WaDefintion
from word_app.data.models import Example as WaExample
from word_app.data.models import Nym as WaNym
from word_app.data.models import Phrase as WaPhrase
from word_app.data.models import Syllable as WaSyllable
from word_app.lib.wordnik.models import Bigram as WnBigram
from word_app.lib.wordnik.models import Definition as WnDefinition
from word_app.lib.wordnik.models import Example as WnExample
from word_app.lib.wordnik.models import Related as WnRelated
from word_app.lib.wordnik.models import Syllable as WnSyllable
from word_app.lib.wordnik.vo import PartOfSpeech, RelationshipType


class WnToWaTransformer:
    _HTML_TO_MARKUP: ClassVar[HtmlToMarkup] = HtmlToMarkup()
    _MARKDOWN: ClassVar[MarkdownIt] = MarkdownIt(
        "commonmark", {"breaks": False, "html": True}
    )
    _POS_TO_GRAMMER: ClassVar[dict[PartOfSpeech, vo.Grammar]] = {
        PartOfSpeech.NOUN: vo.Noun,
        PartOfSpeech.ADJECTIVE: vo.Adjective,
        PartOfSpeech.VERB: vo.Verb,
        PartOfSpeech.INTERJECTION: vo.Interjection,
        PartOfSpeech.PRONOUN: vo.Pronoun,
        PartOfSpeech.PREPOSITION: vo.Preposition,
        PartOfSpeech.ABBREVIATION: vo.Abbreviation,
        PartOfSpeech.AFFIX: vo.Affix,
        PartOfSpeech.ARTICLE: vo.Article,
        PartOfSpeech.AUXILIARY_VERB: vo.AuxiliaryVerb,
        PartOfSpeech.CONJUNCTION: vo.Conjunction,
        PartOfSpeech.DEFINITE_ARTICLE: vo.DefiniteArticle,
        PartOfSpeech.FAMILY_NAME: vo.FamilyName,
        PartOfSpeech.GIVEN_NAME: vo.GivenName,
        PartOfSpeech.IDIOM: vo.Idiom,
        PartOfSpeech.IMPERATIVE: vo.Imperative,
        PartOfSpeech.NOUN_PLURAL: vo.NounPlural,
        PartOfSpeech.NOUN_POSSESSIVE: vo.NounPosessive,
        PartOfSpeech.PAST_PARTICIPLE: vo.PastParticiple,
        PartOfSpeech.PHRASAL_PREFIX: vo.PhrasalPrefix,
        PartOfSpeech.PROPER_NOUN: vo.ProperNoun,
        PartOfSpeech.PROPER_NOUN_PLURAL: vo.ProperNounPlural,
        PartOfSpeech.PROPER_NOUN_POSSESSIVE: vo.ProperNounPosessive,
        PartOfSpeech.SUFFIX: vo.Suffix,
        PartOfSpeech.VERB_INTRANSITIVE: vo.VerbIntransitive,
        PartOfSpeech.VERB_TRANSITIVE: vo.VerbTransitive,
    }
    _RT_TO_GRAMMAR: ClassVar[dict[RelationshipType, vo.Grammar]] = {
        RelationshipType.SYNONYM: vo.Synonym,
        RelationshipType.ANTONYM: vo.Antonym,
        RelationshipType.VARIANT: vo.Variant,
        RelationshipType.EQUIVALENT: vo.Equivalent,
        RelationshipType.CROSS_REFERENCE: vo.CrossReference,
        RelationshipType.RELATED_WORD: vo.RelatedWord,
        RelationshipType.RHYME: vo.Rhyme,
        RelationshipType.FORM: vo.Form,
        RelationshipType.ETYMOLOGLYCALY_RELATED_TERM: vo.EtmologicallyRelatedTerm,
        RelationshipType.HYPERNYM: vo.Hypernym,
        RelationshipType.HYPONYM: vo.Hyponym,
        RelationshipType.INFLECTED_FORM: vo.InflectedForm,
        RelationshipType.PRIMARY: vo.Primary,
        RelationshipType.SAME_CONTEXT: vo.SameContext,
        RelationshipType.VERB_FORM: vo.VerbForm,
        RelationshipType.VERB_STEM: vo.VerbStem,
        RelationshipType.HAS_TOPIC: vo.HasTopic,
    }

    def defintion(self, inp: WnDefinition) -> WaDefintion | None:
        if text := (inp.text or "").strip():
            g = self._POS_TO_GRAMMER.get(inp.partOfSpeech, vo.Miscellaneous)
            return WaDefintion(
                attribution=inp.attributionText or "", type=g, text=text
            )
        return None

    def example(self, inp: WnExample) -> WaExample:
        sentence = self._MARKDOWN.render(inp.text)
        sentence = self._HTML_TO_MARKUP.transform(sentence)
        return WaExample(attribution="", type=vo.Sentence, text=sentence)

    def phrase(self, inp: WnBigram) -> WaPhrase:
        text = f"{inp.gram1} {inp.gram2}" if inp.gram2 else inp.gram1
        return WaPhrase(attribution="", type=vo.Nothing, text=text)

    def syllable(self, inp: WnSyllable) -> WaSyllable:
        return WaSyllable(text=inp.text)

    def thesaurus(self, inp: WnRelated) -> list[WaNym]:
        return [
            WaNym(
                attribution="",
                type=self._RT_TO_GRAMMAR.get(
                    inp.relationshipType, vo.Miscellaneous
                ),
                text=w,
            )
            for w in inp.words
        ]
