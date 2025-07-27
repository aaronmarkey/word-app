from textual.widgets import Static


def SectionStatic(text: str) -> Static:
    return Static(f"[b] {text} [/]", classes="section-static")
