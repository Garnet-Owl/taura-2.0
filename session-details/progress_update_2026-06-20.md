# Taura 2.0 - Progress Update

## Task Board

| Task | Status | Notes |
| :--- | :---: | :--- |
| **1. Project Scaffolding & Setup** | | |
| Initialize project with Poetry, Ruff, and Pytest | ✅ Verified | pyproject.toml exists with dependencies |
| Define feature-based directory structure (`app/api`, `app/serve`, `models/`, `data/`) | ✅ Verified | `models/`, `app/serve` created |
| Set up CI/CD pipelines and contribution guidelines | ✅ Verified | `.github/workflows/ci.yml` and `CONTRIBUTING.md` created |
| **2. Data Engineering & Preprocessing** | | |
| Collect and curate Kikuyu-English parallel corpora | ✅ Verified | HF dataset downloaded and preprocessed in previous session |
| Implement robust tokenization and text normalization scripts | ✅ Verified | Implemented in app/api/preprocessing.py and verified by unit tests |
| Prepare train/validation/test splits | ✅ Verified | Implemented in app/api/split.py and verified by unit tests |
| **3. Model Development & Training** | | |
| Implement FastText embeddings training pipeline | ✅ Verified | Implemented in scripts/train_embeddings.py and app/api/embeddings.py |
| Train models for both Kikuyu -> English and English -> Kikuyu | ✅ Verified | Models and alignment projection matrices trained and saved |
| Evaluate translation quality | ✅ Verified | Top-1, top-5, and MRR metrics computed and saved to JSON |
| **4. API Service & Integration** | | |
| Wrap models into a FastAPI service | ✅ Verified | Implemented in app/serve/main.py with context lifespan |
| Implement endpoints for bidirectional translation | ✅ Verified | Bidirectional endpoints support retrieval and word-by-word methods |
| Write integration tests for API | ✅ Verified | Integration tests implemented in app/tests/test_api.py |


## Blockers

None. All blockers have been successfully resolved.
