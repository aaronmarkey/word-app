class HtmlToMarkup:
    HTML_TO_TAG = {
        "<em>": "[i]",
        "</em>": "[/i]",
        "<strong>": "[b]",
        "</strong>": "[/b]",
        "<p>": "",
        "</p>": "",
    }

    @classmethod
    def transform(cls, text: str) -> str:
        new_text = text
        for html, tag in cls.HTML_TO_TAG.items():
            new_text = new_text.replace(html, tag)

        return new_text


def hoverable(title: str, *styles: str) -> str:
    vis = f"[$user-action]<{title}>"
    for style in reversed(styles):
        vis = f"[{style}]{vis}[/]"
    return vis
