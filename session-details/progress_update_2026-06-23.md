# Taura 2.0 - Progress Update (2026-06-23)

This file tracks milestone progress for the current workstream. It is not a
second changelog. Use `CHANGELOG.md` for detailed per-change history and this
file for milestone status, current focus, blockers, and next work.

## Milestone Status

| Milestone | Status | Evidence |
|---|---|---|
| 0 - Project Foundation | Complete | `uv`, Ruff, pytest, CI, contributor docs, package structure |
| 1 - FastText Baseline | Complete | embeddings, alignment matrices, retrieval metrics, versioned model runs |
| 2 - API, Evaluation, and Demo UI | Complete | FastAPI translation service, candidates endpoint, model info endpoint, feedback UI, BLEU/ChrF evaluation |
| 3 - Corpus Expansion and Quality Control | In progress | seed dictionary, Bible extraction phase, monolingual corpus expansion, improved baseline metrics |
| 4 - NLLB Fine-Tuning Readiness | Not started | roadmap exists; golden split and training workflow still pending |
| 5 - NLLB Training and Evaluation | Not started | no NLLB adapter trained yet |
| 6 - Release Packaging | In progress | public README and dataset/model hosting notes are improving |

## Milestone 3 - Current Phase

**Phase:** Bible corpus extraction and validation.

Purpose: extract high-quality aligned Kikuyu-English scripture pairs as one
data-processing phase within the broader corpus-expansion milestone.

Current evidence:
- Modular Bible parser architecture exists under `app/preprocessing/bible/`.
- `BaseBibleParser` handles page ranges, header parsing, body extraction,
  page-boundary continuation, and English footnote cleanup.
- Extracted and validated books so far:
  - Matthew: 1,070 aligned pairs.
  - Mark: aligned corpus generated.
  - Luke: aligned corpus generated.
  - John: 879 aligned pairs.
  - Acts: 1,007 aligned pairs.
  - Romans: 431 aligned pairs; known WEB versification gap for Romans 16:26-27.
  - 1 Corinthians: 437 aligned pairs.
- Latest full test evidence after 1 Corinthians: 70 passing tests.

## Current Quality Snapshot

Latest recorded FastText baseline after clean Bible corpus improvements:

| Direction | BLEU |
|---|---:|
| Kikuyu to English | 5.34 |
| English to Kikuyu | 4.91 |

These are baseline retrieval metrics, not final sequence-to-sequence quality.
The target NLLB path is still required for stronger contextual translation.

## Next Work

1. Continue the Bible extraction phase with 2 Corinthians.
2. Keep extractor details in `CHANGELOG.md` and handoffs unless they change the
   milestone status.
3. After the New Testament extraction pass reaches a useful stopping point,
   rebuild the parallel splits, retrain the FastText baseline, and compare
   metrics.
4. Start Milestone 4 by defining a golden evaluation split and NLLB fine-tuning
   workflow.

## Blockers

None.
