from word_app.app.main import WordAppContext
from word_app.app.conf import AppConf
from word_app.data.sources import get_available_data_sources
from word_app.io import ApplicationPath

from word_app.data.services.wordnik import WordnikService, create_wordnik_client


def main() -> None:
    app_path = ApplicationPath()
    app_conf = AppConf.from_env(app_path.usr)

    ds = get_available_data_sources()
    ctx = WordAppContext(conf=app_conf, data_sources=ds, path=app_path)

    wnc = create_wordnik_client(ctx.conf.ds.wordnik.api_key)
    service = WordnikService(wnc)
    word = "paper"

    thesaurus = service.get_word_thesaurus(word)


if __name__ == "__main__":
    main()
