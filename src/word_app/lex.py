import gettext
import locale
import pathlib
from dataclasses import dataclass
from typing import Final

frozen = dataclass(frozen=True, eq=True)


def configure_language() -> gettext.GNUTranslations:
    SUPPORTED_LOCALES: Final[tuple[str, ...]] = ("en_US",)
    APPNAME: Final[str] = "word_app"
    ABS_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent.resolve()
    LOCALE_DIR: Final[str] = "locales"

    fp = ABS_DIR / LOCALE_DIR
    lang, _ = locale.getlocale()

    if lang not in SUPPORTED_LOCALES:
        raise SystemExit(f"Unsupported language: '{lang}'.")

    translations = gettext.translation(
        APPNAME, fp, fallback=False, languages=[lang]
    )
    return translations


translations = configure_language()
translations.install()
_ = translations.gettext


@frozen
class Lexicon:
    """Container class for language strings.

    Check /word-app/word_app/locales for PO, POT, and MO files.
    """

    @frozen
    class app:
        @frozen
        class theme:
            light_name: str = _("app.theme.light_name")
            dark_name: str = _("app.theme.dark_name")

    @frozen
    class screen:
        @frozen
        class quick_search:
            failure_auth: str = _("screen.quick_search.failure_auth")
            help: str = _("screen.quick_search.help")
            tooltip: str = _("screen.quick_help.tooltip")
            no_matches: str = _("screen.quick_search.no_matches")
            placeholder: str = _("screen.quick_search.placeholder")

        @frozen
        class settings:
            desc: str = _("screen.settings.desc")
            ds_title: str = _("screen.settings.ds_title")
            title: str = _("screen.settings.title")

        @frozen
        class word_details:
            @frozen
            class sidebar:
                defs_title: str = _("screen.word_details.sidebar.defs_title")
                defs_desc: str = _("screen.word_details.sidebar.defs_desc")
                exam_title: str = _("screen.word_details.sidebar.exam_title")
                exam_desc: str = _("screen.word_details.sidebar.exam_desc")
                info_title: str = _("screen.word_details.sidebar.info_title")
                info_desc: str = _("screen.word_details.sidebar.info_desc")
                phra_title: str = _("screen.word_details.sidebar.phra_title")
                phra_desc: str = _("screen.word_details.sidebar.phra_desc")
                rela_title: str = _("screen.word_details.sidebar.rela_title")
                rela_desc: str = _("screen.word_details.sidebar.rela_desc")
                thes_title: str = _("screen.word_details.sidebar.thes_title")
                thes_desc: str = _("screen.word_details.sidebar.thes_desc")

            already_here: str = _("screen.word_details.already_here")

    @frozen
    class service:
        @frozen
        class datamuse:
            desc: str = _("service.datamuse.desc")
            name: str = _("service.datamuse.name")

        @frozen
        class worknik:
            desc: str = _("service.worknik.desc")
            name: str = _("service.worknik.name")

    @frozen
    class ui:
        @frozen
        class btn:
            back: str = _("ui.btn.back")
            close: str = _("ui.btn.close")
            close_all: str = _("ui.btn.close_all")

            help: str = _("ui.btn.help")
            quick_find: str = _("ui.btn.quick_find")
            go_to_bottom: str = _("ui.btn.go_to_bottom")
            go_to_top: str = _("ui.btn.go_to_top")
            next: str = _("ui.btn.next")
            next_page: str = _("ui.btn.next_page")
            prev: str = _("ui.btn.prev")
            prev_page: str = _("ui.btn.prev_page")

        @frozen
        class input:
            @frozen
            class placeholder:
                api_key: str = _("ui.input.placeholder.api_key")

        @frozen
        class label:
            attribution: str = _("ui.label.attribution")
            etymologies: str = _("ui.label.etymologies")
            error: str = _("ui.label.error")
            frequency: str = _("ui.label.frequency")
            information: str = _("ui.label.information")
            syllables: str = _("ui.label.syllables")
            word: str = _("ui.label.word")


@frozen
class FormattableLexicon:
    @frozen
    class screen:
        @frozen
        class word_details:
            attribution: str = _("screen.word_details.attribution")
            frequency_tooltip: str = _("screen.word.frequency_tooltip")


LEX = Lexicon()
LEX_FMT = FormattableLexicon()
