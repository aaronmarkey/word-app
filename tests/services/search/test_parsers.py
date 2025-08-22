import pytest

from word_app.data.vo import SearchTermType
from word_app.services.search.base import ParseResult
from word_app.services.search.parsers import RegexSearchTermParser


@pytest.mark.parametrize(
    "query, expected_type",
    [
        # Seach by spelling
        ("a***e", SearchTermType.SPELLED_LIKE),
        ("a?", SearchTermType.SPELLED_LIKE),
        ("?a", SearchTermType.SPELLED_LIKE),
        ("A***E", SearchTermType.SPELLED_LIKE),
        ("A?", SearchTermType.SPELLED_LIKE),
        ("?A", SearchTermType.SPELLED_LIKE),
        # Seach by sounds-like and auto-complete
        ("apple", SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("ap", SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("ap0", SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("ap9", SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("AP", SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("AP0", SearchTermType.SUGGEST_SOUNDS_LIKE),
        # Seach by means-like and auto-complete
        ("apple ", SearchTermType.SUGGEST_MEANS_LIKE),
        ("app ", SearchTermType.SUGGEST_MEANS_LIKE),
        ("apple-core", SearchTermType.SUGGEST_MEANS_LIKE),
        ("apple-core ", SearchTermType.SUGGEST_MEANS_LIKE),
        ("APPLE-CORE ", SearchTermType.SUGGEST_MEANS_LIKE),
        # Unknown
        ("%4dasdf", SearchTermType.UNKNOWN),
        ("%4dASaf", SearchTermType.UNKNOWN),
    ],
)
def test__RegexSearchTermParser__parse(query, expected_type):
    search_term_parser = RegexSearchTermParser()
    result = search_term_parser.parse(query)
    assert ParseResult(type=expected_type, text=query.lower()) == result
