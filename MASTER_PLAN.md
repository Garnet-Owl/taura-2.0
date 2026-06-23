# Taura 2.0 - Master Plan

Taura 2.0 is an open-source machine translation project for Kikuyu and English.
The goal is a practical bidirectional translator with a clean data pipeline,
measurable model quality, and a small FastAPI service that can be improved by
contributors over time.

This file is the roadmap. It should describe the project direction, milestones,
and acceptance criteria. Detailed day-to-day changes belong in `CHANGELOG.md`.
Milestone status belongs in `session-details/progress_update_*.md`.

---

## 1. Project Goal

Build a Kikuyu-English translation system that moves from a retrieval-based
FastText baseline to a context-aware sequence-to-sequence model.

Target release quality:
- Reproducible dataset preparation and evaluation.
- Publicly understandable corpus provenance.
- API support for bidirectional translation.
- Documented model metrics and limitations.
- A path from the current FastText baseline to NLLB-200 fine-tuning.

---

## 2. Technical Direction

### Baseline System

The current baseline uses:
- Normalized parallel corpora.
- FastText embeddings for Kikuyu and English.
- Orthogonal Procrustes alignment.
- Retrieval-based sentence translation and word-by-word fallback.
- FastAPI endpoints for translation, candidates, model metadata, feedback, and
  health checks.

This baseline is valuable because it is small, inspectable, and useful for
corpus-quality experiments.

### Target System

The target system uses transfer learning:
- Base model: `facebook/nllb-200-distilled-600M`.
- Languages: `kik_Latn` and `eng_Latn`.
- Fine-tuning: LoRA adapters on attention projection layers.
- Primary metric: ChrF/ChrF++.
- Secondary metrics: BLEU, retrieval accuracy, and qualitative review.

The FastText retrieval system remains a fallback and data-quality diagnostic
tool while the NLLB path matures.

---

## 3. Milestones

### Milestone 0 - Project Foundation

Purpose: establish a maintainable Python project that contributors can run.

Acceptance criteria:
- `uv` manages dependencies and lockfile.
- Ruff, pytest, and CI are configured.
- Package structure is feature-oriented enough for API, preprocessing, serving,
  and scripts.
- Contributor setup docs exist.

Status: complete.

### Milestone 1 - FastText Baseline

Purpose: build the first measurable Kikuyu-English translation baseline.

Acceptance criteria:
- Text normalization and train/validation/test splitting are reproducible.
- FastText embeddings train for both language directions.
- Alignment matrices are saved with versioned model artifacts.
- Retrieval metrics are generated and stored.

Status: complete.

### Milestone 2 - API, Evaluation, and Demo UI

Purpose: expose the baseline through a useful service and verify behavior.

Acceptance criteria:
- FastAPI serves bidirectional translation.
- `/translate/candidates` exposes ranked hypotheses.
- `/model/info` exposes model version, hyperparameters, and available metrics.
- Offline evaluation reports BLEU/ChrF.
- A simple browser UI exists for manual translation and feedback.

Status: complete.

### Milestone 3 - Corpus Expansion and Quality Control

Purpose: improve translation quality by increasing trustworthy parallel and
monolingual data.

Phases:
1. Seed dictionary extraction from legacy spreadsheet pairs.
2. Web and public-source corpus collection where licensing allows.
3. Bible corpus extraction as one data-processing phase.
4. Monolingual corpus expansion for FastText training.
5. Rebuild splits, retrain baseline, and compare metrics.

Bible extraction is a phase within this milestone, not a milestone per book.
Individual book extractors are implementation details and should be recorded in
the changelog or handoff notes unless they change milestone status.

Acceptance criteria:
- Corpus sources and cleaning rules are documented.
- Extracted verse pairs pass missing/empty validation.
- Generated datasets are reproducible from scripts.
- Model metrics improve or the regression is explained.

Status: in progress.

### Milestone 4 - NLLB Fine-Tuning Readiness

Purpose: prepare the project for sequence-to-sequence training.

Acceptance criteria:
- A golden evaluation split is defined.
- Dataset filtering rejects obvious non-Kikuyu/non-English noise.
- Training configuration for LoRA fine-tuning is documented.
- Remote GPU workflow is reproducible.

Status: not started.

### Milestone 5 - NLLB Training and Evaluation

Purpose: train a context-aware translation model and compare it to the baseline.

Acceptance criteria:
- LoRA adapters train successfully on a GPU environment.
- Evaluation includes ChrF/ChrF++, BLEU, and qualitative samples.
- Model artifacts are versioned without committing large binaries to git.
- The FastAPI service can select the fine-tuned model or fallback baseline.

Status: not started.

### Milestone 6 - Release Packaging

Purpose: make the project understandable and usable by outside contributors.

Acceptance criteria:
- README explains current quality honestly.
- Setup, training, evaluation, and serving commands are current.
- Model and dataset download locations are documented.
- Known limitations and next research tasks are visible.

Status: in progress.

---

## 4. Progress-Tracking Rules

Use the documents this way:

- `MASTER_PLAN.md`: stable roadmap, milestone definitions, acceptance criteria.
- `session-details/progress_update_*.md`: milestone status snapshots and current
  blockers. Update only when a milestone status, phase status, metric, or next
  milestone focus changes.
- `CHANGELOG.md`: detailed chronological implementation history. Update after
  code or documentation changes.
- `session-details/handoffs/`: exact resumption point for the next agent run.

Do not duplicate every changelog entry into a progress update.

---

## 5. Current Priority

Finish Milestone 3 by completing the Bible corpus extraction phase, rebuilding
the corpus, retraining the FastText baseline, and comparing metrics against the
latest recorded scores.
