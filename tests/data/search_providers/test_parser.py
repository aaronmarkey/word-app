import pytest

from word_app.data.search_providers import models
from word_app.data.search_providers import parser


@pytest.mark.parametrize(
    "query, expected_type",
    [
        # Seach by spelling
        ("a***e", models.SearchTermType.SPELLED_LIKE),
        ("a?", models.SearchTermType.SPELLED_LIKE),
        ("?a", models.SearchTermType.SPELLED_LIKE),
        ("A***E", models.SearchTermType.SPELLED_LIKE),
        ("A?", models.SearchTermType.SPELLED_LIKE),
        ("?A", models.SearchTermType.SPELLED_LIKE),
        # Seach by sounds-like and auto-complete
        ("apple", models.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("ap", models.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("ap0", models.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("ap9", models.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("AP", models.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("AP0", models.SearchTermType.SUGGEST_SOUNDS_LIKE),
        # Seach by means-like and auto-complete
        ("apple ", models.SearchTermType.SUGGEST_MEANS_LIKE),
        ("app ", models.SearchTermType.SUGGEST_MEANS_LIKE),
        ("apple-core", models.SearchTermType.SUGGEST_MEANS_LIKE),
        ("apple-core ", models.SearchTermType.SUGGEST_MEANS_LIKE),
        ("APPLE-CORE ", models.SearchTermType.SUGGEST_MEANS_LIKE),
        # Unknown
        ("%4dasdf", models.SearchTermType.UNKNOWN),
        ("%4dASaf", models.SearchTermType.UNKNOWN),
    ],
)
def test__RegexSearchTermParser__parse(query, expected_type):
    search_term_parser = parser.RegexSearchTermParser()
    result = search_term_parser.parse(query)
    assert parser.ParseResult(type=expected_type, text=query.lower()) == result
