"""Module contains all the sources we pull language information from."""

from copy import deepcopy
from enum import IntEnum

from pydantic import BaseModel

from word_app.lex import EN_LANG


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
    label_description=EN_LANG.DS_DATAMUSE_DESC,
    label_name=EN_LANG.DS_DATAMUSE_NAME,
    authentication=DataSource.Authentication.NONE,
)

WordnikDataSource = DataSource(
    id="wordnik",
    label_description=EN_LANG.DS_WORDNIK_DESC,
    label_name=EN_LANG.DS_WORDNIK_NAME,
    authentication=DataSource.Authentication.BASIC,
)

_AVAILABLE_DATA_SOURCES = [DataMuseDataSource, WordnikDataSource]


def get_available_data_sources(
    sources: list[DataSource] = _AVAILABLE_DATA_SOURCES,
) -> list[DataSource]:
    return deepcopy(sources)
