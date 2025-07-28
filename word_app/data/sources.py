"""Module contains all the sources we pull language information from."""

from copy import deepcopy
from enum import IntEnum

from pydantic import BaseModel


class DataSource(BaseModel):
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

_AVAILABLE_DATA_SOURCES = [DataMuseDataSource, WordnikDataSource]


def get_available_data_sources(
    sources: list[DataSource] = _AVAILABLE_DATA_SOURCES,
) -> list[DataSource]:
    return deepcopy(sources)
