# Taura 2.0 - Progress Update (2026-10-31)

## Overall Status

Still in Milestone 3: corpus expansion and quality control.

## Current Phase

Run 19 (2 Samuel added, 23,593 train pairs, 2,984 val pairs = Run 18's 2,906 plus 2 Samuel's 78), mean of two retrains:
Ki->En 33.91 BLEU / 49.33 chrF, Top-1 22.8%, Top-5 41.0%, MRR 0.316; En->Ki 33.21 / 53.93, Top-1 19.7%, Top-5 37.9%,
MRR 0.289; MNN about 8,700. Retrain A: 32.38 / 32.89 BLEU, retrain B: 35.44 / 33.52. Ki->En +2.5 and En->Ki -1.1 vs
Run 18, inside the 3.1 BLEU run-to-run spread. (Retrain A was OOM-killed during Procrustes when a CPU scoring job ran
beside it; it resumed from its saved FastText models, so only the alignment and evaluation were recomputed.)
Joshua was extracted after Run 19 started and is not in Run 19's training data.

Run 18 (2 Kings added, 23,047 train pairs, 2,906 val pairs): Ki->En 31.42 / 47.43, En->Ki 34.33 / 54.48.

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

GPU run N3 (Kaggle `jameswanjiku/taura-marian-ft` v2, Marian, stable split, fixed epochs Ki->En 4 / En->Ki 7, 30 min T4),
scored on CPU int8 on Run 18's 2,906 val pairs: Ki->En 39.56 / 56.30 (beam 4), 34.98 / 53.07 (greedy); En->Ki 25.19 / 53.47
(beam 4), 24.22 / 52.32 (greedy). Latency per sentence beam 4: 0.59 s / 1.34 s; greedy 0.29 s / 0.64 s. 78 MB per
direction. Uploaded to HF `Garnet-Owl/taura-marian-kikuyu-english` (replaces N2; N2 is in the repo history).

## Corpus

32 Bible books plus agriculture data: 30,266 pairs loaded, 30,101 unique (2 Samuel and Joshua added 2026-10-31; split now 24,118 train / 3,042 val / 2,941 test).

## Next Work

1. Improve En->Ki further (25.19 BLEU, the weak direction): e.g. add Kikuyu tokens to the en-mul vocabulary or
   back-translate monolingual Kikuyu; compare on the same val.tsv with CPU latency.
2. Run 20 with Joshua (extracted 2026-10-31) on the current split, then extract Judges (618).

## Blockers

None.

## Owner Decisions (2026-10-18)

- Validation split: seeded random 80/10/10 (train/validation/test) across all books. Done in Run 16.
- Method: experiment with lighter translation models trained on the Kaggle GPU, provided inference runs fast on CPU.
  Kaggle GPU access was verified this session (2x Tesla T4).
