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

## Corpus

28 Bible books plus agriculture data: 27,384 pairs loaded, 27,226 unique.

## Next Work

1. GPU experiment: fine-tuned NLLB-200-distilled-600M on Kaggle (see handoff). CPU speed is a concern.
2. Next largest unextracted book: 1 Samuel (810 verses), then retrain on the same split.

## Blockers

None.

## Owner Decisions (2026-10-18)

- Validation split: seeded random 80/10/10 (train/validation/test) across all books. Done in Run 16.
- Method: experiment with lighter translation models trained on the Kaggle GPU, provided inference runs fast on CPU.
  Kaggle GPU access was verified this session (2x Tesla T4).
