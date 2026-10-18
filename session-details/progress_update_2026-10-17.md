# Taura 2.0 - Progress Update (2026-10-17)

## Overall Status

Still in Milestone 3: corpus expansion and quality control.

## Current Phase

Run 8 (Exodus + Isaiah, 19,255 pairs) is evaluated:

- Kikuyu -> English: 28.95 BLEU, 44.34 chrF, MRR 0.277, MNN 7,981.
- English -> Kikuyu: 35.47 BLEU, 53.75 chrF, MRR 0.338.

Lower than Run 7 (39.18 / 38.73 BLEU). An identical repeat retrain scored 35.49 / 32.24 BLEU, so single-run
differences of several BLEU are within noise (multithreaded, unseeded FastText; 100-sentence validation set).
Not treated as a confirmed regression.

## Corpus

Numbers added after Run 8: 1,288 validated pairs (zero missing/empty). Corpus is now 21 books and 20,543 pairs; a retrain (Run 9) is pending.

## Next Work

1. Make evaluation more trustworthy: average several training runs or enlarge the validation set (owner decision on split policy).
2. Retrain on 20,543 pairs and record Run 9 (ideally averaged over several runs).
3. Then extract Ezekiel (1,273 verses), the next largest unextracted book.

## Blockers

None.
