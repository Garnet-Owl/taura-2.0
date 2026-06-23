# Taura 2.0 — Master Plan

## Project Overview
**Taura 2.0** is an open-source machine translation project designed to translate between Kikuyu and English. The name "Taura" is derived from the Kikuyu word "Taũra", which means "Translate".
This project focuses on providing high-quality translations using FastText-based word embeddings, packaged into a clean, feature-based API structure for community contributions and broad usage.

**Timeline:** The project initially started in April 2025, ran for two months, and paused. Resumed in June 2026. A first working version (v1.0) is targeted for the end of July 2026, with overall Phase 1 completion by September 2026.

## Goals & Objectives
1. **Core Translation Model:** Build reliable bidirectional translation capabilities (Kikuyu ↔ English) using FastText embeddings.
2. **Community Driven:** Maintain a clean, modular, and maintainable codebase that encourages open-source contributions.
3. **Performant API:** Serve the translation model efficiently via a FastAPI backend.
4. **Reproducibility & Testing:** Provide comprehensive data preprocessing pipelines, reproducible training scripts, and robust automated tests.

## Architecture & Tech Stack
- **Language:** Python 3.12+
- **Dependency Management:** Poetry
- **API Framework:** FastAPI
- **Model Engine:** FastText
- **Code Quality:** Ruff (linting & formatting), Pytest (testing)

## Project Structure
- `app/api/`: Core API and feature implementation (e.g., embed vectors, preprocessing, model loading).
- `app/serve/`: FastAPI application setup and endpoint routing.
- `app/tests/`: Comprehensive unit and integration test suite.
- `models/`: Storage for serialized FastText models and embeddings.
- `data/`: Raw and processed datasets for training and evaluation.
- `notebooks/`: Exploratory Data Analysis (EDA) and experimental code.
- `scripts/`: Utility scripts for training, evaluation, and data management.

## Milestones (Phase 1)

### 1. Project Scaffolding & Setup
- Initialize project with Poetry, Ruff, and Pytest.
- Define feature-based directory structure (`app/api`, `app/serve`, `models/`, `data/`).
- Set up CI/CD pipelines and contribution guidelines.

### 2. Data Engineering & Preprocessing
- Collect and curate Kikuyu-English parallel corpora.
- Implement robust tokenization and text normalization scripts.
- Prepare train/validation/test splits.

### 3. Model Development & Training
- Implement FastText embeddings training pipeline.
- Train models for both Kikuyu → English and English → Kikuyu.
- Evaluate translation quality using relevant metrics (e.g., BLEU score equivalents for word/phrase embeddings) and store metrics.

### 4. API Service & Integration
- Wrap models into a FastAPI service (`app/serve`).
- Implement endpoints for real-time bidirectional translation.
- Write extensive integration tests for the API.

### 5. Open Source Release & Documentation
- Document API usage and model training instructions.
- Ensure `README.md`, `INSTALL.md`, and contribution guides are up-to-date.
- Finalize first working release (v1.0) by end of July 2026, and complete Phase 1 by September 2026.
