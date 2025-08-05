import factory
from faker import Faker
from faker.providers import DynamicProvider, company

from word_app.data import models
from word_app.data.grammar import DICTIONARY_GRAMMARS, THESAURUS_GRAMMARS

dictionary_grammar = DynamicProvider(
    provider_name="dictionary_grammar", elements=DICTIONARY_GRAMMARS
)
thesaurus_grammar = DynamicProvider(
    provider_name="thesaurus_grammar", elements=THESAURUS_GRAMMARS
)

fake = Faker()
fake.add_provider(company)
fake.add_provider(dictionary_grammar)
fake.add_provider(thesaurus_grammar)


class DefinitionFactory(factory.Factory):
    class Meta:
        model = models.Definition

    attribution = ""
    type = factory.LazyAttribute(lambda _: fake.dictionary_grammar())
    text = factory.LazyAttribute(lambda _: fake.sentence())


class DefinitionsFactory(factory.Factory):
    class Meta:
        model = models.Definitions

    source = factory.LazyAttribute(lambda _: fake.company() + " Dictionary")
    definitions = factory.List(
        [factory.SubFactory(DefinitionFactory) for _ in range(50)]
    )


class NymFactory(factory.Factory):
    class Meta:
        model = models.Nym

    attribution = ""
    type = factory.LazyAttribute(lambda _: fake.thesaurus_grammar())
    text = factory.LazyAttribute(lambda _: fake.word())


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
    thesaurus = factory.SubFactory(ThesaurusFactory)
