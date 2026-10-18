# Taura 2.0 - Progress Update (2026-10-18)

## Overall Status

Still in Milestone 3: corpus expansion and quality control.

## Current Phase

- Run 8 (Exodus + Isaiah, 19,255 pairs) evaluated: Ki->En 31.10 BLEU / 46.37 chrF, En->Ki 31.39 BLEU / 53.07 chrF, MNN 7,947.
- This is a regression from Run 7 (39.18 / 38.73 BLEU). Likely cause (untested): the 100-sentence validation set is New Testament epistle text, while the added data is Old Testament, so retrieval is diluted. The validation set is noisy at this size.
- Numbers extracted: 1,288 pairs, zero missing/empty. Corpus is now 20,543 pairs (21 books). Run 9 retrains on this.

## Next Work

1. Consider a validation set that spans the Bible (not only the last 100 pairs) so metrics are comparable across book additions (changes the metric baseline, owner decision recommended).
2. Extract the next largest book without data: Ezekiel (1,273 verses), then Job, Deuteronomy.

## Blockers

None.
