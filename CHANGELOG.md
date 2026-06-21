# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- Created `app/api/config.py` to centralize project configuration, file paths, and hyperparameters, and refactored scripts to import from it.
- Fixed shallow merge bug in `scripts/train_embeddings.py` by extracting metric preservation logic into `save_metrics` to retain offline evaluation scores.
- Added `test_save_metrics_merges_data` unit test to `app/tests/unit/test_evaluation.py` to guarantee metrics merge logic correctness.
- Removed unused imports and formatted hyperparameter tuning scripts using Ruff.
- Fully checked the implementation plan checkboxes for model scaling and optimization.
- Optimized FastText training parameters to use `epoch=35` and `ws=8` in `scripts/train_embeddings.py`.
- Retrained model embeddings, boosting Kikuyu-to-English Top-1 accuracy to 42.08% (from 39.22%) and English-to-Kikuyu Top-1 accuracy to 42.86% (from 37.14%).
- Evaluated optimized translation models on the test set, improving retrieval BLEU scores to 4.79 (Kikuyu->English) and 3.27 (English->Kikuyu).
- Aligned `CONTRIBUTING.md` developer setup guide to refer to `uv` syntax instead of Poetry.
- Updated path triggers in GitHub Actions workflow `.github/workflows/ci.yml` to target `uv.lock` instead of `poetry.lock`.
- Updated setup docstring in `setup.py` to reference Hatchling/uv instead of Poetry.
- Normalized unsupervised monolingual corpora for Kikuyu and English during dataset preparation, improving cleaning and preprocessing.
- Implemented a FastText hyperparameter grid search script `scripts/tune_hyperparameters.py` evaluated on validation set retrieval accuracy.
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


* Resolved O(N^2) hanging issue during model evaluation by limiting the size of dictionary bounds to 50k and evaluation size to 1000 sentences.
* Successfully evaluated the trained 2.2M-sentence model offline and generated final evaluation metrics.

## [Session 2026-06-21 afternoon]
- Fixed `FASTTEXT_EPOCH` config bug from `1` → `35` and `FASTTEXT_MIN_COUNT` from `1` → `2` to match optimized hyperparameters.
- Added `POST /translate/candidates` endpoint returning top-K translation hypotheses with cosine similarity scores.
- Added `GET /model/info` endpoint exposing version, hyperparameters, and live evaluation metrics.
- Created `app/tests/test_candidates_endpoint.py` with 6 TDD tests for the new endpoints (all passing).
- Updated `README.md` with current model performance metrics table, new API examples, and corrected test count to 29.

## [Session 2026-06-21 evening]
- Implemented `iterative_procrustes` in `app/api/embeddings.py` — refines orthogonal W over N SVD steps for better alignment convergence.
- Created `scripts/refine_alignment.py` — loads existing models/matrices, runs 5-iteration Procrustes refinement, saves improved matrices, re-evaluates retrieval metrics.
- Added 2 TDD tests in `test_embeddings.py` for `iterative_procrustes`: rotation recovery and orthogonality guarantee (31/31 suite passing).
- Ruff format + lint clean across all new/modified files.

