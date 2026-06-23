# Taura 2.0 - Progress Update

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
| Implement endpoints for bidirectional translation | ✅ Verified | Bidirectional endpoints support retrieval and word-by-word methods |
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

## Blockers

None.

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
