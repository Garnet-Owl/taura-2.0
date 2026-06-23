# Taura 2.0 - Progress Update (2026-06-21)

This is a milestone snapshot. It should summarize milestone health and next
focus, not repeat every implementation entry from `CHANGELOG.md`.

## Milestone Status

| Milestone | Status | Evidence |
|---|---|---|
| 0 - Project Foundation | Complete | `uv` migration, CI update, docs aligned to current toolchain |
| 1 - FastText Baseline | Complete | bidirectional embeddings, Procrustes alignment, retrieval metrics |
| 2 - API, Evaluation, and Demo UI | Complete | translation endpoints, candidate endpoint, model info endpoint, feedback route, UI, BLEU/ChrF evaluation |
| 3 - Corpus Expansion and Quality Control | In progress | subword tokenization and model optimization started; larger corpus still needed |
| 4 - NLLB Fine-Tuning Readiness | Not started | target architecture documented but no training workflow yet |
| 5 - NLLB Training and Evaluation | Not started | no fine-tuned NLLB adapter yet |
| 6 - Release Packaging | In progress | README metrics and API examples updated |

## Current Focus

Improve the baseline before moving to NLLB by tightening metrics, model metadata,
subword tokenization, and training reproducibility.

## Recent Evidence

- `/translate/candidates` and `/model/info` expose model behavior for inspection.
- `iterative_procrustes` and alignment refinement were added for baseline quality.
- SentencePiece tokenization was introduced for Kikuyu morphology experiments.
- Model runs are versioned in `models/` and configuration resolves the latest run.
- Current baseline metrics and API examples are documented in README.

## Next Milestone Work

1. Expand high-quality parallel data.
2. Improve monolingual corpora used by FastText.
3. Rebuild the corpus and compare baseline metrics after each meaningful data
   improvement.

## Blockers

None.
