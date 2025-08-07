from dataclasses import dataclass


@dataclass
class FormattableLexicon:
    ATTRIBUTION: str
    FREQUENCY_TOOLTIP: str


@dataclass
class Lexicon:
    BACK: str
    ETYMOLOGIES: str
    FREQUENCY: str
    SYLLABLES: str
    WORD: str

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
    SIDEBAR_EXAMPLES_TITLE: str
    SIDEBAR_EXAMPLES_DESCRIPTION: str
    SIDEBAR_INFO_TITLE: str
    SIDEBAR_INFO_DESCRIPTION: str
    SIDEBAR_PHRASES_TITLE: str
    SIDEBAR_PHRASES_DESCRIPTION: str
    SIDEBAR_RELATED_TITLE: str
    SIDEBAR_RELATED_DESCRIPTION: str
    SIDEBAR_THESAURUS_TITLE: str
    SIDEBAR_THESAURUS_DESCRIPTION: str

    WD_CLOSE_ALL_SECTIONS: str


EN_LANG = Lexicon(
    BACK="Back",
    ETYMOLOGIES="Etymologies",
    FREQUENCY="Frequency",
    SYLLABLES="Syllables",
    WORD="Word",
    DS_DATAMUSE_DESC=(
        "Datamuse provides meta-information about words. "
        "For example: synonyms, related words."
    ),
    DS_DATAMUSE_NAME="Datamuse",
    DS_WORDNIK_DESC=(
        "Wordnik provides definitions, examples, synonyms, antonyms, and more."
    ),
    DS_WORDNIK_NAME="Wordnik",
    INPUT_API_KEY_PLACEHOLDER="Enter API Key",
    SETTINGS_SCREEN_DESC="Configure the application.",
    SETTINGS_SCREEN_SECTION_DS_TITLE="Data Sources",
    SETTINGS_SCREEN_TITLE="Settings",
    SIDEBAR_DEFINITIONS_TITLE="Definitions",
    SIDEBAR_DEFINITIONS_DESCRIPTION="Definitions of the word.",
    SIDEBAR_EXAMPLES_TITLE="Examples",
    SIDEBAR_EXAMPLES_DESCRIPTION="Example sentences using the word.",
    SIDEBAR_INFO_TITLE="Information",
    SIDEBAR_INFO_DESCRIPTION="Syllable, etymology, and historical frequency information.",
    SIDEBAR_PHRASES_TITLE="Phrases",
    SIDEBAR_PHRASES_DESCRIPTION="Idiomatic phrases containing the word.",
    SIDEBAR_RELATED_DESCRIPTION="Related words and word forms.",
    SIDEBAR_RELATED_TITLE="Related",
    SIDEBAR_THESAURUS_TITLE="Thesaurus",
    SIDEBAR_THESAURUS_DESCRIPTION="Synonyms, antonyms, hyponyms, and hypernyms of the word.",
    WD_CLOSE_ALL_SECTIONS="Collapse All",
)
EN_LANG_FORMATS = FormattableLexicon(
    ATTRIBUTION="from {attr}.",
    FREQUENCY_TOOLTIP=(
        "Frequency of the word's usage in English texts "
        "between the years {start} and {end}."
    ),
)
