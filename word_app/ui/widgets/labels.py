from typing import Any

from textual.widgets import Label

from word_app.ui.constants import BOUND_KEY, HELP_HOVER_ICON


def WALabel(
    text: str,
    *,
    binding_key: str = "",
    lpadding: int = 0,
    rpadding: int = 0,
    separator: str = "",
    tooltip: str = "",
    styles: str = "",
    classes: str = "",
) -> Label:
    allowed_styles = {"b", "d", "i", "u", "s", "r"}
    styles = styles.lower()
    for style in styles:
        if style not in allowed_styles:
            raise ValueError(f"Invalid Label styles: '{style}'.")

    lt = f"{' ' * lpadding}{text}{' ' * rpadding}"

    if tooltip:
        lt += f" {HELP_HOVER_ICON}"

    if binding_key:
        lt = BOUND_KEY.format(key=binding_key) + f" {lt}"

    for style in styles:
        lt = f"[{style}]{lt}[/]"

    lt += separator

    # Mypy doesn't support dictionary unpacking, a basic Python feature.
    # Fucking worthless type checker.
    # So I have to use shit typing to get it to stop complaining about
    # something it shouldn't.
    options: dict[str, Any] = {}
    if classes:
        options["classes"] = classes

    label = Label(lt, **options)

    if tooltip:
        label.tooltip = tooltip

    return label
