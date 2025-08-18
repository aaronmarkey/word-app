# Run code linter and static type checker
check:
	poetry run ruff check .
	poetry run mypy .

# Clean project of all auto-generated directories and files.
clean:
	find . -name __pycache__ -type d -print0|xargs -0 rm -r --
	find . -name .mypy_cache -type d -print0|xargs -0 rm -r --
	find . -name .ruff_cache -type d -print0|xargs -0 rm -r --

# Run code auto-formatter.
format:
	poetry run ruff check . --fix
	poetry run ruff format .

# Install project
install:
	poetry install
	cp -n ./word_app/usr/.env.example ./word_app/usr/.env || true

# Install project with dev dependencies
install-dev:
	poetry install --with dev
	cp -n ./word_app/usr/.env.example ./word_app/usr/.env || true

# Create i18n .mo file
lang-mo:
	msgfmt -o ./word_app/locales/en_US/LC_MESSAGES/word_app.mo ./word_app/locales/en_US/LC_MESSAGES/word_app.po

# Create i18n .pot files
lang-pot:
	poetry run xgettext -d base -o ./word_app/locales/word_app.pot ./word_app/lex.py

lang-pot-po:
	cp ./word_app/locales/word_app.pot ./word_app/locales/en_US/LC_MESSAGES/word_app.po

# Run
run:
	poetry run textual run word_app/__main__.py

# Run in dev mode
run-dev:
	poetry run textual run --dev word_app/__main__.py

# Run unit tests
test:
	poetry run pytest .

# Run the Textual debug console. Start _before_ running application.
textual-console:
	poetry run textual console
