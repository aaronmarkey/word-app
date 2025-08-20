from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from textual.app import RenderResult

from textual.events import MouseDown, MouseEvent
from textual.message import Message
from textual.visual import Visual, visualize
from textual.widget import Widget
from textual.widgets import Label

from word_app.ui.constants import BOUND_KEY, HELP_HOVER_ICON


def WALabel(
    text: str,
    *,
    binding_key: str = "",
    lpadding: int = 0,
    rpadding: int = 0,
    separator: str = "",
    tooltip: str = "",
    styles: str = "",
    classes: str = "",
) -> Label:
    allowed_styles = {"b", "d", "i", "u", "s", "r"}
    styles = styles.lower()
    for style in styles:
        if style not in allowed_styles:
            raise ValueError(f"Invalid Label styles: '{style}'.")

    lt = f"{' ' * lpadding}{text}{' ' * rpadding}"

    if tooltip:
        lt += f" {HELP_HOVER_ICON}"

    if binding_key:
        lt = BOUND_KEY.format(key=binding_key) + f" {lt}"

    for style in styles:
        lt = f"[{style}]{lt}[/]"

    lt += separator

    # Mypy doesn't support dictionary unpacking, a basic Python feature.
    # Fucking worthless type checker.
    # So I have to use shit typing to get it to stop complaining about
    # something it shouldn't.
    options: dict[str, Any] = {}
    if classes:
        options["classes"] = classes

    label = Label(lt, **options)

    if tooltip:
        label.tooltip = tooltip

    return label


class ClickableText(Widget, inherit_bindings=False):
    @dataclass
    class TextClicked(Message):
        word: str
        click: MouseEvent

    def __init__(self, text: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._current_click_event: MouseEvent | None = None
        self._text = self._make_clickable(text)
        self._visual: Visual | None = None

    @property
    def visual(self) -> Visual:
        if self._visual is None:
            self._visual = visualize(self, self._text, markup=True)
        return self._visual

    @abstractmethod
    def _make_clickable(self, text: str) -> str:
        """"""

    def _markup(self, text: str, lc: str = "") -> str:
        callable = f"text_clicked('{text}')"
        return f"[@click={callable}]{text}[/]{lc}"

    def render(self) -> RenderResult:
        return self.visual

    # Action Methods
    def action_text_clicked(self, text: str) -> None:
        if event := self._current_click_event:
            self.post_message(self.TextClicked(word=text, click=event))
            self._current_click_event = None

    # Event Listeners
    def on_mouse_down(self, event: MouseDown) -> None:
        # Hacky way to get the event from an inline @click.
        self._current_click_event = event


class ClickablePhrase(ClickableText):
    def _make_clickable(self, text: str) -> str:
        return f"[u]{self._markup(text)}[/]"


class ClickableSentence(ClickableText):
    DEFAULT_CSS = """
    ClickableSentence {
        height: auto;
        width: auto;
    }
    """

    def _make_clickable(self, text: str) -> str:
        def _for_word(word: str) -> str:
            if not word:
                return word

            allowed_non_alpha = {"-", ".", ";", ":", ","}

            not_alphas: set[str] = set()
            for character in word:
                if not character.isalpha():
                    not_alphas.add(character)

            if (not not_alphas) or (
                not_alphas and not_alphas - allowed_non_alpha == set()
            ):
                w = word[0:-1] if word[-1] in allowed_non_alpha else word
                lc = word[-1] if word[-1] in allowed_non_alpha else ""
                return self._markup(w, lc)

            return word

        words = text.split(" ")
        new_words: list[str] = []
        for word in words:
            new_words.append(_for_word(word))

        new_sent = " ".join(new_words)
        return f"[u]{new_sent}[/]"
