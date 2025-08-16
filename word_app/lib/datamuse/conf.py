from dataclasses import dataclass


def _error(name: str, value: str) -> None:
    raise ValueError(
        f"Invalid value of '{value} for Datamuse configration '{name}'."
    )


@dataclass(frozen=True, eq=True)
class LimitContainer:
    default: int
    max: int
    min: int

    def _validate(self, name: str, value: int) -> None:
        if not (self.min <= value and value <= self.max):
            _error(name, str(value))

    def validate(self) -> None:
        self._validate("default", self.default)

    def validate_limit(self, limit: int) -> None:
        self._validate("limit", limit)


@dataclass(frozen=True, eq=True)
class LocationContainer:
    root: str
    endpoint_suggest: str
    endpoint_words: str

    def validate(self) -> None:
        for name, value in [
            ("root", self.root),
            ("endpoint_suggest", self.endpoint_suggest),
            ("endpoint_words", self.endpoint_words),
        ]:
            if not value.strip():
                _error(name, value)

    def full_path(self, endpoint: str) -> str:
        endpoint = getattr(self, f"endpoint_{endpoint}")
        return f"{self.root}/{endpoint}"


@dataclass(frozen=True, eq=True)
class DatamuseClientParamsContainer:
    limit: LimitContainer
    location: LocationContainer
    timeout: float | None

    def _validate_timeout(self) -> None:
        if to := self.timeout:
            if to < 0.0:
                _error("timeout", str(to))

    def validate(self) -> None:
        self.limit.validate()
        self.location.validate()
        self._validate_timeout()


DatamuseClientParams = DatamuseClientParamsContainer(
    limit=LimitContainer(max=1000, min=1, default=100),
    location=LocationContainer(
        root="https://api.datamuse.com",
        endpoint_suggest="sug",
        endpoint_words="words",
    ),
    timeout=1.0,
)
