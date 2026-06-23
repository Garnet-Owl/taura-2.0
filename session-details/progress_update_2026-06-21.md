# Taura 2.0 - Progress Update (2026-06-21)

Progress updates are milestone snapshots. They should explain where the project
stands, not repeat the changelog.

## Overall Status

The baseline translator is now easier to inspect and compare. The project has
API endpoints for model behavior, clearer metrics, and early improvements for
Kikuyu morphology through subword tokenization.

## Milestones

| Milestone | Status | What this means |
|---|---|---|
| Project foundation | Complete | Tooling, CI, and setup docs are aligned around `uv`. |
| FastText baseline | Complete | Bidirectional embedding training and retrieval metrics are available. |
| API and demo UI | Complete | Translation, candidate, model-info, feedback, and demo UI surfaces exist. |
| Corpus expansion | In progress | Training quality now depends most on better data. |
| NLLB fine-tuning | Not started | The high-accuracy model path still needs a golden split and training workflow. |
| Release packaging | In progress | README and model notes are improving, but not final. |

## Current Focus

Improve baseline quality and reproducibility before starting NLLB fine-tuning.

## Recent Evidence

- Users can inspect candidate translations and model metadata through the API.
- Subword tokenization and alignment refinement improved experiment quality.
- Model runs are versioned so results can be compared more safely.

## Next Work

1. Add more high-quality parallel data.
2. Expand monolingual corpora.
3. Retrain and compare baseline metrics after data changes.

## Blockers

None.
