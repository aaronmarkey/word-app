from __future__ import annotations

from functools import total_ordering

from textual.reactive import var
from textual.widgets import Input, OptionList, Static
from textual.widgets.option_list import Option
from textual.visual import VisualType

from word_app.ui.screens.quick_search._models import Hit


@total_ordering
class Suggestion(Option):
    """Class that holds a hit in the SuggestionList."""

    def __init__(
        self,
        prompt: VisualType,
        hit: Hit,
        id: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the option.

        Args:
            prompt: The prompt for the option.
            hit: The details of the hit associated with the option.
            id: The optional ID for the option.
            disabled: The initial enabled/disabled state. Enabled by default.
        """
        super().__init__(prompt, id, disabled)
        self.hit = hit
        """The details of the hit associated with the option."""

    def __hash__(self) -> int:
        return id(self)

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Suggestion):
            return self.hit < other.hit
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Suggestion):
            return self.hit == other.hit
        return NotImplemented


class SuggestionIcon(Static, inherit_css=False):
    """Widget for displaying a search icon before the suggestion input."""

    DEFAULT_CSS = """
    SuggestionIcon {
        margin-left: 1;
        margin-top: 1;
        width: 2;
    }
    """

    icon: var[str] = var("🔎")

    def render(self) -> VisualType:
        """Render the icon.

        Returns:
            The icon renderable.
        """
        return self.icon


class SuggestionInput(Input):
    """The suggestion palette input control."""

    DEFAULT_CSS = """
    SuggestionInput, SuggestionInput:focus {
        border: blank;
        width: 1fr;
        padding-left: 0;
        background: transparent;
        background-tint: 0%;
    }
    """


class SuggestionList(OptionList, can_focus=False):
    """The suggestion palette's sugtgestion list."""

    DEFAULT_CSS = """
    SuggestionList {
        visibility: hidden;
        border: outer $foreground 50%;
        border-top: none;
        height: auto;
        max-height: 70vh;
        background: transparent;
    }

    SuggestionList:focus {
        border: blank;
    }

    SuggestionList.--visible {
        visibility: visible;
    }

    SuggestionList.--populating {
        border-bottom: none;
    }

    SuggestionList > .option-list--option-highlighted {
        color: $block-cursor-blurred-foreground;
        background: $user-action;
    }

    SuggestionList:nocolor > .option-list--option-highlighted {
        text-style: reverse;
    }

    SuggestionList > .option-list--option {
        padding: 0 3;
        color: $foreground;
        text-style: bold;
    }
    """
