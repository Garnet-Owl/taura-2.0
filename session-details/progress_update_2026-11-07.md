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
- N10 (Kaggle `jameswanjiku/taura-marian-bt`, 3,489 val): 20,000 back-translated pairs hurt Ki->En (35.27 / 54.31 vs N8 41.55 / 57.97). En->Ki control 26.82 / 54.94. Back-translation with the current En->Ki model is rejected; published models not refreshed.

## Update: N11
- N11 (Kaggle `jameswanjiku/taura-nllb-enki`, En->Ki only, NLLB-200-distilled-600M, 3 epochs, 3,489 val): 29.08 BLEU / 56.97 chrF vs N8 26.99 / 54.88. CT2 int8 631 MB, ~2.1 s/sentence on 4 CPU threads (beam 4): too slow/large to ship. Not published.

## Update: N12
- N12 (CPU only, N11 CT2 int8 model, 40 random val sentences, 4 threads): greedy 1.44 s/sentence (24.25 BLEU on the sample), beam 2 2.14 s, beam 4 2.21 s. Lower beam does not make NLLB-600M shippable; distillation into Marian is still the open path. No model published.

## Update: N13
- N13 (Kaggle `jameswanjiku/taura-nllb-distill`, En->Ki only, 3,489 val): Marian trained on real pairs + 48,393 NLLB-N11 teacher translations (train English + 20k Tatoeba), 8 epochs: 26.26 BLEU / 54.83 chrF vs N8 26.99 / 54.88. Sequence-level distillation does not transfer the gain; not published. Kaggle note: CT2 on GPU needs `pip install nvidia-cublas-cu12` and a ctypes preload.
