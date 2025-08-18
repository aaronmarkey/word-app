from dataclasses import dataclass, field, fields
from typing import Any


def _error(name: str, value: str) -> None:
    """Helper to raise an error for some validation issue."""
    raise ValueError(
        f"Invalid value of '{value} for Datamuse configration '{name}'."
    )


@dataclass
class Param:
    """Base class for query parameters used in endpoints."""

    value: Any = ""
    """The value of the query parameter."""

    name: str = ""
    """The anme of the query parameter."""

    @property
    def as_dict(self) -> dict[str, int | str]:
        return {self.name: self.value} if self.value else {}


@dataclass
class Endpoint:
    """Endpoint container.

    Contains query params, endpoint configuration information.
    """

    _endpoint: str = field(default="")

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
                param: Param = getattr(self, _field.name)
                if _ := param.value:
                    params |= param.as_dict
        return params
