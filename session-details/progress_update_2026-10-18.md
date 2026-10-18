# Taura 2.0 - Progress Update (2026-10-18)

## Overall Status

Still in Milestone 3: corpus expansion and quality control.

## Current Phase

The split is now stable: each pair is placed in train / validation / test by a seeded hash of its text (seed 42), so adding a
book only appends pairs. Run 17 (new baseline, 1 Samuel included) trained on 22,467 train pairs and was scored on 2,836
validation pairs, mean of two retrains (M and N):

- Kikuyu -> English: 33.01 BLEU, 49.22 chrF, Top-1 21.7%, Top-5 39.6%, MRR 0.305.
- English -> Kikuyu: 34.67 BLEU, 54.82 chrF, Top-1 21.8%, Top-5 38.9%, MRR 0.304.
- MNN about 8,668.

The runs differ by 3.8 BLEU Ki->En. Run 17 is not comparable with Run 16 (different validation verses); Run 18 onward will
be. The test split has not been used.

Run 16 (previous shuffled split, 2,723 validation pairs): Ki->En 30.82 / 47.41, En->Ki 35.84 / 55.65.

GPU experiments below were scored on the Run 16 validation split; they need re-scoring on the stable split (the Kaggle
dataset `jameswanjiku/taura-splits-20261018` now holds the new train.tsv / val.tsv).

GPU experiments on the Run 16 validation split (generated translations, not retrieval; not directly comparable with FastText):

- NLLB-600M fine-tuned (Kaggle T4, 75 min): Ki->En 37.95 BLEU / 57.51 chrF, En->Ki 27.51 / 54.85. 623 MB int8, 1.5-3.4 s
  per sentence on CPU. Too slow for the CPU target.
- Marian opus-mt fine-tuned (Kaggle T4, 20 min, 77M params per direction): Ki->En 39.21 / 55.67, En->Ki 22.13 / 50.45
  (beam 4). 78 MB int8 each; 0.42 s (Ki->En) and 1.0 s (En->Ki) per sentence greedy on CPU, 75 / 137 ms batched; greedy
  CPU int8 scores 33.98 / 20.67 BLEU. Served by the API's 'neural' method. Model: private HF repo
  Garnet-Owl/taura-marian-kikuyu-english.

## Corpus

29 Bible books plus agriculture data: 28,194 pairs loaded, 28,036 unique.

## Next Work

1. Retrain Marian on the stable split (more epochs for En->Ki inside a 15-20 minute GPU budget) and re-score both
   directions on the new val.tsv, with CPU latency.
2. Next largest unextracted book: 2 Kings (719 verses), then Run 18 (directly comparable with Run 17).

## Blockers

None.

## Owner Decisions (2026-10-18)

- Validation split: seeded random 80/10/10 (train/validation/test) across all books. Done in Run 16.
- Method: experiment with lighter translation models trained on the Kaggle GPU, provided inference runs fast on CPU.
  Kaggle GPU access was verified this session (2x Tesla T4).
