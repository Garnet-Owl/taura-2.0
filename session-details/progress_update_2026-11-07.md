# Taura 2.0 - Progress Update (2026-11-07)

## Overall Status
Milestone 3 corpus complete (66 books); still in quality control. Training text is now cleaned in `scripts/prepare_dataset.py` (27,628 / 3,489 / 3,360 split).

## Latest Metrics
- N8 (Kaggle `jameswanjiku/taura-marian-syn`, train + 1,231 synthetic pairs at confidence >= 0.5, 3,489 val): Ki->En 41.80 BLEU / 58.11 chrF, En->Ki 26.84 / 54.90. Small gain over N7; published models not refreshed.
- N7 (Kaggle `jameswanjiku/taura-marian-clean`, held-out, 3,489 val): Ki->En 41.20 BLEU / 57.87 chrF, En->Ki 26.72 / 54.73. Same as N6 within noise; published models not refreshed.
- FastText not yet retrained on the cleaned split (last: Run 34, 35.13 / 38.35 BLEU on the older val).

## Next Work
FastText retrain on the cleaned split; synthetic data batches; En->Ki Marian improvement.

## Blockers
None.
