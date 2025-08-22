from __future__ import annotations

from asyncio import (
    CancelledError,
    Queue,
    TimeoutError,
    create_task,
    wait,
    wait_for,
)
from dataclasses import dataclass
from inspect import isclass
from operator import attrgetter
from time import monotonic
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    ClassVar,
    Final,
    Iterable,
)

from rich.align import Align
from rich.text import Text
from textual import on, work
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical
from textual.content import Content
from textual.events import Click, Key, Mount
from textual.keys import Keys
from textual.message import Message
from textual.reactive import var
from textual.screen import ModalScreen, Screen, ScreenResultType
from textual.style import Style
from textual.timer import Timer
from textual.widgets import (
    Button,
    Footer,
    Input,
    Label,
    LoadingIndicator,
    OptionList,
)
from textual.widgets.option_list import Option
from textual.worker import get_current_worker

if TYPE_CHECKING:
    from textual.app import ComposeResult

from word_app.app.tui._models import Hit, Hits
from word_app.app.tui.constants import HELP_HCLICK_ICON
from word_app.app.tui.screens.help import HelpScreen
from word_app.app.tui.screens.quick_search.suggestion_provider import (
    Provider,
    ProviderSource,
)
from word_app.app.tui.widgets import (
    Suggestion,
    SuggestionIcon,
    SuggestionInput,
    SuggestionList,
)
from word_app.lex import LEX


