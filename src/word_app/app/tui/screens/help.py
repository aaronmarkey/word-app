from art import text2art
from textual.app import ComposeResult
from textual.containers import Grid, VerticalScroll
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Markdown


class HelpScreen(ModalScreen):
    """Modal screen with help information.."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;

        Button {
            column-span: 3;
            margin: 0 1;
            width: 100%;
        }

        Grid {
            grid-size: 3;
            grid-rows: 1fr 3;
            width: 60;
            height: auto;
            max-height: 90%;
            border: panel $foreground;
            background: $surface;
        }

        #content {
            column-span: 3;
            content-align: center middle;
            margin: 0;
            Label {
                width: 100%;
            }
        }

        #title {
            width: 100%;
            text-align: center;
            margin-top: 0;
            padding-top: 1;
        }
    }
    """

    class WIDGET_IDS:
        BUTTON = "close"
        CONTENT = "content"
        TITLE = "title"
        TEXT = "text"

    def __init__(
        self,
        text: str,
        *,
        title: str,
        button: str = "Close",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._button_title = button
        self._text = text
        self._title = title

    def _compose_button(self) -> Button:
        return Button(
            self._button_title, variant="primary", id=self.WIDGET_IDS.BUTTON
        )

    def _compose_text(self) -> Markdown:
        return Markdown(self._text, id=self.WIDGET_IDS.TEXT)

    def _compose_title(self) -> Label:
        title_text = text2art(self._title, font="roman")
        longest_line = 0
        current_line = 0
        for char in title_text:
            if char == "\n":
                if current_line > longest_line:
                    longest_line = current_line
                current_line = 0
            else:
                current_line += 1
        title_text = f"[$foreground]{title_text}{'_' * longest_line}[/]"
        return Label(title_text, id=self.WIDGET_IDS.TITLE)

    def compose(self) -> ComposeResult:
        yield Grid(
            VerticalScroll(
                self._compose_title(),
                self._compose_text(),
                id=self.WIDGET_IDS.CONTENT,
            ),
            self._compose_button(),
        )

    # Event handlers
    def on_button_pressed(self) -> None:
        self.app.pop_screen()

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            event.stop()
            self.app.pop_screen()
