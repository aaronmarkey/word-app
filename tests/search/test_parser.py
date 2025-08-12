import pytest

from word_app.search import parser


@pytest.mark.parametrize(
    "query, expected_type",
    [
        # Seach by spelling
        ("a***e", parser.SearchTermType.SPELLED_LIKE),
        ("a?", parser.SearchTermType.SPELLED_LIKE),
        ("?a", parser.SearchTermType.SPELLED_LIKE),
        ("A***E", parser.SearchTermType.SPELLED_LIKE),
        ("A?", parser.SearchTermType.SPELLED_LIKE),
        ("?A", parser.SearchTermType.SPELLED_LIKE),
        # Seach by sounds-like and auto-complete
        ("apple", parser.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("ap", parser.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("ap0", parser.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("ap9", parser.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("AP", parser.SearchTermType.SUGGEST_SOUNDS_LIKE),
        ("AP0", parser.SearchTermType.SUGGEST_SOUNDS_LIKE),
        # Seach by means-like and auto-complete
        ("apple ", parser.SearchTermType.SUGGEST_MEANS_LIKE),
        ("app ", parser.SearchTermType.SUGGEST_MEANS_LIKE),
        ("apple-core", parser.SearchTermType.SUGGEST_MEANS_LIKE),
        ("apple-core ", parser.SearchTermType.SUGGEST_MEANS_LIKE),
        ("APPLE-CORE ", parser.SearchTermType.SUGGEST_MEANS_LIKE),
        # Unknown
        ("%4dasdf", parser.SearchTermType.UNKNOWN),
        ("%4dASaf", parser.SearchTermType.UNKNOWN),
    ],
)
def test__RegexSearchTermParser__parse(query, expected_type):
    search_term_parser = parser.RegexSearchTermParser()
    result = search_term_parser.parse(query)
    assert parser.ParseResult(type=expected_type, text=query.lower()) == result
