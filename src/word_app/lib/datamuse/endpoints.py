from dataclasses import dataclass, field
from typing import TypedDict

from word_app.lib._shr.models import Endpoint, Param
from word_app.lib._shr.utils import make_value_error


@dataclass
class DatamuseEndpoint(Endpoint):
    """Datamuse Endpoint container.

    Contains query params, endpoint configuration information.
    """

    @dataclass
    class Max(Param):
        """Both Datamuse endpoints support the 'max' parameter."""

        name: str = field(default="max")
        value: int | str | None = 100
        _min: int = field(default=1)
        _max: int = field(default=1000)

        def __post_init__(self) -> None:
            value = int(self.value) if self.value else -1
            if not (self._min <= value and value <= self._max):
                make_value_error(self.name, str(self.value))

    max: Max = field(default_factory=Max)


@dataclass
class SuggestionsEndpoint(DatamuseEndpoint):
    """Suggestion endpoint."""

    @dataclass
    class Prefix(Param):
        """The string partial to get suggestions for."""

        name: str = field(default="s")
        value: str | int | None = field(default="")

    _endpoint: str = "sug"
    s: Prefix = field(default_factory=Prefix)


@dataclass
class WordsEndpoint(DatamuseEndpoint):
    """Words endpoint."""

    @dataclass
    class MeansLike(Param):
        """Require results have a meaning related to this string value"""

        name: str = field(default="ml")
        value: str | int | None = field(default="")

    @dataclass
    class SoundsLike(Param):
        """Require results are pronounced similarly to the string of chars."""

        name: str = field(default="sl")
        value: str | int | None = field(default="")

    @dataclass
    class SpelledLike(Param):
        """Require results are spelled similarly to the string of chars."""

        name: str = field(default="sp")
        value: str | int | None = field(default="")

    class ParamsType(TypedDict):
        """Typing for endpoint params. For ease-of-use."""

        ml: "WordsEndpoint.MeansLike"
        sl: "WordsEndpoint.SoundsLike"
        sp: "WordsEndpoint.SpelledLike"

    _endpoint: str = "words"
    ml: MeansLike = field(default_factory=MeansLike)
    sl: SoundsLike = field(default_factory=SoundsLike)
    sp: SpelledLike = field(default_factory=SpelledLike)
