from textual.widgets import Label

from word_app.ui.constants import BOUND_KEY, TOOLTIP_ICON


def WALabel(
    text: str,
    *,
    binding_key: str = "",
    lpadding: int = 0,
    rpadding: int = 0,
    separator: str = "",
    tooltip: str = "",
) -> Label:
    lt = f"{' ' * lpadding}{text}{' ' * rpadding}"

    if tooltip:
        lt += f" {TOOLTIP_ICON}"

    if binding_key:
        lt = BOUND_KEY.format(key=binding_key) + f" {lt}"

    lt += separator

    label = Label(lt)

    if tooltip:
        label.tooltip = tooltip

    return label
