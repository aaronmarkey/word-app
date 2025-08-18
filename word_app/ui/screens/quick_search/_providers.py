from abc import ABC, abstractmethod
from asyncio import Task, create_task
from typing import TYPE_CHECKING, Any, Callable, Iterable

from textual.fuzzy import Matcher
from textual.screen import Screen
from textual.style import Style
from textual.widget import Widget
from typing_extensions import TypeAlias

if TYPE_CHECKING:
    from textual.app import App

from word_app.ui.screens.quick_search._models import Hits

ProviderSource: TypeAlias = (
    "Iterable[type[Provider] | Callable[[], type[Provider]]]"
)
"""The type used to declare the providers for a SuggestionPalette."""


class Provider(ABC):
    """Base class for suggestion palette providers."""

    def __init__(
        self, screen: Screen[Any], match_style: Style | None = None
    ) -> None:
        """Initialise the provider.

        Args:
            screen: A reference to the active screen.
        """
        if match_style is not None:
            assert isinstance(match_style, Style), (
                "match_style must be a Visual style "
                "(from textual.style import Style)"
            )
        self.__screen = screen
        self.__match_style = match_style
        self._init_task: Task | None = None
        self._init_success = False

    @property
    def focused(self) -> Widget | None:
        """The currently-focused widget in the currently-active screen."""
        return self.__screen.focused

    @property
    def screen(self) -> Screen[object]:
        """The currently-active screen."""
        return self.__screen

    @property
    def app(self) -> "App[object]":
        """A reference to the application."""
        return self.__screen.app

    @property
    def match_style(self) -> Style | None:
        """The preferred style to use when highlighting."""
        return self.__match_style

    def matcher(self, user_input: str, case_sensitive: bool = False) -> Matcher:
        """Create a `textual.fuzzy.Matcher` for the given input.

        Args:
            user_input: The text that the user has input.
            case_sensitive: Should matching be case sensitive?

        Returns:
            A `textual.fuzzy.Matcher` object for matching against candidates.
        """
        return Matcher(
            user_input,
            match_style=self.match_style,
            case_sensitive=case_sensitive,
        )

    def _post_init(self) -> None:
        """Internal method to run post init task."""

        async def post_init_task() -> None:
            """Wrapper to post init that runs in a task."""
            try:
                await self.startup()
            except Exception:
                from rich.traceback import Traceback

                self.app.log.error(Traceback())
            else:
                self._init_success = True

        self._init_task = create_task(post_init_task())

    async def _wait_init(self) -> None:
        """Wait for initialization."""
        if self._init_task is not None:
            await self._init_task
        self._init_task = None

    async def startup(self) -> None:
        """
        Called after Provider is initialized, but before any calls to `search`.
        """

    async def _search(self, query: str) -> Hits:
        """Internal method to perform search.

        Args:
            query: The user input to be matched.

        Yields:
            Instances of Hit.
        """
        await self._wait_init()
        if self._init_success:
            if query:
                async for hit in self.search(query):
                    yield hit

    @abstractmethod
    async def search(self, query: str) -> Hits:
        """A request to search for suggestions relevant to the given query.

        Args:
            query: The user input to be matched.

        Yields:
            Instances of Hit.
        """
        yield NotImplemented

    async def _shutdown(self) -> None:
        """Internal method to call shutdown and log errors."""
        try:
            await self.shutdown()
        except Exception:
            from rich.traceback import Traceback

            self.app.log.error(Traceback())

    async def shutdown(self) -> None:
        """Called when the Provider is shutdown.

        Use this method to perform an cleanup, if required.

        """
