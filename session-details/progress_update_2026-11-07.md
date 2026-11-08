# Taura 2.0 - Progress Update (2026-11-07)

## Overall Status
Milestone 3 corpus complete (66 books); still in quality control. Training text is now cleaned in `scripts/prepare_dataset.py` (27,628 / 3,489 / 3,360 split).

## Latest Metrics
- N7 (Kaggle `jameswanjiku/taura-marian-clean`, held-out, 3,489 val): Ki->En 41.20 BLEU / 57.87 chrF, En->Ki 26.72 / 54.73. Same as N6 within noise; published models not refreshed.
- FastText not yet retrained on the cleaned split (last: Run 34, 35.13 / 38.35 BLEU on the older val).

## Next Work
FastText retrain on the cleaned split; synthetic data batches; En->Ki Marian improvement.

## Blockers
None.

## Update: N8
- N8 (Kaggle `jameswanjiku/taura-marian-synth`, dataset `jameswanjiku/taura-splits-20261107-synth`, held-out, 3,489 val): Ki->En 41.55 BLEU / 57.97 chrF, En->Ki 26.99 / 54.88. Train = cleaned split + 1,231 synthetic pairs (conf >= 0.5). +0.35 / +0.27 BLEU vs N7: noise; published models not refreshed.

## Update: F36
- F36 (Kaggle `jameswanjiku/taura-fasttext-run36`, held-out, 3,489 val): FastText retrieval Ki->En 36.26 BLEU / 52.21 chrF, En->Ki 36.64 / 57.73. Word-by-word ~1 BLEU. Published FastText not refreshed.

## Update: N9
- N9 (Kaggle `jameswanjiku/taura-marian-enki20`, En->Ki only, 20 epochs, 3,489 val): 27.15 BLEU / 54.90 chrF vs N8 26.99 / 54.88. Noise; published models not refreshed.

## Update: N10
- N10 (Kaggle `jameswanjiku/taura-marian-bt`, 3,489 val): Ki->En with 20,000 synthetic back-translated pairs 35.27 BLEU / 54.31 chrF (N8: 41.55 / 57.97), a regression; En->Ki 12-epoch generator 26.82 / 54.94. Not adopted. Next lever should avoid noisy machine-made Kikuyu (real Kikuyu monolingual text for true back-translation, or larger base model).
