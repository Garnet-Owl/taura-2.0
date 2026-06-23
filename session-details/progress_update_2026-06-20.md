# Taura 2.0 - Progress Update (2026-06-20)

This is a milestone snapshot, not a changelog. Detailed implementation history
belongs in `CHANGELOG.md`.

## Milestone Status

| Milestone | Status | Evidence |
|---|---|---|
| 0 - Project Foundation | Complete | `uv`, Ruff, pytest, CI workflow, contributor docs, project directories |
| 1 - FastText Baseline | Complete | preprocessing, split generation, embedding training, alignment matrices, saved metrics |
| 2 - API, Evaluation, and Demo UI | In progress | FastAPI service and UI present; offline evaluation pipeline added |
| 3 - Corpus Expansion and Quality Control | Not started | Bible extraction and larger corpus work not yet organized as a milestone |
| 4 - NLLB Fine-Tuning Readiness | Not started | No sequence-to-sequence training workflow yet |
| 5 - NLLB Training and Evaluation | Not started | No trained NLLB adapter yet |
| 6 - Release Packaging | In progress | README/setup docs exist but still evolving |

## Current Focus

Stabilize the FastText baseline and make the API/evaluation surface usable
enough to compare future corpus and model changes.

## Recent Evidence

- Core project scaffolding and CI are in place.
- Text normalization and train/validation/test splitting are implemented.
- FastText embedding training and alignment are implemented.
- FastAPI translation endpoints and integration tests are present.
- Offline BLEU/ChrF evaluation has been introduced.

## Next Milestone Work

1. Finish API/evaluation documentation.
2. Improve corpus quality and quantity.
3. Re-evaluate the baseline after each meaningful corpus change.

## Blockers

None.
