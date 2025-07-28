from word_app.app import WordAppContext, create_app
from word_app.app_conf import AppConf
from word_app.data.sources import DATA_SOURCES
from word_app.io import ApplicationPath


def run() -> None:
    app_path = ApplicationPath()
    app_conf = AppConf.from_env(app_path.usr)

    ctx = WordAppContext(
        conf=app_conf, data_sources=DATA_SOURCES, path=app_path
    )
    app = create_app(ctx)
    app.run()
