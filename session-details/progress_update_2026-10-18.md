# Taura 2.0 - Progress Update (2026-10-18)

## Overall Status

Still in Milestone 3: corpus expansion and quality control.

## Current Phase

Run 15 (2 Chronicles added, 26,568 pairs loaded) is evaluated, mean of two identical retrains (I and J):

- Kikuyu -> English: 27.01 BLEU, 44.42 chrF, Top-1 17%, Top-5 40%, MRR 0.285.
- English -> Kikuyu: 34.30 BLEU, 51.07 chrF, Top-1 19.5%, Top-5 44%, MRR 0.319.
- MNN about 9,098.

Ki->En has fallen for four averaged runs in a row (35.99, 34.38, 32.13, 27.01). Runs I and J agree within 2.0 BLEU, so this
drop is probably real, not noise. The validation set is fixed: the last 100 pairs in file order, which are all of
1 Thessalonians plus the last 11 verses of Romans. The likely cause is a domain mismatch, since the set is New Testament
letters while recent additions are all Old Testament history and law. This has not been tested.

## Corpus

1 Kings extracted (816 pairs, zero missing/empty). The corpus is 28 Bible books plus agriculture data, about 27,384 pairs.
1 Kings is not yet included in a training run.

## Next Work

1. Make evaluation representative (owner decision on split policy): a validation set sampled across all books, with fixed
   seed, kept out of training. Without it, adding OT books cannot be judged fairly.
2. Retrain on the 28-book corpus (1 Kings) as Run 16, mean of two runs.
3. Next largest unextracted book: 1 Samuel (810 verses).

## Blockers

- Owner decision on the validation split policy (see Next Work 1).