class SuggestionPalette(ModalScreen[ScreenResultType], inherit_css=False):
    """The Suggetion Palette."""

    AUTO_FOCUS = "SuggestionInput"

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "suggestion-palette--help-text",
        "suggestion-palette--highlight",
        "screen--selection",
    }

    DEFAULT_CSS = """
    SuggestionPalette {
        color: $foreground;
        background: $foreground 10%;
        align-horizontal: center;

        #--container {
            display: none;
        }

        &:ansi {
            background: transparent;
        }
    }

    SuggestionPalette.-ready {
        #--container {
            display: block;
            width: 50%;
        }
    }

    SuggestionPalette > .suggestion-palette--help-text {
        color: $text-muted;
        background: transparent;
        text-style: not bold;
    }

    SuggestionPalette > .suggestion-palette--highlight {
        text-style: bold underline;
    }

    SuggestionPalette:nocolor > .suggestion-palette--highlight {
        text-style: underline;
    }

    SuggestionPalette > Vertical {
        margin-top: 1;
        height: 100%;
        visibility: hidden;
        background: $surface;
        &:dark {
            background: $panel-darken-1;
        }
    }

    SuggestionPalette #--input {
        height: auto;
        visibility: visible;
        border: outer $user-action;
    }

    SuggestionPalette #--input.--list-visible {
        border-bottom: none;
    }

    SuggestionPalette #--input Label {
        margin-top: 1;
        margin-left: 1;
    }

    SuggestionPalette #--input Button {
        min-width: 7;
        margin-right: 1;
    }

    SuggestionPalette #--results {
        overlay: screen;
        height: auto;
    }

    SuggestionPalette LoadingIndicator {
        height: auto;
        visibility: hidden;
        border-bottom: hkey $border;
    }

    SuggestionPalette LoadingIndicator.--visible {
        visibility: visible;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "ctrl+end, shift+end",
            "suggestion_list('last')",
            LEX.ui.btn.go_to_bottom,
            show=False,
        ),
        Binding(
            "ctrl+home, shift+home",
            "suggestion_list('first')",
            LEX.ui.btn.go_to_top,
            show=False,
        ),
        Binding("down", "cursor_down", LEX.ui.btn.next, show=False),
        Binding("escape", "escape", LEX.ui.btn.back),
        Binding("ctrl+h", "show_help", LEX.ui.btn.help),
        Binding(
            "pagedown",
            "suggestion_list('page_down')",
            LEX.ui.btn.next_page,
            show=False,
        ),
        Binding(
            "pageup",
            "suggestion_list('page_up')",
            LEX.ui.btn.prev_page,
            show=False,
        ),
        Binding(
            "up",
            "suggestion_list('cursor_up')",
            LEX.ui.btn.prev,
            show=False,
        ),
    ]

    _BELOW_CLASS = "below"
    """Class added to screens below the palette."""

    _BUSY_COUNTDOWN: Final[float] = 0.5
    """How many seconds to wait for hits to come in before showing busy."""

    _GATHER_SUGGESTIONS_GROUP: Final[str] = (
        "--suggestion-palette-gather-suggestions"
    )
    """The group name of the suggestion gathering worker."""

    _NO_MATCHES: Final[str] = "--no-matches"
    """The ID to give the disabled option that shows there were no matches."""

    _NO_MATCHES_COUNTDOWN: Final[float] = 0.5
    """How many seconds to wait before showing 'No matches found'."""

    _RESULT_BATCH_TIME: Final[float] = 0.25
    """How long to wait before adding suggestions to the suggestion list."""

    _list_visible: var[bool] = var(False, init=False)
    """Internal reactive to toggle the visibility of the suggestion list."""

    _show_busy: var[bool] = var(False, init=False)
    """Internal reactive to toggle the visibility of the busy indicator."""

    _calling_screen: var[Screen[Any] | None] = var(None)
    """A record of the screen that was active when we were called."""

    # Events
    @dataclass
    class OptionHighlighted(Message):
        """Posted to App when an option is highlighted in the palette."""

        highlighted_event: OptionList.OptionHighlighted
        """The option highlighted event from the OptionList within the palette."""

    @dataclass
    class Opened(Message):
        """Posted to App when the palette is opened."""

    @dataclass
    class Closed(Message):
        """Posted to App when the palette is closed."""

        option_selected: bool
        """True if an option was selected, False if the palette was closed without selecting an option."""

    # Static methods
    @staticmethod
    async def _consume(hits: Hits, suggestions: Queue[Hit]) -> None:
        """Consume a source of matching suggestions, feeding the given queue.

        Args:
            hits: The hits to consume.
            suggestions: The suggestion queue to feed.
        """
        async for hit in hits:
            await suggestions.put(hit)

    def __init__(
        self,
        providers: ProviderSource = [],
        *,
        placeholder: str = "Enter term…",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the palette.

        Args:
            providers: An optional list of providers to use.
            placeholder: The placeholder text for the palette.
        """
        super().__init__(
            id=id,
            classes=classes,
            name=name,
        )
        self.add_class("--suggestion-palette")

        self._selected_suggestion: Hit | None = None
        """The suggestion that was selected by the user."""

        self._busy_timer: Timer | None = None
        """Keeps track of if there's a busy indication timer in effect."""

        self._no_matches_timer: Timer | None = None
        """
        Keeps track of if there are 'No matches found' message waiting
        to be displayed.
        """

        self._supplied_providers: ProviderSource = providers

        self._providers: list[Provider] = []
        """List of Provider instances involved in searches."""

        self._hit_count: int = 0
        """Number of hits displayed."""

        self._placeholder = placeholder

    # Properties
    @property
    def _provider_classes(self) -> set[type[Provider]]:
        """The currently available providers."""

        def get_providers(
            provider_source: ProviderSource,
        ) -> Iterable[type[Provider]]:
            """Load the providers from a source.

            Args:
                provider_source: The source of providers.

            Returns:
                An iterable of providers.
            """
            for provider in provider_source:
                if isclass(provider) and issubclass(provider, Provider):
                    yield provider
                else:
                    # Lazy loaded providers
                    yield provider()  # type: ignore

        return {*get_providers(self._supplied_providers)}

    # Private methods
    def _cancel_gather_suggestions(self) -> None:
        """Cancel any operation that is gather suggestions."""
        self.workers.cancel_group(self, self._GATHER_SUGGESTIONS_GROUP)

    def _refresh_suggestion_list(
        self,
        suggestion_list: SuggestionList,
        suggestions: list[Suggestion],
    ) -> None:
        """Refresh the suggestion list.

        Args:
            suggestion_list: The widget that shows the list of suggestions.
            suggestions: The suggestions to show in the widget.
        """

        sorted_suggestions = sorted(
            suggestions, key=attrgetter("hit.score"), reverse=True
        )
        suggestion_list.clear_options().add_options(sorted_suggestions)

        if sorted_suggestions:
            suggestion_list.highlighted = 0

        self._list_visible = bool(suggestion_list.option_count)
        self._hit_count = suggestion_list.option_count

    async def _search_for(self, search_value: str) -> AsyncGenerator[Hit, bool]:
        """Search for a given search value amongst all of the providers.

        Args:
            search_value: The value to search for.

        Yields:
            The hits made amongst the registered providers.
        """

        # Set up a queue to stream in the hits from all the providers.
        suggestions: Queue[Hit] = Queue()

        # Fire up an instance of each provider, inside a task, and
        # have them go start looking for matches.
        searches = [
            create_task(
                self._consume(
                    provider._search(search_value),
                    suggestions,
                )
            )
            for provider in self._providers
        ]
        # Set up a delay for showing that we're busy.
        self._start_busy_countdown()

        # Assume the search isn't aborted.
        aborted = False

        # Now, while there's some task running...
        while not aborted and any(not search.done() for search in searches):
            try:
                # ...briefly wait for something on the stack. If we get
                # something yield it up to our caller.
                aborted = yield await wait_for(suggestions.get(), 0.1)
            except TimeoutError:
                # A timeout is fine. We're just going to go back round again
                # and see if anything else has turned up.
                pass
            except CancelledError:
                # A cancelled error means things are being aborted.
                aborted = True
            else:
                # There was no timeout, which means that we managed to yield
                # up that suggestions; we're done with it so let the queue know.
                suggestions.task_done()

        # Check through all the finished searches, see if any have
        # exceptions, and log them. In most other circumstances we'd
        # re-raise the exception and quit the application, but the decision
        # has been made to find and log exceptions with providers.
        #
        # https://github.com/Textualize/textual/pull/3058#discussion_r1310051855
        for search in searches:
            if search.done():
                exception = search.exception()
                if exception is not None:
                    from rich.traceback import Traceback

                    self.log.error(
                        Traceback.from_exception(
                            type(exception), exception, exception.__traceback__
                        )
                    )

        # Having finished the main processing loop, we're not busy any more.
        # Anything left in the queue (see next) will fall out more or less
        # instantly. If we're aborted, that means a fresh search is incoming
        # and it'll have cleaned up the countdown anyway, so don't do that
        # here as they'll be a clash.
        if not aborted:
            self._stop_busy_countdown()

        # If all the providers are pretty fast it could be that we've reached
        # this point but the queue isn't empty yet. So here we flush the
        # queue of anything left.
        while not aborted and not suggestions.empty():
            aborted = yield await suggestions.get()

        # If we were aborted, ensure that all of the searches are cancelled.
        if aborted:
            for search in searches:
                search.cancel()

    def _start_busy_countdown(self) -> None:
        """Start a countdown to showing that we're busy searching."""
        self._stop_busy_countdown()

        def _become_busy() -> None:
            if self._list_visible:
                self._show_busy = True

        self._busy_timer = self.set_timer(self._BUSY_COUNTDOWN, _become_busy)

    def _stop_busy_countdown(self) -> None:
        """Stop any busy countdown that's in effect."""
        if self._busy_timer is not None:
            self._busy_timer.stop()
            self._busy_timer = None

    def _stop_no_matches_countdown(self) -> None:
        """Stop any 'No matches' countdown that's in effect."""
        if self._no_matches_timer is not None:
            self._no_matches_timer.stop()
            self._no_matches_timer = None

    def _start_no_matches_countdown(self, search_value: str) -> None:
        """Start a countdown to showing that there are no matches for the query.

        Args:
            search_value: The value being searched for.

        Adds a 'No matches found' option to the suggestion list after
        `_NO_MATCHES_COUNTDOWN` seconds.
        """
        self._stop_no_matches_countdown()

        def _show_no_matches() -> None:
            # If we were actually searching for something, show that we
            # found no matches.
            if search_value:
                suggestion_list = self.query_one(SuggestionList)
                suggestion_list.add_option(
                    Option(
                        Align.center(
                            Text(
                                LEX.screen.quick_search.no_matches,
                                style="not bold",
                            )
                        ),
                        disabled=True,
                        id=self._NO_MATCHES,
                    )
                )
                self._list_visible = True
            else:
                self._list_visible = False

        self._no_matches_timer = self.set_timer(
            self._NO_MATCHES_COUNTDOWN,
            _show_no_matches,
        )

    def _watch__list_visible(self) -> None:
        """React to the list visible flag being toggled."""
        self.query_one(SuggestionList).set_class(
            self._list_visible, "--visible"
        )
        self.query_one("#--input", Horizontal).set_class(
            self._list_visible, "--list-visible"
        )
        if not self._list_visible:
            self._show_busy = False

    async def _watch__show_busy(self) -> None:
        """React to the show busy flag being toggled.

        This watcher adds or removes a busy indication depending on the
        flag's state.
        """
        self.query_one(LoadingIndicator).set_class(self._show_busy, "--visible")
        self.query_one(SuggestionList).set_class(
            self._show_busy, "--populating"
        )

    # Public methods
    def compose(self) -> ComposeResult:
        """Compose the palette.

        Returns:
            The content of the screen.
        """
        help_label = Label(HELP_HCLICK_ICON, id="help-icon")
        help_label.tooltip = LEX.screen.quick_search.tooltip
        with Vertical(id="--container"):
            with Horizontal(id="--input"):
                yield SuggestionIcon()
                yield help_label
                yield SuggestionInput(
                    placeholder=self._placeholder, select_on_focus=False
                )
            with Vertical(id="--results"):
                yield SuggestionList()
                yield LoadingIndicator()
        yield Footer()

    # Event handlers
    @on(Input.Changed)
    def _input(self, event: Input.Changed) -> None:
        """Listen to Input.Changed."""
        event.stop()
        self._cancel_gather_suggestions()
        self._stop_no_matches_countdown()
        self._gather_suggestions(event.value.strip())

    def _on_click(self, event: Click) -> None:  # type: ignore[override]
        """Handle the click events"""
        if w := event.widget:
            if w.id == "help-icon":
                self._action_show_help()

        if self.get_widget_at(event.screen_x, event.screen_y)[0] is self:
            self._cancel_gather_suggestions()
            self.app.post_message(
                SuggestionPalette.Closed(option_selected=False)
            )
            self.dismiss()

    async def _on_key(self, event: Key) -> None:
        """Handle key events."""
        if event.character == "\x08" or event.key == Keys.ControlH.value:
            self._action_show_help()

    def _on_mount(self, event: Mount) -> None:
        """Configure the palette once the DOM is ready."""
        self.app.post_message(SuggestionPalette.Opened())
        self._calling_screen = self.app.screen_stack[-2]
        self._calling_screen.add_class(self._BELOW_CLASS)

        match_style = self.get_visual_style(
            "suggestion-palette--highlight", partial=True
        )

        assert self._calling_screen is not None
        self._providers = [
            provider_class(self._calling_screen, match_style)
            for provider_class in self._provider_classes
        ]
        for provider in self._providers:
            provider._post_init()
        self._gather_suggestions("")

    async def _on_unmount(self) -> None:  # type: ignore[override]
        """Shutdown providers when palette is closed."""
        if self._providers:
            await wait(
                [
                    create_task(provider._shutdown())
                    for provider in self._providers
                ],
            )
            self._providers.clear()
        if screen := self._calling_screen:
            screen.remove_class(self._BELOW_CLASS)

    @on(Input.Submitted)
    @on(Button.Pressed)
    def _select_or_suggest(
        self, event: Input.Submitted | Button.Pressed | None = None
    ) -> None:
        """Depending on context, select or execute a suggestion."""
        # If the list is visible, that means we're in "pick a suggetion"
        # mode...
        if event is not None:
            event.stop()
        if self._list_visible:
            suggestion_list = self.query_one(SuggestionList)
            # ...so if nothing in the list is highlighted yet...
            if suggestion_list.highlighted is None:
                # ...cause the first completion to be highlighted.
                self._action_cursor_down()
                # If there is one option, assume the user wants to select it
                if suggestion_list.option_count == 1:
                    # Call after a short delay to provide a little visual feedback
                    self._action_suggestion_list("select")
            else:
                # The list is visible, something is highlighted, the user
                # made a selection "gesture"; let's go select it!
                self._action_suggestion_list("select")
        else:
            # The list isn't visible, which means that if we have a
            # suggestion...
            if self._selected_suggestion is not None:
                # ...we should return it to the parent screen and let it
                # decide what to do with it (hopefully it'll run it).
                self._cancel_gather_suggestions()
                self.app.post_message(
                    SuggestionPalette.Closed(option_selected=True)
                )
                self.app._delay_update()
                self.dismiss()
                self.app.call_later(self._selected_suggestion.action)

    @on(OptionList.OptionSelected)
    def _select_suggestion(self, event: OptionList.OptionSelected) -> None:
        """Listen to OptionList.OptionSelected."""
        event.stop()
        self._cancel_gather_suggestions()
        input = self.query_one(SuggestionInput)
        with self.prevent(Input.Changed):
            assert isinstance(event.option, Suggestion)
            hit = event.option.hit
            input.value = str(hit.text)
            self._selected_suggestion = hit
        input.action_end()
        self._list_visible = False
        self.query_one(SuggestionList).clear_options()
        self._hit_count = 0
        self._select_or_suggest()

    @on(OptionList.OptionHighlighted)
    def _stop_event_leak(self, event: OptionList.OptionHighlighted) -> None:
        """Stop any unused events so they don't leak to the application."""
        event.stop()
        self.app.post_message(
            SuggestionPalette.OptionHighlighted(highlighted_event=event)
        )

    # Action methods.
    def _action_cursor_down(self) -> None:
        """Handle the cursor down action.

        This allows the cursor down key to either open the suggestion list, if
        it's closed but has options, or if it's open with options just
        cursor through them.
        """
        suggestion_list = self.query_one(SuggestionList)
        if suggestion_list.option_count and not self._list_visible:
            self._list_visible = True
            suggestion_list.highlighted = 0
        elif (
            suggestion_list.option_count
            and not suggestion_list.get_option_at_index(0).id
            == self._NO_MATCHES
        ):
            self._action_suggestion_list("cursor_down")

    def _action_escape(self) -> None:
        """Handle a request to escape out of the palette."""
        self._cancel_gather_suggestions()
        self.app.post_message(SuggestionPalette.Closed(option_selected=False))
        self.dismiss()

    def _action_show_help(self):
        self.app.push_screen(
            HelpScreen(
                LEX.screen.quick_search.help,
                title=LEX.ui.btn.help,
                button=LEX.ui.btn.close,
            )
        )

    def _action_suggestion_list(self, action: str) -> None:
        """Pass an action on to the SuggestionList.

        Args:
            action: The action to pass on to the SuggestionList.
        """
        try:
            cbl = getattr(self.query_one(SuggestionList), f"action_{action}")
        except AttributeError:
            return
        cbl()

    # Worker methods
    @work(exclusive=True, group=_GATHER_SUGGESTIONS_GROUP)
    async def _gather_suggestions(self, search_value: str) -> None:
        """Gather up all of the suggestions that match the search value.

        Args:
            search_value: The value to search for.
        """
        # The list to hold on to the suggestions we've gathered from the
        # providers.
        gathered_suggestions: list[Suggestion] = []

        # Get a reference to the widget that we're going to drop the
        # (display of) suggestions into.
        suggestion_list = self.query_one(SuggestionList)

        # If there's just one option in the list, and it's the item that
        # tells the user there were no matches, let's remove that. We're
        # starting a new search so we don't want them thinking there's no
        # matches already.
        if (
            suggestion_list.option_count == 1
            and suggestion_list.get_option_at_index(0).id == self._NO_MATCHES
        ):
            suggestion_list.remove_option(self._NO_MATCHES)

        # Each suggestion will receive a sequential ID. This is going to be
        # used to find suggestions back again when we update the visible list
        # and want to settle the selection back on the suggestion it was on.
        suggestion_id = 0

        # We're going to be checking in on the worker as we loop around, so
        # grab a reference to that.
        worker = get_current_worker()

        # Reset busy mode.
        self._show_busy = False

        # We're going to batch updates over time, so start off pretending
        # we've just done an update.
        last_update = monotonic()

        # Kick off the search, grabbing the iterator.
        search_routine = self._search_for(search_value)
        search_results = search_routine.__aiter__()

        # We're going to be doing the send/await dance in this code, so we
        # need to grab the first yielded suggestion to start things off.
        try:
            hit = await search_results.__anext__()
        except StopAsyncIteration:
            # We've been stopped before we've even really got going, likely
            # because the user is very quick on the keyboard.
            hit = None

        while hit:
            # Turn the suggestion into something for display, and add it to the
            # list of suggestions that have been gathered so far.

            def build_prompt() -> Iterable[Content]:
                """Generator for prompt content."""
                assert hit is not None
                if isinstance(hit.prompt, Text):
                    yield Content.from_rich_text(hit.prompt)
                else:
                    yield Content.from_markup(hit.prompt)  # type: ignore

                # Optional help text
                if hit.help:
                    help_style = Style.from_styles(
                        self.get_component_styles(
                            "suggestion-palette--help-text"
                        )
                    )
                    yield Content.from_markup(hit.help).stylize_before(
                        help_style
                    )

            prompt = Content("\n").join(build_prompt())

            gathered_suggestions.append(
                Suggestion(prompt, hit, id=str(suggestion_id))
            )

            if worker.is_cancelled:
                break

            now = monotonic()
            if (now - last_update) > self._RESULT_BATCH_TIME:
                self._refresh_suggestion_list(
                    suggestion_list,
                    gathered_suggestions,
                )
                last_update = now

            suggestion_id += 1

            # Finally, get the available suggestion from the incoming queue;
            # note that we send the worker cancelled status down into the
            # search method.
            try:
                hit = await search_routine.asend(worker.is_cancelled)
            except StopAsyncIteration:
                break

        # On the way out, if we're still in play, ensure everything has been
        # dropped into the suggestion list.
        if not worker.is_cancelled:
            self._refresh_suggestion_list(suggestion_list, gathered_suggestions)

        # One way or another, we're not busy any more.
        self._show_busy = False

        # If we didn't get any hits, and we're not cancelled, that would
        # mean nothing was found. Give the user positive feedback to that
        # effect.
        if suggestion_list.option_count == 0 and not worker.is_cancelled:
            self._hit_count = 0
            self._start_no_matches_countdown(search_value)

        self.add_class("-ready")
