from dataclasses import dataclass


@dataclass
class Lexicon:
    BACK: str

    DS_DATAMUSE_DESC: str
    DS_DATAMUSE_NAME: str
    DS_WORDNIK_DESC: str
    DS_WORDNIK_NAME: str

    INPUT_API_KEY_PLACEHOLDER: str

    SETTINGS_SCREEN_DESC: str
    SETTINGS_SCREEN_SECTION_DS_TITLE: str
    SETTINGS_SCREEN_TITLE: str

    SIDEBAR_DEFINITIONS_TITLE: str
    SIDEBAR_DEFINITIONS_DESCRIPTION: str
    SIDEBAR_THESAURUS_TITLE: str
    SIDEBAR_THESAURUS_DESCRIPTION: str
    SIDEBAR_PHRASES_TITLE: str
    SIDEBAR_PHRASES_DESCRIPTION: str


EN_LANG = Lexicon(
    BACK="Back",
    DS_DATAMUSE_DESC=(
        "Datamuse provides meta-information about words. "
        "For example: synonyms, related words."
    ),
    DS_DATAMUSE_NAME="Datamuse",
    DS_WORDNIK_DESC=(
        "Wordnik provides definitions, examples, synonyms, antonyms, and more."
    ),
    DS_WORDNIK_NAME="Wordnik",
    INPUT_API_KEY_PLACEHOLDER="EnterAPI Key",
    SETTINGS_SCREEN_DESC="Configure the application.",
    SETTINGS_SCREEN_SECTION_DS_TITLE="Data Sources",
    SETTINGS_SCREEN_TITLE="Settings",
    SIDEBAR_DEFINITIONS_TITLE="Definitions",
    SIDEBAR_DEFINITIONS_DESCRIPTION="Definitions of the word.",
    SIDEBAR_THESAURUS_TITLE="Thesaurus",
    SIDEBAR_THESAURUS_DESCRIPTION="Synonyms, antonyms, hyponyms, and hypernyms of the word.",
    SIDEBAR_PHRASES_TITLE="Examples",
    SIDEBAR_PHRASES_DESCRIPTION="Example phrases containing the word.",
)
