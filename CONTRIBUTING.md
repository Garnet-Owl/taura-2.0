# Contributing to Taura 2.0

First off, thanks for taking the time to contribute!

## Getting Started

1. Ensure you have Python 3.12+ and `uv` installed.
2. Clone the repository and run `uv sync`.
3. Set up pre-commit hooks: `uv run pre-commit install`.

## Development Workflow

- We use `ruff` for linting and formatting. Run `uv run ruff check` and `uv run ruff format` before committing.
- Ensure all tests pass by running `uv run pytest`.
- Follow the "Two Hats" rule: do not refactor and add functionality at the same time.

## Submitting Pull Requests

1. Create a new branch for your feature or bugfix.
2. Commit your changes locally. Ensure commit messages are short imperative sentences.
3. Push to your fork and submit a pull request against the `main` branch.
4. Ensure the CI pipeline passes.
