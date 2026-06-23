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

Latest baseline BLEU after recent corpus improvements:

| Direction | BLEU |
|---|---:|
| Kikuyu to English | 5.34 |
| English to Kikuyu | 4.91 |

## Next Work

1. Continue the Bible extraction phase with 2 Corinthians.
2. Rebuild training splits after the extraction pass reaches a useful stopping point.
3. Retrain the FastText baseline and compare metrics before moving toward NLLB work.

## Blockers

None.
