# Contributing to pyinegi

Write code, issues, pull requests, commit messages, and documentation in English.

## Development environment

pyinegi supports Python 3.10 through 3.13. Python 3.12 is the recommended local default because it is also used by the type-checking configuration.

Install [uv](https://docs.astral.sh/uv/), then create a seeded virtual environment and synchronize the project:

```console
uv python install 3.12
uv sync --python 3.12 --all-extras --dev
uv venv --python 3.12 --seed --allow-existing
```

`--all-extras` installs both the optional pandas support and the development tools. `uv sync` is exact, so run the final `uv venv --seed --allow-existing` command to ensure `pip` is present in `.venv` for direct package-management commands such as `.venv/bin/python -m pip install ...`. Use `uv sync` for normal dependency changes; rerun the seed command afterward if a subsequent sync removes `pip`.

Install the commit hooks once per clone:

```console
uv run pre-commit install
```

No activation is required: `uv run` automatically uses the project environment. Do not commit API tokens, local paths, `.venv`, or generated build artifacts.

## Validate changes

Before opening a pull request, run the same local quality gates used by CI:

```console
uv run pre-commit run --all-files
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv build
uv run twine check dist/*
```

The default test suite is offline and deterministic. Live API tests, when available, are marked `integration` and require an `INEGI_TOKEN` supplied through the environment.

## Live integration tests

Integration tests call the public INEGI API and are skipped automatically when `INEGI_TOKEN` is absent. They never run as part of the default `uv run pytest` command.

Run them locally with a token supplied only in your shell:

```console
export INEGI_TOKEN="your-token"
uv run pytest -m integration
```

For protected CI, store `INEGI_TOKEN` as an environment secret (not a repository variable) and expose it only to a protected environment or a manually approved workflow. The integration job should run `uv run pytest -m integration` with that secret in its environment. Do not print the token, place it in a URL, or commit a response fixture from the live API.

## Workflow

Use a short-lived `feature/`, `fix/`, `docs/`, or `chore/` branch. Link an issue and use English Conventional Commits, such as `feat: add catalog client`.
