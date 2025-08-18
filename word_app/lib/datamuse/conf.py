from dataclasses import dataclass, field, fields
from typing import TypedDict


def _error(name: str, value: str) -> None:
    """Helper to raise an error for some validation issue."""
    raise ValueError(
        f"Invalid value of '{value} for Datamuse configration '{name}'."
    )


@dataclass
class Param:
    """Base class for query parameters used in endpoints."""

    value: int | str | None = ""
    """The value of the query parameter."""

    name: str = ""
    """The anme of the query parameter."""

    @property
    def as_dict(self) -> dict[str, int | str]:
        return {self.name: self.value} if self.value else {}


@dataclass
class Endpoint:
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
                _error(self.name, str(self.value))

    _endpoint: str = field(default="")
    param_max: Max = field(default_factory=Max)

    @property
    def endpoint(self) -> str:
        """Public access to endpoint."""
        return self._endpoint

    @property
    def params(self) -> dict:
        """Convert all Param type fields into a JSON-compat dictionary."""
        params: dict = {}
        for _field in fields(self):
            if issubclass(_field.type, Param):  # type: ignore
                param = getattr(self, _field.name)
                if value := param.value:
                    params[param.name] = value
        return params


@dataclass
class Suggestions(Endpoint):
    """Suggestion endpoint."""

    @dataclass
    class Prefix(Param):
        """The string partial to get suggestions for."""

        name: str = field(default="s")
        value: str | int | None = field(default="")

    _endpoint: str = "sug"
    param_s: Prefix = field(default_factory=Prefix)


@dataclass
class Words(Endpoint):
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

        param_ml: "Words.MeansLike"
        param_sl: "Words.SoundsLike"
        param_sp: "Words.SpelledLike"

    _endpoint: str = "words"
    param_ml: MeansLike = field(default_factory=MeansLike)
    param_sl: SoundsLike = field(default_factory=SoundsLike)
    param_sp: SpelledLike = field(default_factory=SpelledLike)


@dataclass(frozen=True, eq=True)
class DatamuseApiConf:
    """Datamuse API configuration."""

    root: str
    """The base URL of the Datamuse API."""
    timeout: float | None
    """Default timeout to use on requests to API, in seconds."""

    def __post_init__(self) -> None:
        if to := self.timeout:
            if to < 0.0:
                _error("timeout", str(to))

    def full_path(self, endpoint: Endpoint) -> str:
        return f"{self.root}/{endpoint.endpoint}"


DEFAULT_API_CONF = DatamuseApiConf(
    root="https://api.datamuse.com",
    timeout=1.0,
)
