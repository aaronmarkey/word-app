import factory
from faker import Faker
from faker.providers import BaseProvider, DynamicProvider, company

from word_app.data import models
from word_app.data.grammar import (
    DICTIONARY_GRAMMARS,
    THESAURUS_GRAMMARS,
    Miscellaneous,
)

dictionary_grammar = DynamicProvider(
    provider_name="dictionary_grammar", elements=DICTIONARY_GRAMMARS
)
thesaurus_grammar = DynamicProvider(
    provider_name="thesaurus_grammar", elements=THESAURUS_GRAMMARS
)


class CustomProvider(BaseProvider):
    def frequency_graph(
        self,
        *,
        start_year: int,
        end_year: int,
        max_value: int = 100,
    ) -> models.FrequencyGraph:
        graph = models.FrequencyGraph()
        decade = 10
        for year in range(start_year, end_year + 1, decade):
            start = (year // decade) * decade
            end = start + decade - 1
            if end > end_year:
                end = end_year
            value = self.generator.random.randint(1, max_value + 1)
            graph.intervals.append(
                models.FrequencyInterval(
                    start=start,
                    end=end,
                    value=value,
                )
            )
        return graph


fake = Faker()
fake.add_provider(company)
fake.add_provider(CustomProvider)
fake.add_provider(dictionary_grammar)
fake.add_provider(thesaurus_grammar)


class DefinitionFactory(factory.Factory):
    class Meta:
        model = models.Definition

    attribution = ""
    type = factory.LazyAttribute(lambda _: fake.dictionary_grammar())
    text = factory.LazyAttribute(lambda _: fake.sentence())


class EtymologyFactory(factory.Factory):
    class Meta:
        model = models.Etymology

    attribution = ""
    text = factory.LazyAttribute(lambda _: fake.sentence(nb_words=12))


class ExampleFactory(factory.Factory):
    class Meta:
        model = models.Example

    attribution = ""
    type = factory.LazyAttribute(lambda _: fake.dictionary_grammar())
    text = factory.LazyAttribute(lambda _: fake.sentence(nb_words=6))


class NymFactory(factory.Factory):
    class Meta:
        model = models.Nym

    attribution = ""
    type = factory.LazyAttribute(lambda _: fake.thesaurus_grammar())
    text = factory.LazyAttribute(lambda _: fake.word())


class PhraseFactory(factory.Factory):
    class Meta:
        model = models.Phrase

    attribution = ""
    type = Miscellaneous
    text = factory.LazyAttribute(
        lambda _: " ".join(fake.words(nb=3, unique=True))
    )


class SyllableFactory(factory.Factory):
    class Meta:
        model = models.Syllable

    text = factory.LazyAttribute(
        lambda _: "".join([v.lower() for v in fake.random_letters(2)])
    )


class DefinitionsFactory(factory.Factory):
    class Meta:
        model = models.Definitions

    source = factory.LazyAttribute(lambda _: fake.company() + " Dictionary")
    definitions = factory.List(
        [factory.SubFactory(DefinitionFactory) for _ in range(50)]
    )


class EtymologiesFactory(factory.Factory):
    class Meta:
        model = models.Etymologies

    source = factory.LazyAttribute(lambda _: fake.company() + " Dictionary")
    etymologies = factory.List(
        [factory.SubFactory(EtymologyFactory) for _ in range(2)]
    )


class ExamplesFactory(factory.Factory):
    class Meta:
        model = models.Examples

    examples = factory.List(
        [factory.SubFactory(ExampleFactory) for _ in range(25)]
    )


class PhrasesFactory(factory.Factory):
    class Meta:
        model = models.Phrases

    source = factory.LazyAttribute(lambda _: fake.sentence())
    phrases = factory.List(
        [factory.SubFactory(PhraseFactory) for _ in range(25)]
    )


class SyllablesFactory(factory.Factory):
    class Meta:
        model = models.Syllables

    syllables = factory.List(
        [factory.SubFactory(SyllableFactory) for _ in range(3)]
    )


class ThesaurusFactory(factory.Factory):
    class Meta:
        model = models.Thesaurus

    source = factory.LazyAttribute(lambda _: fake.sentence())
    nyms = factory.List([factory.SubFactory(NymFactory) for _ in range(50)])


class WordFactory(factory.Factory):
    class Meta:
        model = models.Word

    word = factory.LazyAttribute(lambda _: fake.word())

    definitions = factory.SubFactory(DefinitionsFactory)
    etymologies = factory.SubFactory(EtymologiesFactory)
    examples = factory.SubFactory(ExamplesFactory)
    frequency_graph = factory.LazyAttribute(
        lambda _: fake.frequency_graph(start_year=1800, end_year=2025)
    )
    phrases = factory.SubFactory(PhrasesFactory)
    syllables = factory.SubFactory(SyllablesFactory)
    thesaurus = factory.SubFactory(ThesaurusFactory)
