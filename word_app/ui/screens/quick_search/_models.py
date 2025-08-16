from dataclasses import dataclass
from typing import AsyncIterator, TypeAlias

from textual.types import IgnoreReturnCallbackType
from textual.visual import VisualType


@dataclass
class Hit:
    """Holds the details of a single search hit."""

    score: float
    """The score of the hit, a float between 0 and 1."""

    match_display: VisualType
    """A string or Rich renderable representation of the hit."""

    action: IgnoreReturnCallbackType
    """The function to call when the hit is chosen."""

    text: str | None = None
    """The text associated with the hit, as plain text.

    If `match_display` is not simple text, this attribute should be provided
    by the Provider object.
    """

    help: str | None = None
    """Optional help text for the hit."""

    @property
    def prompt(self) -> VisualType:
        """The prompt to use when displaying the hit in the palette."""
        return self.match_display

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Hit):
            return self.score < other.score
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Hit):
            return self.score == other.score
        return NotImplemented

    def __post_init__(self) -> None:
        """Ensure 'text' is populated."""
        if self.text is None:
            self.text = str(self.match_display)


Hits: TypeAlias = AsyncIterator["Hit"]
"""Return type for the Provider's `search` method."""
