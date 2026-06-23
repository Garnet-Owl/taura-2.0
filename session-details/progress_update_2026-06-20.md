# Taura 2.0 - Progress Update (2026-06-20)

Progress updates are milestone snapshots. They should explain where the project
stands, not repeat the changelog.

## Overall Status

The project has a working FastText baseline and a usable API foundation. The
main work is moving from "it runs" to "the data and metrics are strong enough to
trust."

## Milestones

| Milestone | Status | What this means |
|---|---|---|
| Project foundation | Complete | The repo can be installed, tested, and developed with `uv`, Ruff, pytest, and CI. |
| FastText baseline | Complete | The first bidirectional translation baseline can train and produce metrics. |
| API and demo UI | In progress | Translation service exists; evaluation and user-facing docs still need polish. |
| Corpus expansion | Not started | The project still needs more trusted Kikuyu-English data. |
| NLLB fine-tuning | Not started | The future sequence-to-sequence model path is not ready yet. |
| Release packaging | In progress | Basic docs exist, but public release material is still being improved. |

## Current Focus

Stabilize the baseline and make the service/evaluation flow understandable for
future contributors.

## Recent Evidence

- Preprocessing, splitting, FastText training, and alignment are implemented.
- FastAPI can serve translation requests.
- Offline BLEU/ChrF evaluation has started.

## Next Work

1. Finish documenting the API and evaluation flow.
2. Start expanding and cleaning the training data.
3. Compare model quality after each meaningful data improvement.

## Blockers

None.
