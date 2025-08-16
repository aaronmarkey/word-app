from statistics import mean

import pyperclip
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, ItemGrid, VerticalScroll
from textual.events import Key, MouseDown, MouseEvent, MouseUp
from textual.widget import Widget
from textual.widgets import (
    Button,
    Collapsible,
    Footer,
    Header,
    Label,
    Rule,
    Sparkline,
)

from pydantic import BaseModel

from word_app.data.grammar import (
    Antonym,
    Form,
    Grammar,
    Hypernym,
    Hyponym,
    InflectedForm,
    Rhyme,
    Synonym,
    Variant,
    VerbForm,
    VerbStem,
)
from word_app.data.models import Word, WordDetailContainer
from word_app.ext import WAScreen
from word_app.lex import EN_LANG, EN_LANG_FORMATS
from word_app.ui.constants import HELP_HOVER_ICON
from word_app.ui.navigation.common import POP_SCREEN
from word_app.ui.widgets import Sidebar, SidebarButton, WALabel


class ClickableSentence:
    def __init__(self, sentence: str, *, action: str) -> None:
        self._sentence = sentence
        self._action = action

    def _for_word(self, word: str) -> str:
        allowed_non_alpha = {"-", "'", '"'}
        sanitized = ""

        for character in word:
            if character.isalpha() or character in allowed_non_alpha:
                sanitized += character

        callable = f"screen.{self._action}('{sanitized}')"
        new_word = f"[@click={callable}][u]{sanitized}[/][/]"

        return word.replace(sanitized, new_word)

    def _convert(self) -> str:
        words = self._sentence.split(" ")
        clickables: list[str] = []

        for word in words:
            clickables.append(self._for_word(word))

        return "[u] [/]".join(clickables)

    def __str__(self) -> str:
        return self._convert()


class WordDetailSection(BaseModel):
    title: str
    desc: str
    key_binding: str
    css_class: str


InformationSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_INFO_TITLE,
    desc=EN_LANG.SIDEBAR_INFO_DESCRIPTION,
    key_binding="1",
    css_class="information",
)

DefinitionSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_DEFINITIONS_TITLE,
    desc=EN_LANG.SIDEBAR_DEFINITIONS_DESCRIPTION,
    key_binding="2",
    css_class="definition",
)

ThesaurusSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_THESAURUS_TITLE,
    desc=EN_LANG.SIDEBAR_THESAURUS_DESCRIPTION,
    key_binding="3",
    css_class="thesaurus",
)

RelatedSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_RELATED_TITLE,
    desc=EN_LANG.SIDEBAR_RELATED_DESCRIPTION,
    key_binding="4",
    css_class="related",
)

ExampleSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_EXAMPLES_TITLE,
    desc=EN_LANG.SIDEBAR_EXAMPLES_DESCRIPTION,
    key_binding="5",
    css_class="example",
)

PhraseSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_PHRASES_TITLE,
    desc=EN_LANG.SIDEBAR_PHRASES_DESCRIPTION,
    key_binding="6",
    css_class="phrase",
)


