# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- Initialized `CHANGELOG.md` and `session-details/progress_update_2026-06-20.md`.
- Completed directory scaffolding for `app/serve` and `models`.
- Added `CONTRIBUTING.md` and verified CI pipeline presence.
- Implemented robust tokenization and text normalization scripts (`app/api/preprocessing.py`).
- Resolved environment issue by disabling keyring configuration to prevent Poetry commands from hanging on Windows.
- Installed test dependencies (`givenpy`, `pyhamcrest`) and verified the preprocessing tests.
- Implemented dataset splitting logic (`app/api/split.py`) with unit tests, achieving 100% test pass rate.
- Installed `fasttext-wheel`, `numpy`, and `pydantic` in the python virtual environment.
- Created cross-lingual embeddings alignment and translator module (`app/api/embeddings.py`) supporting sentence-retrieval and word-by-word modes.
- Implemented embedding training and SVD Procrustes mapping matrix learning pipeline (`scripts/train_embeddings.py`).
- Implemented translation service API (`app/serve/main.py`) with FastAPI/Uvicorn, achieving 100% pass rate across all 18 unit and integration tests.
- Updated `README.md` with dataset preparation, training, serving instructions, and curl API examples.
- Installed missing development tools (`ruff`, `mypy`) in the `.venv` virtual environment.
- Configured Mypy for Python 3.12, excluded the tests directory from strict typing, and added complete type hints to `app/api/embeddings.py` and `app/serve/main.py`.
- Formatted and cleaned up codebase using Ruff format and check.
