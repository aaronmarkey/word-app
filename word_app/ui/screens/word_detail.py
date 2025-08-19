from statistics import mean

import pyperclip
from pydantic import BaseModel
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
from word_app.lex import LEX, LEX_FMT
from word_app.ui.constants import HELP_HOVER_ICON
from word_app.ui.utils import hoverable
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
    id: str


InformationSection = WordDetailSection(
    title=LEX.screen.word_details.sidebar.info_title,
    desc=LEX.screen.word_details.sidebar.info_desc,
    key_binding="1",
    css_class="information",
    id="section-information",
)

DefinitionSection = WordDetailSection(
    title=LEX.screen.word_details.sidebar.defs_title,
    desc=LEX.screen.word_details.sidebar.defs_desc,
    key_binding="2",
    css_class="definition",
    id="section-definition",
)

ThesaurusSection = WordDetailSection(
    title=LEX.screen.word_details.sidebar.thes_title,
    desc=LEX.screen.word_details.sidebar.thes_desc,
    key_binding="3",
    css_class="thesaurus",
    id="section-thesaurus",
)

RelatedSection = WordDetailSection(
    title=LEX.screen.word_details.sidebar.rela_title,
    desc=LEX.screen.word_details.sidebar.rela_desc,
    key_binding="4",
    css_class="related",
    id="section-related",
)

ExampleSection = WordDetailSection(
    title=LEX.screen.word_details.sidebar.exam_title,
    desc=LEX.screen.word_details.sidebar.exam_desc,
    key_binding="5",
    css_class="example",
    id="section-example",
)

PhraseSection = WordDetailSection(
    title=LEX.screen.word_details.sidebar.phra_title,
    desc=LEX.screen.word_details.sidebar.phra_desc,
    key_binding="6",
    css_class="phrase",
    id="section-phrase",
)


def _make_attribution(*attributions: str) -> str:
    no_repeats = set(attributions)
    return ", ".join(no_repeats)


class WordDetailScreen(WAScreen):
    AUTO_FOCUS = ""
    BINDINGS = [
        ("escape", "app.pop_screen", LEX.ui.btn.back),
        ("-", "close_all_sections", LEX.ui.btn.close_all),
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
        id: str = "",
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
                id=id,
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
        id: str = "",
    ) -> Collapsible | None:
        if container.has_value:
            labels: list[Widget] = []

            if include_attribution:
                attr_tooltip = _make_attribution(
                    *[w.attribution for w in container.details]
                )
                if attr_tooltip:
                    attr_text = hoverable(LEX.ui.label.attribution)
                    attr = WALabel(
                        attr_text, classes="collapsible--attribution"
                    )
                    attr.tooltip = attr_tooltip
                    labels.append(attr)

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
                id=id,
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
            id=DefinitionSection.id,
        )

    def _compose_examples(self) -> Collapsible | None:
        return self._compose_collapsible_list(
            container=self._word.examples,
            section=ExampleSection,
            include_attribution=False,
            id=ExampleSection.id,
        )

    def _compose_information(self) -> Collapsible | None:
        elements: list[Widget] = []

        elements.append(
            Label(
                f"[i][b]{LEX.ui.label.word}[/][/]: {self._word.word}",
            )
        )

        if self._word.syllables.has_value:
            elements.append(
                Label(
                    f"[i][b]{LEX.ui.label.syllables}[/][/]: "
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
                    LEX.ui.label.etymologies,
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
                    f"{LEX.ui.label.frequency} {HELP_HOVER_ICON}",
                    classes=label_css,
                    separator=": ",
                    styles="ib",
                )
                flabel.tooltip = (
                    LEX_FMT.screen.word_details.frequency_tooltip.format(
                        start=in_order[0].start,
                        end=in_order[-1].end,
                    )
                )
                elements.append(flabel)
                elements.append(
                    Sparkline(
                        [freq.value for freq in in_order], summary_function=mean
                    )
                )

        con = Collapsible(
            *elements,
            title=InformationSection.title,
            collapsed=False,
            classes="word-detail--container",
            id=InformationSection.id,
        )
        self._active_sections[InformationSection.key_binding] = con
        return con

    def _compose_phrases(self) -> Collapsible | None:
        return self._compose_collapsible_list(
            container=self._word.phrases,
            section=PhraseSection,
            include_attribution=False,
            id=PhraseSection.id,
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
            id=RelatedSection.id,
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
        section_ids = {w.id for w in self._active_sections.values()}
        pairs = (
            (InformationSection, infb),
            (DefinitionSection, defb),
            (ThesaurusSection, theb),
            (RelatedSection, relb),
            (ExampleSection, exab),
            (PhraseSection, phrb),
        )

        for section, btn in pairs:
            if section.id in section_ids:
                active_buttons.append(btn)
            else:
                btn.disabled = True
                btn.tooltip = None
                inactive_buttons.append(btn)

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
            id=ThesaurusSection.id,
        )

    def compose(self) -> ComposeResult:
        yield from self._compose_content()
        yield from self._compose_sidebar()

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
