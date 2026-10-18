# Taura 2.0 - Progress Update (2026-10-18)

## Overall Status

Still in Milestone 3: corpus expansion and quality control.

## Current Phase

Run 16 (new baseline) is evaluated on the seeded 80/10/10 split (`data/splits/`, seed 42, 158 duplicate pairs removed):
trained on 21,781 train pairs (all 28 books plus agriculture, 1 Kings included), scored on 2,723 validation pairs,
mean of two retrains (K and L):

- Kikuyu -> English: 30.82 BLEU, 47.41 chrF, Top-1 19.5%, Top-5 38.7%, MRR 0.290.
- English -> Kikuyu: 35.84 BLEU, 55.65 chrF, Top-1 22.8%, Top-5 41.7%, MRR 0.320.
- MNN about 8,410.

The two runs agree within 2.5 BLEU, so the new validation set is stable. Runs 1-15 used the old last-100 set and are not
comparable. The test split has not been used.

GPU experiments on the same validation split (generated translations, not retrieval; not directly comparable with FastText):

- NLLB-600M fine-tuned (Kaggle T4, 75 min): Ki->En 37.95 BLEU / 57.51 chrF, En->Ki 27.51 / 54.85. 623 MB int8, 1.5-3.4 s
  per sentence on CPU. Too slow for the CPU target.
- Marian opus-mt fine-tuned (Kaggle T4, 20 min, 77M params per direction): Ki->En 39.21 / 55.67, En->Ki 22.13 / 50.45
  (beam 4). 78 MB int8 each; 0.42 s (Ki->En) and 1.0 s (En->Ki) per sentence greedy on CPU, 75 / 137 ms batched; greedy
  CPU int8 scores 33.98 / 20.67 BLEU. Served by the API's 'neural' method. Model: private HF repo
  Garnet-Owl/taura-marian-kikuyu-english.

## Corpus

28 Bible books plus agriculture data: 27,384 pairs loaded, 27,226 unique.

## Next Work

1. Next largest unextracted book: 1 Samuel (810 verses), then retrain FastText and Marian on the rebuilt split.
2. Improve Marian En->Ki (the weak direction): more epochs inside a 15-20 minute GPU budget, or back-translation.

## Blockers

None.

## Owner Decisions (2026-10-18)

- Validation split: seeded random 80/10/10 (train/validation/test) across all books. Done in Run 16.
- Method: experiment with lighter translation models trained on the Kaggle GPU, provided inference runs fast on CPU.
  Kaggle GPU access was verified this session (2x Tesla T4).
