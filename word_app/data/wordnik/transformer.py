from word_app.data.grammar import ALL_GRAMMARS, Grammar
from word_app.data.models import Definition, Nym


class WordnikTransformer:
    HTML_TO_TAG = {
        "<em>": "[i]",
        "</em>": "[/i]",
        "<strong>": "[b]",
        "</strong>": "[/b]",
    }

    POS_TO_GRAMMAR: dict[str, Grammar] = {
        g.title.lower().replace(" ", "-"): g for g in ALL_GRAMMARS
    }

    @classmethod
    def definition(cls, response) -> Definition | None:
        if response.partOfSpeech and response.text:
            text = cls.html_to_tag(response.text)
            if type_ := cls.POS_TO_GRAMMAR.get(response.partOfSpeech, None):
                return Definition(type=type_, text=text)
        return None

    @classmethod
    def html_to_tag(cls, text: str) -> str:
        new_text = text
        for html, tag in cls.HTML_TO_TAG.items():
            new_text = new_text.replace(html, tag)

        return new_text

    @classmethod
    def nyms(cls, response) -> list[Nym]:
        _type = response.relationshipType.lower()
        _type = cls.POS_TO_GRAMMAR.get(_type, None)
        if _type:
            return [
                Nym(text=word, type=_type) for word in response.words if word
            ]
        return []