class WordDetailScreen(WAScreen):
    AUTO_FOCUS = ""
    BINDINGS = [
        POP_SCREEN.binding,
        ("-", "close_all_sections", EN_LANG.WD_CLOSE_ALL_SECTIONS),
    ]

    WA_BINDING = "w"
    WA_ICON = "🗣️"
    WA_TITLE = "Word Details"

    class SidebarButtonManager:
        id_prefix = "sidebarbutton"
        sep = "_"

        @classmethod
        def make_button_id(cls, key_bind: str) -> str:
            return f"{cls.id_prefix}{cls.sep}{key_bind}"

        @classmethod
        def parse_button_id(cls, button_id: str) -> str:
            return button_id.split(cls.sep)[-1]

    def __init__(self, *, word: Word) -> None:
        super().__init__()
        self._word = word
        self._active_sections: dict[str, Collapsible] = {}
        self._current_click_event: MouseEvent | None = None

        self.title = f"{self.WA_ICON}  {self._word.word}"

    # Composition
    def _compose_collapsible_grid(
        self,
        *,
        container: WordDetailContainer,
        section: WordDetailSection,
        allowed_types: list[Grammar],
    ) -> Collapsible | None:
        # Allowed Types and order they are displayed.
        if container.has_value:
            content: list[Widget] = []
            column_padding = 3
            """int: The padding between columns in the ItemGrid."""

            # Store map so I don't calculate it multiple times.
            by_type = container.by_type

            for idx, allowed in enumerate(allowed_types):
                # Don't show *nym section if none exist.
                if nyms := by_type.get(allowed, []):
                    longest_word = 0

                    # Label for the section.
                    content.append(
                        WALabel(
                            f"{allowed.title_display} ({len(nyms)}):",
                            classes="collapsible--pos",
                            styles="ib",
                        )
                    )

                    # Create a list of *nyms and calculate the longest word
                    # for column padding.
                    items: list[Label] = []
                    for nym in nyms:
                        if len(nym.text) > longest_word:
                            longest_word = len(nym.text)
                        lt = ClickableSentence(nym.text, action="click_word")
                        items.append(Label(str(lt)))
                    # Everything goes in an item grid for dynamic layout.
                    content.append(
                        ItemGrid(
                            *items,
                            min_column_width=longest_word + column_padding,
                        )
                    )

                    # Horizontal rule between sections, but not after the
                    # last section.
                    if idx != len(allowed_types) - 1:
                        content.append(Rule())

            con = Collapsible(
                *content,
                title=section.title,
                collapsed=False,
                classes="word-detail--container",
            )
            self._active_sections[section.key_binding] = con
            return con
        return None

    def _compose_collapsible_list(
        self,
        *,
        container: WordDetailContainer,
        section: WordDetailSection,
        include_attribution: bool = True,
    ) -> Collapsible | None:
        if container.has_value:
            labels: list[Widget] = []

            if include_attribution:
                attribution_text = EN_LANG_FORMATS.ATTRIBUTION.format(
                    attr=container.source
                )
                labels.append(
                    WALabel(
                        attribution_text,
                        classes="collapsible--attribution",
                        styles="ib",
                    )
                )

            by_type = container.by_type
            i = 0
            keys = sorted(
                [key for key in by_type.keys()],
                key=lambda k: k.title_display.lower(),
            )

            for part in keys:
                labels.append(
                    WALabel(
                        part.title_display,
                        classes="collapsible--pos",
                        separator=": ",
                        styles="ib",
                    )
                )
                details = by_type.get(part, [])
                for j, detail in enumerate(details):
                    horizontal = HorizontalGroup(
                        Label(f"[b]{j + 1}.[/]"),
                        Label(
                            str(
                                ClickableSentence(
                                    detail.text, action="click_word"
                                )
                            ),
                            classes="text",
                        ),
                        classes=(
                            "collapsible--list "
                            f"collapsible--{section.css_class}"
                        ),
                    )
                    labels.append(horizontal)

                if i < len(keys) - 1:
                    labels.append(Rule())
                i += 1

            con = Collapsible(
                *labels,
                title=section.title,
                collapsed=False,
                classes="word-detail--container",
            )
            self._active_sections[section.key_binding] = con
            return con
        return None

    def _compose_content(self) -> ComposeResult:
        all_sections: list[Collapsible] = []

        section_callables = [
            self._compose_information,
            self._compose_definitions,
            self._compose_thesaurus,
            self._compose_related,
            self._compose_examples,
            self._compose_phrases,
        ]

        for sc in section_callables:
            if section := sc():
                all_sections.append(section)

        yield VerticalScroll(*all_sections, classes="word-detail--content")

    def _compose_definitions(self) -> Collapsible | None:
        return self._compose_collapsible_list(
            container=self._word.definitions,
            section=DefinitionSection,
            include_attribution=True,
        )

    def _compose_examples(self) -> Collapsible | None:
        return self._compose_collapsible_list(
            container=self._word.examples,
            section=ExampleSection,
            include_attribution=False,
        )

    def _compose_information(self) -> Collapsible | None:
        elements: list[Widget] = []

        elements.append(
            Label(
                f"[i][b]{EN_LANG.WORD}[/][/]: {self._word.word}",
            )
        )

        if self._word.syllables.has_value:
            elements.append(
                Label(
                    f"[i][b]{EN_LANG.SYLLABLES}[/][/]: "
                    f"{self._word.syllables.as_string}",
                    classes="syllables",
                )
            )

        if self._word.etymologies.has_value:
            label_css = "collapsible--pos"
            if self._word.syllables.has_value:
                label_css += " mt-1"
            elements.append(
                WALabel(
                    EN_LANG.ETYMOLOGIES,
                    separator=": ",
                    classes=label_css,
                    styles="ib",
                )
            )

            for idx, ety in enumerate(self._word.etymologies.etymologies):
                horizontal = HorizontalGroup(
                    Label(f"[b]{idx + 1}.[/]"),
                    Label(ety.text, classes="text"),
                    classes=(
                        "collapsible--list "
                        f"collapsible--{InformationSection.css_class}"
                    ),
                )
                elements.append(horizontal)

        if self._word.frequency_graph.has_value:
            in_order = self._word.frequency_graph.in_order
            label_css = "collapsible--pos"
            if self._word.etymologies.has_value:
                label_css += " mt-1"
                flabel = WALabel(
                    f"{EN_LANG.FREQUENCY} {HELP_HOVER_ICON}",
                    classes=label_css,
                    separator=": ",
                    styles="ib",
                )
                flabel.tooltip = EN_LANG_FORMATS.FREQUENCY_TOOLTIP.format(
                    start=in_order[0].start,
                    end=in_order[-1].end,
                )
                elements.append(flabel)
                elements.append(
                    Sparkline(
                        [freq.value for freq in in_order], summary_function=mean
                    )
                )

        if elements:
            con = Collapsible(
                *elements,
                title=InformationSection.title,
                collapsed=False,
                classes="word-detail--container",
            )
            self._active_sections[InformationSection.key_binding] = con
            return con
        return None

    def _compose_phrases(self) -> Collapsible | None:
        return self._compose_collapsible_list(
            container=self._word.phrases,
            section=PhraseSection,
            include_attribution=False,
        )

    def _compose_related(self) -> Collapsible | None:
        return self._compose_collapsible_grid(
            container=self._word.thesaurus,
            section=RelatedSection,
            allowed_types=[
                Form,
                InflectedForm,
                Rhyme,
                Variant,
                VerbForm,
                VerbStem,
            ],
        )

    def _compose_sidebar(self) -> ComposeResult:
        active_buttons: list[Widget] = []
        inactive_buttons: list[Widget] = []

        infb = SidebarButton(
            InformationSection.title,
            desc=InformationSection.desc,
            key_binding=InformationSection.key_binding,
            id=self.SidebarButtonManager.make_button_id(
                InformationSection.key_binding
            ),
        )
        defb = SidebarButton(
            DefinitionSection.title,
            desc=DefinitionSection.desc,
            key_binding=DefinitionSection.key_binding,
            id=self.SidebarButtonManager.make_button_id(
                DefinitionSection.key_binding
            ),
        )
        theb = SidebarButton(
            ThesaurusSection.title,
            desc=ThesaurusSection.desc,
            key_binding=ThesaurusSection.key_binding,
            id=self.SidebarButtonManager.make_button_id(
                ThesaurusSection.key_binding
            ),
        )
        relb = SidebarButton(
            RelatedSection.title,
            desc=RelatedSection.desc,
            key_binding=RelatedSection.key_binding,
            id=self.SidebarButtonManager.make_button_id(
                RelatedSection.key_binding
            ),
        )
        exab = SidebarButton(
            ExampleSection.title,
            desc=ExampleSection.desc,
            key_binding=ExampleSection.key_binding,
            id=self.SidebarButtonManager.make_button_id(
                ExampleSection.key_binding
            ),
        )
        phrb = SidebarButton(
            PhraseSection.title,
            desc=PhraseSection.desc,
            key_binding=PhraseSection.key_binding,
            id=self.SidebarButtonManager.make_button_id(
                PhraseSection.key_binding
            ),
        )

        if (
            self._word.etymologies.has_value
            or self._word.frequency_graph.has_value
            or self._word.syllables.has_value
        ):
            active_buttons.append(infb)
        else:
            infb.disabled = True
            infb.tooltip = None
            inactive_buttons.append(infb)

        if self._word.definitions.has_value:
            active_buttons.append(defb)
        else:
            defb.disabled = True
            defb.tooltip = None
            inactive_buttons.append(defb)

        if self._word.thesaurus.has_value:
            active_buttons.append(theb)
            active_buttons.append(relb)
        else:
            theb.disabled = True
            theb.tooltip = None
            inactive_buttons.append(theb)
            relb.disabled = True
            relb.tooltip = None
            inactive_buttons.append(relb)

        if self._word.examples.has_value:
            active_buttons.append(exab)
        else:
            exab.disabled = True
            exab.tooltip = None
            inactive_buttons.append(exab)

        if self._word.phrases.has_value:
            active_buttons.append(phrb)
        else:
            phrb.disabled = True
            phrb.tooltip = None
            inactive_buttons.append(phrb)

        yield Sidebar(
            active_buttons + inactive_buttons, classes="with-header with-footer"
        )

    def _compose_thesaurus(self) -> Collapsible | None:
        # Allowed Types and order they are displayed.
        return self._compose_collapsible_grid(
            container=self._word.thesaurus,
            section=ThesaurusSection,
            allowed_types=[
                Synonym,
                Antonym,
                Hypernym,
                Hyponym,
            ],
        )

    def compose(self) -> ComposeResult:
        yield from self._compose_sidebar()
        yield from self._compose_content()

        h = Header(icon="")
        h.disabled = True
        yield h

        yield Footer()

    # Event Listeners
    def action_click_word(self, word: str) -> None:
        if event := self._current_click_event:
            if event.button == 1:
                print(f"Go to word details for '{word}'.")
            elif event.button == 2:
                pyperclip.copy(word)

    def action_close_all_sections(self) -> None:
        for section in self._active_sections.values():
            section.collapsed = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        id_ = event.control.id or ""
        key_bind = self.SidebarButtonManager.parse_button_id(id_)
        if widget := self._active_sections.get(key_bind, None):
            self._wa_scroll_to(collapsible=widget)

    def on_mouse_down(self, event: MouseDown) -> None:
        # Hacky way to get the event from an
        # inline-link action (ClickableSentence).
        self._current_click_event = event

    def on_mouse_up(self, _: MouseUp):
        self._current_click_event = None

    def on_key(self, event: Key) -> None:
        # Scroll the section if it's keyboard shortcut is pressed.
        if widget := self._active_sections.get(event.key, None):
            self._wa_scroll_to(collapsible=widget)

    # Misc Functions
    def _wa_scroll_to(self, *, collapsible: Collapsible) -> None:
        if collapsible.collapsed:
            collapsible.collapsed = False
        self.scroll_to_widget(collapsible, top=True)
