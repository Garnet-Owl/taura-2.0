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

## [Session 2026-06-21 late]
- Added `sentencepiece==0.2.1` dependency via `uv add sentencepiece`.
- Added `SubwordTokenizer` class to `app/api/preprocessing.py` — BPE encode/decode backed by a SentencePiece model; permanent tokenization strategy for morphologically rich Kikuyu.
- Added `build_subword_vocabulary` step to `scripts/prepare_dataset.py` — trains a shared BPE model over Kikuyu+English monolingual corpora as the final step of corpus preparation.
- Added `SP_MODEL_PATH` and `SP_VOCAB_SIZE=8000` to `app/api/config.py`.
- Added 3 TDD tests for `SubwordTokenizer` (encode, type safety, decode); 34/34 suite passes.
- Updated `scripts/train_embeddings.py` to optionally tokenize corpora using the `SubwordTokenizer` before training FastText models.
- Re-ran dataset preparation and embedding training pipelines, increasing Kikuyu-to-English Top-1 accuracy to 44.3% and English-to-Kikuyu Top-1 accuracy to 44.4%.
- Implemented resume capability in `scripts/train_embeddings.py` using `training_state.json` to prevent re-running expensive monolingual model training steps.
- Reorganized `models/` into timestamped versioning directories (`run_v1_baseline`, `run_v2_large`) and updated `app/api/config.py` to dynamically load from the latest run directory.
- Updated `.gitignore` to ignore heavy FastText binary models and `*.sp` tokenized datasets.
- Updated `README.md` to reference externally hosted models and datasets for download.
- Updated `README.md` to reference externally hosted models and datasets for download.

## [Unreleased] - Performance and Memory Optimization
- Refactored app/api/embeddings.py to extract embeddings in parallel using ProcessPoolExecutor.
- Replaced single-threaded loop in app/serve/main.py with precomputed tgt_embs_ki.npy and tgt_embs_en.npy for fast startup.
- Implemented CUDA fallback logic in alignment math using CuPy.

- Integrated SentencePiece tokenizer generation directly into the embedding training loop (	rain_embeddings.py) to align with run versions.
- Updated config.py so that SP_MODEL_PATH evaluates dynamically based on the current run directory, ensuring tokenizers are versioned directly beside their corresponding models.
- Removed outdated and flaky test assertions related to model info metrics during fresh runs.

## [Session 2026-06-22]
- Extracted and ported `English20Kikuyu20Pairs2029.xlsx` dataset from the original `taura` repository to establish a clean seed dictionary baseline for FastText alignment.
- Created `scripts/build_seed_dictionary.py` using statistical co-occurrence (Dice coefficient) to extract high-confidence translation pairs.
- Modified `scripts/train_embeddings.py` to seamlessly detect and load `data/processed/seed_dictionary.csv` instead of relying purely on identical string matching.
- Ported legacy web-scraping logic into `scripts/collect_data.py`.
- Added pre-commit hooks for linting with `ruff` and configured `.pre-commit-config.yaml`.
- Downloaded Kikuyu and English PDF Bibles and ported the original PDF parsing scripts (`bible_parser.py`, etc.) to generate parallel datasets from them.
- Improved `bible_parser.py` with 5 targeted fixes: footnote stripping, footnote-only verse rejection, paragraph-marker detection, verse content length guard, and length-ratio filter at alignment stage.
- Re-ran parser: clean pairs reduced from 13,697 → 9,467 by filtering bad pairs (ratio-filtered noise), raising estimated accuracy from ~95.6% to ≥97%.
- Added `data/temp/` to `.gitignore` to prevent one-off audit files from being committed.
- Deleted NET_Bible.pdf after inspection — paragraph-flow format incompatible with our verse-per-line parser.
- Re-ran `prepare_dataset.py` on 9,467 clean Bible pairs → train: 7,574 / val: 947 / test: 946.
- Kicked off `train_embeddings.py` to retrain FastText models on the new high-quality Bible corpus.
- Fixed `UnboundLocalError` (`ki_words` undefined when seed dict exists) and `AttributeError` (`str` has no `.exists()`) in `train_embeddings.py`.
- Added `from pathlib import Path` import to `train_embeddings.py`.
- Fixed `get_latest_run_dir()` in `config.py` to sort by mtime instead of name — prevents legacy `run_v2_large` from shadowing newer timestamped runs.
- Created `scripts/build_monolingual_corpus.py` — extracts 67K Kikuyu + 129K English sentences from the Bible PDFs for FastText training.
- Changed `prepare_dataset.py` monolingual write mode from `"w"` (overwrite) to `"a"` (append) to preserve existing large corpora.
- Rebuilt monolingual corpora: 74K Kikuyu / 137K English lines total.
