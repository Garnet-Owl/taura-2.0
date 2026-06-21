# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- Added ignores for model files (`models/*.npy`), local wheel files (`*.whl`), and telemetry/feedback data (`data/feedback.jsonl`) to `.gitignore`.
- Configured `.pre-commit-config.yaml` to enforce a 10MB limit check on all added files.
- Configured `.gitattributes` to route binaries and package extensions through a declarative `check-size` filter.
- Tracked and committed the lightweight translation datasets under the `data/` directory.
- Migrated package and dependency management from Poetry to `uv` and adopted PEP 621 metadata with Hatchling build backend.
- Replaced Poetry installation and caching in GitHub Actions CI pipeline with official `astral-sh/setup-uv` action and updated all task commands.
- Updated project documentation (`README.md`, `INSTALL.md`) and developer guidelines (`AGENTS.md`) to align with `uv` command-line utility.
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
- Installed `sacrebleu` dependency using poetry.
- Implemented offline evaluation pipeline (`scripts/evaluate.py`) calculating corpus-level BLEU and ChrF scores against `data/test.tsv`.
- Mounted templates and static files inside FastAPI serving architecture and added `/health` and `/feedback` API endpoints.
- Built a sleek, glassmorphic translation SPA frontend (`index.html`, `style.css`, `main.js`) with interactive translation, word-by-word alignments, and user feedback submission.
- Fixed return type annotations for script entry points to achieve 100% type check pass rate under MyPy.

