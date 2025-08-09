# Run code linter.
check:
	poetry run ruff check .

# Clean project of all auto-generated directories and files.
clean:
	find . -name __pycache__ -type d -print0|xargs -0 rm -r --
	find . -name .mypy_cache -type d -print0|xargs -0 rm -r --
	find . -name .ruff_cache -type d -print0|xargs -0 rm -r --

# Run code auto-formatter.
format:
	poetry run ruff format .

# Run
run:
	poetry run textual run word_app/__main__.py

# Run in dev mode
run-dev:
	poetry run textual run --dev word_app/__main__.py

# Run the Textual debug console. Start _before_ running application.
textual-console:
	poetry run textual console

# Run code static type checker.
type-check:
	poetry run mypy .
