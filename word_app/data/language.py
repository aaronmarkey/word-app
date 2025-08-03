from __future__ import annotations
from enum import StrEnum


class WordDetailType(StrEnum):
    antonym = "antonym"
    cross_reference = "cross-reference"
    equivalent = "equivalent"
    etymologically_related_term = "etymologically-related-term"
    form = "form"
    has_topic = "has_topic"
    hypernym = "hypernym"
    hyponym = "hyponym"
    inflected_form = "inflected-form"
    primary = "primary"
    related_word = "related-word"
    rhyme = "rhyme"
    same_context = "same-context"
    suggests = "suggests"
    synonym = "synonym"
    variant = "variant"
    verb_form = "verb-form"
    verb_stem = "verb-stem"

    @classmethod
    def all(cls) -> list[WordDetailType]:
        return list(cls)
