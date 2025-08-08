from word_app.app.factory import create_app


def run() -> None:
    app = create_app()
    app.run()
