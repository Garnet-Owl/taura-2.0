# Taura 2.0 - Progress Update (2026-06-23)

## Task Board

| Task | Status | Notes |
| :--- | :---: | :--- |
| **1. Project Scaffolding & Setup** | | |
| Initialize project with Poetry, Ruff, and Pytest | ✅ Verified | `pyproject.toml` exists with dependencies |
| Define feature-based directory structure (`app/api`, `app/serve`, `models/`, `data/`) | ✅ Verified | `models/`, `app/serve` created |
| Set up CI/CD pipelines and contribution guidelines | ✅ Verified | `.github/workflows/ci.yml` and `CONTRIBUTING.md` created |
| **2. Data Engineering & Preprocessing** | | |
| Collect and curate Kikuyu-English parallel corpora | ✅ Verified | HF dataset downloaded and preprocessed |
| Implement robust tokenization and text normalization scripts | ✅ Verified | Implemented in `app/api/preprocessing.py` and verified by unit tests |
| Prepare train/validation/test splits | ✅ Verified | Implemented in `app/api/split.py` and verified by unit tests |
| **3. Model Development & Training** | | |
| Implement FastText embeddings training pipeline | ✅ Verified | Implemented in `scripts/train_embeddings.py` and `app/api/embeddings.py` |
| Train models for both Kikuyu -> English and English -> Kikuyu | ✅ Verified | Models and alignment projection matrices trained and saved |
| Evaluate translation quality | ✅ Verified | Top-1, top-5, and MRR metrics computed and saved to JSON |
| **4. API Service & Integration** | | |
| Wrap models into a FastAPI service | ✅ Verified | Implemented in `app/serve/main.py` with context lifespan |
| Implement endpoints for real-time bidirectional translation | ✅ Verified | Bidirectional endpoints support retrieval and word-by-word methods |
| Write integration tests for API | ✅ Verified | Integration tests implemented in `app/tests/test_api.py` |
| **5. Phase 2 Features (Evaluation & Web UI)** | | |
| Build robust offline evaluation pipeline with `sacrebleu` | ✅ Verified | Implemented in `scripts/evaluate.py` calculating BLEU/ChrF |
| Construct FastAPI single-page web UI layout and controller | ✅ Verified | Designed glassmorphic dark-mode SPA under `/` with template mounting |
| Implement feedback collection and logging pipeline | ✅ Verified | Log user ratings and feedback suggestions to `data/feedback.jsonl` |
| **6. Phase 3 Features (uv Packaging Migration)** | | |
| Migrate pyproject.toml to PEP 621 metadata & Hatchling backend | ✅ Verified | Replaced Poetry with PEP 621 structure using Hatchling |
| Generate uv.lock and synchronize dependencies | ✅ Verified | Generated uv.lock using `uv lock` and synced with `uv sync` |
| Migrate CI/CD pipeline to use setup-uv | ✅ Verified | Replaced Snok Poetry action with astral-sh/setup-uv action |
| Update project documentation (README.md, INSTALL.md, CONTRIBUTING.md) | ✅ Verified | Replaced Poetry commands with uv commands |
| Align developer instructions (AGENTS.md) with uv toolset | ✅ Verified | Updated developer guidelines to enforce uv |
| **7. Phase 4 Features (Model Scaling & Optimization)** | | |
| Clean and normalize unsupervised monolingual corpora | ✅ Verified | Applied text normalization to monolingual corpora exports |
| Implement automated hyperparameter tuning script | ✅ Verified | Created `scripts/tune_hyperparameters.py` for grid search |
| Train final models with optimal hyperparameters | ✅ Verified | Updated `scripts/train_embeddings.py` and retrained models |
| Re-evaluate on test set and verify API test suite | ✅ Verified | Re-evaluated metrics and verified all pytest test suites |
| **8. Phase 5 & 6 Features (Model Scaling & Optimization)** | | |
| Expand Parallel Corpora & Retraining | ✅ Verified | Task 195 successfully processed, evaluated and metrics saved |
| **9. Phase 7 Features (Open Source Release & Documentation)** | | |
| Fix hyperparameter config (EPOCH=35, MIN_COUNT=2) | ✅ Verified | Corrected `config.py` to match tuned values |
| Add `/translate/candidates` (top-K) endpoint | ✅ Verified | Implemented with TDD tests in `test_candidates_endpoint.py` |
| Add `/model/info` metadata endpoint | ✅ Verified | Returns version, hyperparameters, and live evaluation metrics |
| Update README with metrics and new endpoints | ✅ Verified | Added performance table and new API examples |
| **10. Phase 8 Features (Alignment Refinement)** | | |
| Implement `iterative_procrustes` in `app/api/embeddings.py` | ✅ Verified | 2 TDD tests pass; function refines W over N SVD iterations |
| Create `scripts/refine_alignment.py` | ✅ Verified | Loads models, runs 5-iteration refinement, saves matrices, re-evaluates |
| **11. Phase 9 Features (Subword Tokenization)** | | |
| Add `SubwordTokenizer` to `app/api/preprocessing.py` | ✅ Verified | SentencePiece BPE wrapper with encode/decode; 3 TDD tests pass |
| Add `build_subword_vocabulary` to `scripts/prepare_dataset.py` | ✅ Verified | Trains shared BPE model over Kikuyu+English corpora as final prep step |
| Add `SP_MODEL_PATH`, `SP_VOCAB_SIZE` to `app/api/config.py` | ✅ Verified | Centralised config; vocab_size=8000 |
| Train FastText on SP-tokenized corpora | ✅ Verified | Updated `scripts/train_embeddings.py` and retrained models; Top-1 accuracy improved |
| **12. Phase 10 Features (Bible Corpus & Co-occurrence Matching)** | | |
| Refactor Bible parser and parallel alignment pipeline | ✅ Verified | Cleaned verse extraction and aligned 9.4k sentence pairs |
| Extract statistical co-occurrence seed dictionary | ✅ Verified | Generated `seed_dictionary.csv` using Dice coefficient matching |
| Expand Kikuyu/English monolingual training corpora | ✅ Verified | Expanded monolingual sets from Bible parsing to 74K/137K sentences |
| **13. Phase 11 Features (Type Safety & Evaluation Verification)** | | |
| Validate model translation nearest-neighbors | ✅ Verified | Verified Named Entity translation mappings and alignments |
| Resolve strict type check and linter warnings | ✅ Verified | Fixed all Mypy type-annotation warnings and Ruff formatting issues |
| Re-evaluate translation quality on clean split | ✅ Verified | Evaluated Kikuyu<->English translation BLEU scores (5.34 / 4.91) |
| **14. Phase 12 Features (Modular Bible Preprocessing & Matthew Feature)** | | |
| Package Matthew extraction as a modular feature | ✅ Verified | Core and Service structure inside `matthew/` feature directory |
| Implement CLI orchestrator runner | ✅ Verified | Created `app/preprocessing/bible/orchestrator.py` |
| Add comprehensive parser unit tests | ✅ Verified | Created `tests/test_matthew_parser.py` (all tests passing) |
| Fix propagation shift on missing/empty verses | ✅ Verified | Robust slicing logic implemented and tested with 1070 aligned verses |
| **15. Phase 13 Features (Acts Corpus Extraction)** | | |
| Implement Acts (Atũmwo) extractor | ✅ Verified | `app/preprocessing/bible/acts/` — 1007 aligned verse pairs, 0 missing/empty |
| Wire Acts into orchestrator | ✅ Verified | Added to `BOOKS` list in `orchestrator.py` |
| Add Acts parser unit tests | ✅ Verified | `tests/test_acts_parser.py` — 5 BDD tests, all passing; full suite 61/61 |
| **16. Phase 14 Features (Romans Corpus Extraction)** | | |
| Implement Romans (Aroma) extractor | ✅ Verified | `app/preprocessing/bible/romans/` — 431 aligned verse pairs; 0 Kikuyu missing/empty; 2 English missing (known WEB versification gap at 16:26-27) |
| Wire Romans into orchestrator | ✅ Verified | Added to `BOOKS` list in `orchestrator.py` |
| Add Romans parser unit tests | ✅ Verified | `tests/test_romans_parser.py` — 5 BDD tests, all passing; full suite 66/66 |

## Blockers

None.
