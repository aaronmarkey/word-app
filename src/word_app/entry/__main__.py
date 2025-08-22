import argparse
from enum import StrEnum
from typing import Callable

from word_app.app.tui.main import WordApp
from word_app.entry.tui import create_dummy_app, create_real_app
from word_app.entry.tui import run as tui_run


class AvailableApp(StrEnum):
    tui = "tui"
    tui_dumb = "tui-dumb"


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Word App",
        usage="Various English language word operations.",
        description="Start the Word App.",
    )
    parser.add_argument(
        "-a",
        "--app",
        action="store",
        required=True,
        type=AvailableApp,
        choices=list(AvailableApp),
    )
    return parser.parse_args()


def main() -> None:
    _app_map: dict[AvailableApp, Callable[[], WordApp]] = {
        AvailableApp.tui: create_real_app,
        AvailableApp.tui_dumb: create_dummy_app,
    }
    arguments = args()
    app = _app_map[arguments.app]()
    tui_run(app)


main()
