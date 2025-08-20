from dataclasses import dataclass, field
from typing import TypeAlias

from word_app.lib.utils import Endpoint, EnumParam, Param, make_value_error
from word_app.lib.wordnik.models import AmericanHeritage, SourceDictionary
from word_app.lib.wordnik.models import (
    PartOfSpeech as POSEnum,
)
from word_app.lib.wordnik.models import (
    RelationshipType as RTEnum,
)


@dataclass
class WordnikEndpoint(Endpoint):
    _endpoint: str = "word.{type}/{word}/{purpose}"
    _endpoint_type: str = "json"
    _endpoint_purpose: str = ""

    @dataclass
    class ApiKey(Param):
        name: str = field(default="api_key")
        value: str = field(default="")

    @property
    def endpoint(self) -> str:
        return self._endpoint.format(
            type=self._endpoint_type,
            purpose=self._endpoint_purpose,
            word="{word}",
        )

    def endpoint_fmt(self, word: str) -> str:
        return self.endpoint.format(word=word)

    api_key: ApiKey = field(default_factory=ApiKey)


@dataclass
class _UseCanonical(Param):
    name: str = field(default="useCanonical")
    value: bool = field(default=False)


@dataclass
class _Word(Param):
    name: str = field(default="word")
    value: str = field(default="")


@dataclass
class Definitions(WordnikEndpoint):
    @dataclass
    class IncludeRelated(Param):
        name: str = field(default="includeRelated")
        value: bool = field(default=False)

        @property
        def as_dict(self) -> dict:
            v = "true" if self.value else "false"
            return {self.name: v}

    @dataclass
    class IncludeTags(Param):
        name: str = field(default="includeTags")
        value: bool = field(default=False)

    @dataclass
    class Limit(Param):
        name: str = field(default="limit")
        value: int = field(default=500)

    @dataclass
    class PartOfSpeech(EnumParam):
        name: str = field(default="partOfSpeech")
        value: list[POSEnum] = field(default_factory=list)

    @dataclass
    class SourceDictionaries(Param):
        name: str = field(default="sourceDictionaries")
        value: list[SourceDictionary] = field(
            default_factory=lambda: [AmericanHeritage]
        )

        @property
        def as_dict(self) -> dict:
            return (
                {self.name: [str(d) for d in self.value]} if self.value else {}
            )

    UseCanonical: TypeAlias = _UseCanonical  # type: ignore
    Word: TypeAlias = _Word  # type: ignore

    _endpoint_purpose: str = "definitions"
    include_related: IncludeRelated = field(default_factory=IncludeRelated)
    include_tags: IncludeTags = field(default_factory=IncludeTags)
    limit: Limit = field(default_factory=Limit)
    part_of_speech: PartOfSpeech = field(default_factory=PartOfSpeech)
    source_dictionaries: SourceDictionaries = field(
        default_factory=SourceDictionaries
    )
    use_canonical: UseCanonical = field(default_factory=UseCanonical)
    word: Word = field(default_factory=Word)


@dataclass
class RelatedWords(WordnikEndpoint):
    @dataclass
    class LimitPerRelationshipType(Param):
        name: str = field(default="limitPerRelationshipType")
        value: int = field(default=1_000)

    @dataclass
    class RelationshipTypes(EnumParam):
        name: str = field(default="relationshipTypes")
        value: list[RTEnum] | None = field(default=None)

    UseCanonical: TypeAlias = _UseCanonical  # type: ignore
    Word: TypeAlias = _Word  # type: ignore

    _endpoint_purpose: str = "relatedWords"
    limit_per_relationship_type: LimitPerRelationshipType = field(
        default_factory=LimitPerRelationshipType
    )
    relationship_types: RelationshipTypes = field(
        default_factory=RelationshipTypes
    )
    use_canonical: UseCanonical = field(default_factory=UseCanonical)
    word: Word = field(default_factory=Word)


@dataclass
class WordnikApiConf:
    api_key: str
    root: str = "https://api.wordnik.com/v4"
    timeout: float | None = 1.0

    def __post_init__(self) -> None:
        if to := self.timeout:
            if to < 0.0:
                make_value_error("timeout", str(to))

    def full_path(self, word: str, endpoint: WordnikEndpoint) -> str:
        return f"{self.root}/{endpoint.endpoint_fmt(word)}"
