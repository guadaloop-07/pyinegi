# Contributing to pyinegi
Write code, issues, pull requests, commit messages, and documentation in English.

Install [uv](https://docs.astral.sh/uv/), then run `uv sync --all-extras --dev` and `uv run pre-commit install`.

Before opening a PR, run `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy`, and `uv run pytest`.

Use a short-lived `feature/`, `fix/`, `docs/`, or `chore/` branch. Link an issue and use English Conventional Commits, such as `feat: add catalog client`. Do not commit API tokens.
