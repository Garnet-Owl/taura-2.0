# Taura 2.0 - Progress Update (2026-06-23)

Progress updates are milestone snapshots. They should explain where the project
stands, not repeat the changelog.

## Overall Status

The project is in the corpus-expansion milestone. The active phase is extracting
clean Bible-aligned Kikuyu-English sentence pairs, then using that data to judge
whether the baseline model improves.

## Milestones

| Milestone | Status | What this means |
|---|---|---|
| Project foundation | Complete | The repo is ready for normal development and testing. |
| FastText baseline | Complete | A measurable baseline exists and can be retrained. |
| API and demo UI | Complete | Users can call the model, inspect candidates, and try the UI. |
| Corpus expansion | In progress | Bible extraction and corpus cleanup are the active work. |
| NLLB fine-tuning readiness | Not started | Golden evaluation data and training workflow are still pending. |
| NLLB training | Not started | No fine-tuned NLLB adapter exists yet. |
| Release packaging | In progress | Public docs and dataset/model hosting notes still need refinement. |

## Current Phase

Bible corpus extraction is one phase inside the larger data milestone. Individual
books are implementation details; progress is measured by validated corpus
coverage and model-quality impact.

Current extracted evidence:

| Book set | Status |
|---|---|
| Matthew, Mark, Luke, John | Extracted and validated enough to support the current corpus work. |
| Acts | Extracted with 1,007 aligned verse pairs. |
| Romans | Extracted with 431 aligned verse pairs; two English verses are a known source-text versification gap. |
| 1 Corinthians | Extracted with 437 aligned verse pairs. |
| 2 Corinthians | Extracted with 257 aligned verse pairs. |
| Galatians | Extracted with 149 aligned verse pairs. |
| Ephesians | Extracted with 155 aligned verse pairs. |
| Philippians | Extracted with 104 aligned verse pairs. |
| Colossians | Extracted with 95 aligned verse pairs. |
| 1 Thessalonians | Extracted with 89 aligned verse pairs. |
| Psalms | Extracted with 2,461 aligned verse pairs. |
| Genesis | Extracted with 1,493 aligned verse pairs. |
| Proverbs | Extracted with 915 aligned verse pairs. |
| Ecclesiastes | Extracted with 222 aligned verse pairs. |

Latest baseline BLEU after recent corpus improvements:

- **Kikuyu -> English:** 33.18 BLEU (down from 35.27, but Top-1 accuracy improved from 20% to 25%)
- **English -> Kikuyu:** 35.96 BLEU (up from 34.38)
- **Mutual Nearest Neighbors (MNN):** 5,654 (huge jump from 4,859)

## Next Work

1. Continue the Bible extraction phase with other large books (Exodus, Jeremiah, Isaiah) to maximize corpus growth.
2. Rebuild training splits after the extraction pass reaches a useful stopping point.
3. Retrain the FastText baseline and compare metrics before moving toward NLLB work.

## Recent Session Work

Ruff config upgraded (bugbear, isort, PLC0415), preprocessing files excluded from linting; hybrid three-source Procrustes alignment implemented; test suite expanded to 78 tests.

## Blockers

None.
