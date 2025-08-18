from dataclasses import dataclass, field

from word_app.lib.utils import Endpoint, Param, _error
from word_app.lib.wordnik.models import AmericanHeritage, SourceDictionary
from word_app.lib.wordnik.models import PartOfSpeech as POSEnum


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
class WordDefintions(WordnikEndpoint):
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
    class PartOfSpeech(Param):
        name: str = field(default="partOfSpeech")
        value: list[POSEnum] = field(default_factory=list)

        @property
        def as_dict(self) -> dict:
            return {self.name: ",".join([v.value for v in self.value])}

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

    @dataclass
    class UseCanonical(Param):
        name: str = field(default="useCanonical")
        value: bool = field(default=False)

    @dataclass
    class Word(Param):
        name: str = field(default="word")
        value: str = field(default="")

    _endpoint_purpose: str = "definitions"
    word: Word = field(default_factory=Word)
    limit: Limit = field(default_factory=Limit)
    part_of_speech: PartOfSpeech = field(default_factory=PartOfSpeech)
    include_related: IncludeRelated = field(default_factory=IncludeRelated)
    source_dictionaries: SourceDictionaries = field(
        default_factory=SourceDictionaries
    )
    use_canonical: UseCanonical = field(default_factory=UseCanonical)
    include_tags: IncludeTags = field(default_factory=IncludeTags)


@dataclass
class WordnikApiConf:
    api_key: str
    root: str = "https://api.wordnik.com/v4"
    timeout: float | None = 1.0

    def __post_init__(self) -> None:
        if to := self.timeout:
            if to < 0.0:
                _error("timeout", str(to))

    def full_path(self, word: str, endpoint: WordnikEndpoint) -> str:
        return f"{self.root}/{endpoint.endpoint_fmt(word)}"
