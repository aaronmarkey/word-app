from textual.app import ComposeResult
from textual.containers import HorizontalGroup, ItemGrid, VerticalScroll
from textual.events import Key
from textual.widget import Widget
from textual.widgets import Button, Collapsible, Footer, Header, Label, Rule

from pydantic import BaseModel

from word_app.data.language import WordDetailType
from word_app.data.models import Word, WordDetailContainer
from word_app.ext import WAScreen
from word_app.lex import EN_LANG, EN_LANG_FORMATS
from word_app.ui.navigation.common import POP_SCREEN
from word_app.ui.widgets import Sidebar, SidebarButton


class WordDetailSection(BaseModel):
    title: str
    desc: str
    key_binding: str
    css_class: str


DefinitionSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_DEFINITIONS_TITLE,
    desc=EN_LANG.SIDEBAR_DEFINITIONS_DESCRIPTION,
    key_binding="1",
    css_class="definition",
)

ThesaurusSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_THESAURUS_TITLE,
    desc=EN_LANG.SIDEBAR_THESAURUS_DESCRIPTION,
    key_binding="2",
    css_class="thesaurus",
)

RelatedSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_RELATED_TITLE,
    desc=EN_LANG.SIDEBAR_RELATED_DESCRIPTION,
    key_binding="3",
    css_class="related",
)

PhraseSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_PHRASES_TITLE,
    desc=EN_LANG.SIDEBAR_PHRASES_DESCRIPTION,
    key_binding="3",
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
        self.title = f"{self.WA_ICON}  {self._word.word}"

    # Composition
    def _compose_collapsible_grid(
        self,
        *,
        container: WordDetailContainer,
        section: WordDetailSection,
        allowed_types: list[WordDetailType],
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
                        Label(
                            f"[i][u]{allowed.value} ({len(nyms)})[/][/]:",
                            classes="collapsible--pos",
                        )
                    )

                    # Create a list of *nyms and calculate the longest word
                    # for column padding.
                    items: list[Label] = []
                    for nym in nyms:
                        if len(nym.text) > longest_word:
                            longest_word = len(nym.text)
                        items.append(Label(nym.text))
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

    def _compose_content(self) -> ComposeResult:
        all_sections: list[Collapsible] = []

        if defc := self._compose_definitions():
            all_sections.append(defc)
        if thec := self._compose_thesaurus():
            all_sections.append(thec)
        if relc := self._compose_related():
            all_sections.append(relc)

        yield VerticalScroll(*all_sections, classes="word-detail--content")

    def _compose_definitions(self) -> Collapsible | None:
        if self._word.definitions.has_value:
            labels = []

            attribution_text = EN_LANG_FORMATS.ATTRIBUTION.format(
                attr=self._word.definitions.source
            )
            labels.append(
                Label(
                    f"[i][u]{attribution_text}[/][/]",
                    classes="collapsible--attribution",
                )
            )

            i = 0
            keys = self._word.definitions.by_type.keys()
            values = self._word.definitions.by_type.values()
            for (
                part,
                details,
            ) in zip(keys, values):
                labels.append(
                    Label(
                        f"[i][u]{part}[/][/]: ",
                        classes="collapsible--pos",
                    )
                )
                for j, definition in enumerate(details):
                    horizontal = HorizontalGroup(
                        Label(f"[b]{j + 1}.[/]"),
                        Label(definition.text, classes="text"),
                        classes="collapsible--definition",
                    )
                    labels.append(horizontal)

                if i < len(keys) - 1:
                    labels.append(Rule())
                i += 1

            con = Collapsible(
                *labels,
                title=DefinitionSection.title,
                collapsed=False,
                classes="word-detail--container",
            )
            self._active_sections[DefinitionSection.key_binding] = con
            return con
        return None

    def _compose_related(self) -> Collapsible | None:
        return self._compose_collapsible_grid(
            container=self._word.thesaurus,
            section=RelatedSection,
            allowed_types=[
                WordDetailType.form,
                WordDetailType.inflected_form,
                WordDetailType.rhyme,
                WordDetailType.variant,
                WordDetailType.verb_form,
                WordDetailType.verb_stem,
            ],
        )

    def _compose_sidebar(self) -> ComposeResult:
        active_buttons: list[Button] = []
        inactive_buttons: list[Button] = []

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

        yield Sidebar(
            active_buttons + inactive_buttons, classes="with-header with-footer"
        )

    def _compose_thesaurus(self) -> Collapsible | None:
        # Allowed Types and order they are displayed.
        return self._compose_collapsible_grid(
            container=self._word.thesaurus,
            section=ThesaurusSection,
            allowed_types=[
                WordDetailType.synonym,
                WordDetailType.antonym,
                WordDetailType.hyponym,
                WordDetailType.hypernym,
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
    def action_close_all_sections(self) -> None:
        for section in self._active_sections.values():
            section.collapsed = True

    def on_key(self, event: Key) -> None:
        # Scroll the section if it's keyboard shortcut is pressed.
        if widget := self._active_sections.get(event.key, None):
            self._wa_scroll_to(collapsible=widget)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        id_ = event.control.id or ""
        key_bind = self.SidebarButtonManager.parse_button_id(id_)
        if widget := self._active_sections.get(key_bind, None):
            self._wa_scroll_to(collapsible=widget)

    # Misc Functions
    def _wa_scroll_to(self, *, collapsible: Collapsible) -> None:
        if collapsible.collapsed:
            collapsible.collapsed = False
        self.scroll_to_widget(collapsible, top=True)
