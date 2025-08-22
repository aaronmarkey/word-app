DIR_SRC="./src"
DIR_TESTS="./tests"
DIR_USR="./usr"

# Run code linter and static type checker
check:
	poetry run ruff check $(DIR_SRC)
	poetry run mypy

# Clean project of all auto-generated directories and files.
clean:
	find ./src -name __pycache__ -type d -print0|xargs -0 rm -r --
	find ./src -name .mypy_cache -type d -print0|xargs -0 rm -r --
	find ./src -name .ruff_cache -type d -print0|xargs -0 rm -r --
	find ./tests -name __pycache__ -type d -print0|xargs -0 rm -r --
	find ./tests -name .mypy_cache -type d -print0|xargs -0 rm -r --
	find ./tests -name .ruff_cache -type d -print0|xargs -0 rm -r --

# Run code auto-formatter.
format:
	poetry run ruff check $(DIR_SRC) --fix
	poetry run ruff format $(DIR_SRC)

# Install project
install:
	poetry install
	cp -n $(DIR_USR)/.env.example $(DIR_USR)/.env || true

# Install project with dev dependencies
install-dev:
	poetry install --with dev
	cp -n $(DIR_USR)/.env.example $(DIR_USR)/.env || true

# Create i18n .mo file
lang-mo:
	msgfmt -o $(DIR_SRC)/word_app/locales/en_US/LC_MESSAGES/word_app.mo $(DIR_SRC)/word_app/locales/en_US/LC_MESSAGES/word_app.po

# Create i18n .pot files
lang-pot:
	poetry run xgettext -d base -o $(DIR_SRC)/word_app/locales/word_app.pot $(DIR_SRC)/word_app/lex.py

lang-pot-po:
	cp $(DIR_SRC)/word_app/locales/word_app.pot $(DIR_SRC)/word_app/locales/en_US/LC_MESSAGES/word_app.po

# Run
run:
	poetry run textual run $(DIR_SRC)/word_app/entry/__main__.py --app=tui

# Run in dev mode
run-dev:
	poetry run textual run --dev $(DIR_SRC)/word_app/entry/__main__.py --app=tui

# Run unit tests
test:
	poetry run pytest $(DIR_TESTS)

# Run the Textual debug console. Start _before_ running application.
textual-console:
	poetry run textual console
