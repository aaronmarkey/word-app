from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, HorizontalGroup, VerticalScroll
from textual.widgets import Button, Collapsible, Header, Footer, Label

from pydantic import BaseModel

from word_app.data.models import Word
from word_app.ext import WAScreen
from word_app.lex import EN_LANG
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

PhraseSection = WordDetailSection(
    title=EN_LANG.SIDEBAR_PHRASES_TITLE,
    desc=EN_LANG.SIDEBAR_PHRASES_DESCRIPTION,
    key_binding="3",
    css_class="phrase",
)


class WordDetailScreen(WAScreen):
    AUTO_FOCUS = ""
    BINDINGS = [POP_SCREEN.binding]

    WA_BINDING = "w"
    WA_ICON = "🗣️"
    WA_TITLE = "Word Details"

    def __init__(self, *, word: Word) -> None:
        super().__init__()
        self._word = word
        self.title = f"{self.WA_ICON}  {self._word.word}"

    @property
    def word(self) -> Word:
        return self._word

    def _compose_sidebar(self) -> ComposeResult:
        active_buttons: list[Button] = []
        inactive_buttons: list[Button] = []

        defb = SidebarButton(
            DefinitionSection.title,
            desc=DefinitionSection.desc,
            key_binding=DefinitionSection.key_binding,
        )
        theb = SidebarButton(
            ThesaurusSection.title,
            desc=ThesaurusSection.desc,
            key_binding=ThesaurusSection.key_binding,
        )
        phrb = SidebarButton(
            PhraseSection.title,
            desc=PhraseSection.desc,
            key_binding=PhraseSection.key_binding,
        )
        if self._word.definitions:
            active_buttons.append(defb)
        else:
            defb.disabled = True
            defb.tooltip = None
            inactive_buttons.append(defb)
        if self._word.thesaurus.has_data:
            active_buttons.append(theb)

        else:
            theb.disabled = True
            theb.tooltip = None
            inactive_buttons.append(theb)
        if self._word.phrases:
            active_buttons.append(phrb)
        else:
            phrb.disabled = True
            phrb.tooltip = None
            inactive_buttons.append(phrb)

        yield Sidebar(
            active_buttons + inactive_buttons, classes="with-header with-footer"
        )

    def _compose_content(self) -> ComposeResult:
        all_sections: list[Collapsible] = []
        if self._word.definitions:
            contents: Horizontal
            for definition in self._word.definitions:
                contents = Horizontal(
                    Label(
                        f"[i]{definition.part_of_speech}[/]: ",
                        classes="collapsible--pos",
                    ),
                    Label(definition.text, classes="collapsible--definition"),
                )
            defc = Collapsible(
                contents,
                title=DefinitionSection.title,
                collapsed=False,
            )
            all_sections.append(defc)

        yield VerticalScroll(*all_sections)

    def compose(self) -> ComposeResult:
        yield from self._compose_sidebar()
        yield from self._compose_content()

        h = Header(icon="")
        h.disabled = True
        yield h

        yield Footer()
