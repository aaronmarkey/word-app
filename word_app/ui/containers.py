from textual.widget import Widget


def ContainerWithBorderLabel(
    border_title: str, cls: type[Widget], *children: Widget
) -> Widget:
    container = cls(*children, classes="container-bordered")
    container.border_title = border_title
    return container
