"""Module contains all the sources we pull language information from."""
from dataclasses import dataclass

@dataclass
class DataSource:
    """Base class for all data sources."""

    label_description: str = ""
    label_name: str = ""


DataMuseDataSource = DataSource(
    label_description=(
        "Datamuse provides meta-information about words. "
        "For example: synonyms, related words."
    ),
    label_name="Datamuse"
)

DATA_SOURCES: list[DataSource] = [DataMuseDataSource]
