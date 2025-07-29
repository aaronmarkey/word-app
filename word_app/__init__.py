from word_app.app.main import WordAppContext, create_app
from word_app.app.conf import AppConf
from word_app.data.sources import get_available_data_sources
from word_app.io import ApplicationPath


def run() -> None:
    app_path = ApplicationPath()
    app_conf = AppConf.from_env(app_path.usr)

    ds = get_available_data_sources()
    ctx = WordAppContext(conf=app_conf, data_sources=ds, path=app_path)
    app = create_app(ctx=ctx)
    app.run()
