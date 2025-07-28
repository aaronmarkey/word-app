"""Module contains all the sources we pull language information from."""

from dataclasses import dataclass
from enum import IntEnum


@dataclass
class DataSource:
    """Base class for all data sources."""

    class Authentication(IntEnum):
        NONE = 0
        BASIC = 1

    id: str
    label_description: str
    label_name: str
    authentication: Authentication


DataMuseDataSource = DataSource(
    id="datamuse",
    label_description=(
        "Datamuse provides meta-information about words. "
        "For example: synonyms, related words."
    ),
    label_name="Datamuse",
    authentication=DataSource.Authentication.NONE,
)

WordnikDataSource = DataSource(
    id="wordnik",
    label_description=(
        "Wordnik provides definitions, examples, synonyms, antonyms, and more."
    ),
    label_name="Wordnik",
    authentication=DataSource.Authentication.BASIC,
)

DATA_SOURCES: list[DataSource] = [DataMuseDataSource, WordnikDataSource]
