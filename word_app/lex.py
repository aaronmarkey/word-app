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
)
