# Changelog

Short history of what changed and why it matters. Detailed technical notes
belong in handoffs, tests, and code comments.

## 2026-08-29 - Keep Exodus/Isaiah data, drop local algorithm changes
- Rebuilt the local branch on top of remote `main`: the remote's FastText + Procrustes retrieval stack is kept as-is, and the local NLLB/BM25 rewrite is set aside (preserved on the `backup/local-26-commits` branch and the `pre-reset-2026-08-29` tag).
- Carried over only the corpus work: Exodus (1,213 pairs) and Isaiah (1,292 pairs) aligned CSVs, their extractors, the page-number bleed fixes in the base parser, and the parser tests. Corpus is now 19,255 pairs; retraining on the expanded corpus is still pending.

## 2026-06-23 - Swahili NLP Improvements and Galatians Extraction
- Implemented Swahili NLP techniques (parallel proper-noun anchors and Morfessor diagnostics) resulting in a massive improvement to retrieval BLEU (from ~5 to ~21).
- Added the Galatians extractor and aligned corpus with 149 validated verse pairs.

## 2026-06-23 - Planning and Tracking Cleanup
- Reworked planning docs so `MASTER_PLAN.md` explains milestones, progress updates show milestone status, and this changelog stays short.
- Updated agent instructions so future changelog entries use 1-2 plain-language bullets instead of long technical task lists.

## 2026-06-23 - Bible Corpus Extraction
- Improved Bible extraction reliability by fixing page-boundary truncation, header bleed, section-heading noise, and verse alignment issues.
- Added validated aligned corpora for Matthew, Mark, Luke, John, Acts, Romans, and 1 Corinthians; the test suite reached 70 passing tests.
- Added the 2 Corinthians extractor and aligned corpus with 257 validated verse pairs for the next corpus rebuild.

## 2026-06-23 - Agriculture Data, Recursive Loading, and Morfessor
- Added 3,852 agriculture sentence pairs (coffee, dairy, poultry, potato, banana, mango, cabbage, avocado) to `data/parallel/agriculture/` — total corpus grows from 5,911 to 9,763 pairs.
- Data loading is now recursive: adding a new sub-folder under `data/parallel/` is all that's needed to include a new source.
- FastText n-gram range tightened to minn=2/maxn=7 to better capture Kikuyu's short agglutinative prefixes.
- Morfessor unsupervised morphological segmentation applied to Kikuyu before FastText training, splitting verb prefixes into separate tokens for cleaner morpheme-level embeddings.

## 2026-06-23 - Training Run Data Versioning
- Monolingual training text files are now written into each run's directory (e.g. `models/run_*/train.kikuyu`) instead of overwriting `data/monolingual/`, so every training experiment is fully reproducible.

## 2026-06-23 - Ruff Config Upgrade
- Broadened linting coverage with bugbear, isort, and non-top-level import detection; preprocessing files are excluded so hand-tuned regex patterns are never touched.

## 2026-06-23 - Hybrid Alignment and Test Coverage
- Training now uses three anchor sources for Procrustes alignment: parallel sentence embeddings, seed dictionary word pairs, and identical-string vocabulary pairs — combining sentence-level precision with vocabulary-level breadth.
- Updated and expanded unit tests to cover CSV loading, retrieval accuracy (Top-1/Top-5/MRR), and metrics merging; all 78 tests pass.

## 2026-06-23 - Baseline Quality Check
- Re-ran offline evaluation after corpus improvements and recorded better baseline BLEU scores: 5.34 for Kikuyu to English and 4.91 for English to Kikuyu.

## 2026-06-23 - Ephesians and Philippians Extraction
- Added the Ephesians and Philippians extractors and aligned corpus with 155 and 104 validated verse pairs respectively.

## 2026-06-23 - Colossians and 1 Thessalonians Extraction
- Added the Colossians and 1 Thessalonians extractors and aligned corpus with 95 and 89 validated verse pairs respectively.

## 2026-06-23 - Psalms Extraction
- Shifted extraction strategy to prioritize the largest Bible books first. Added the Psalms extractor, producing a massive aligned corpus addition with 2,461 validated verse pairs.

## 2026-06-23 - Genesis, Proverbs, and Ecclesiastes Extraction
- Extracted and aligned three more large books: Genesis (1,533 verses), Proverbs (915 verses), and Ecclesiastes (222 verses), increasing total parallel sentences by 2,670 pairs.

## 2026-06-23 - Jeremiah Extraction
- Extracted and aligned Jeremiah (1,364 verses) continuing the strategy of prioritizing the largest books to maximize corpus size.

## 2026-10-17 - Evaluation Memory Fix
- Fixed training evaluation crashing on small machines: the validation step no longer starts one multi-gigabyte model copy per CPU core when there are only 100 sentences to embed.

## 2026-10-17 - Run 8 Evaluation (Exodus + Isaiah)
- Retrained on 19,255 pairs and recorded Run 8 in the README. Scores dipped versus Run 7, but a second identical retrain swung by up to 6 BLEU, so the dip is within run-to-run noise on the small 100-sentence validation set.

## 2026-10-17 - Numbers Extraction
- Extracted and aligned Numbers (1,288 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 21 books and the parallel corpus to 20,543 pairs. Not yet retrained, so it is not reflected in the metrics.

## 2026-10-18 - Run 9 Evaluation (Numbers)
- Retrained twice on the 20,643-pair corpus including Numbers and recorded the average in the README (Ki to En 32.92 BLEU, En to Ki 35.58); the vocabulary alignment grew to about 8,320 matched words, and the two runs differed by up to 5.5 BLEU, confirming how noisy the 100-sentence check is.

## 2026-10-18 - Ezekiel Extraction
- Extracted and aligned Ezekiel (1,273 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 22 books. Not yet retrained, so it is not reflected in the metrics.

## 2026-10-18 - Job Extraction
- Extracted and aligned Job (1,070 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 23 books. Not yet retrained, so it is not reflected in the metrics.

## 2026-10-18 - Run 10 Evaluation (Ezekiel)
- Retrained twice on 21,916 pairs including Ezekiel and recorded the average in the README (Ki to En 32.20 BLEU, En to Ki 39.04); the vocabulary alignment grew to 8,533 matched words, and the two runs again differed by several BLEU, so small changes are not meaningful.

## 2026-10-18 - Run 11 Evaluation (Job)
- Retrained twice on 22,986 pairs including Job and recorded the average in the README (Ki to En 32.88 BLEU, En to Ki 37.88); the vocabulary alignment grew to about 8,680 matched words, and the two runs differed by over 4 BLEU, so the small En to Ki dip is noise rather than a regression.

## 2026-10-18 - Deuteronomy Extraction
- Extracted and aligned Deuteronomy (959 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 24 books. Not yet retrained, so it is not reflected in the metrics.

## 2026-10-18 - Run 12 Evaluation (Deuteronomy)
- Retrained twice on 23,945 pairs including Deuteronomy and recorded the average in the README (Ki to En 35.99 BLEU, En to Ki 33.49); English to Kikuyu dipped from Run 11, but the two runs differed by 4.4 BLEU, so this is most likely noise and is flagged for watching.

## 2026-10-18 - 1 Chronicles Extraction
- Extracted and aligned 1 Chronicles (942 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 25 books. Not yet retrained, so it is not reflected in the metrics.

## 2026-10-18 - Run 13 Evaluation (1 Chronicles)
- Retrained twice on 24,887 pairs including 1 Chronicles and recorded the average in the README (Ki to En 34.38 BLEU, En to Ki 35.94); English to Kikuyu recovered from the Run 12 dip, but the two runs differed by 6 to 8 BLEU, so the movement is noise.

## 2026-10-18 - Leviticus Extraction
- Extracted and aligned Leviticus (859 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 26 books. Not yet retrained, so it is not reflected in the metrics.

## 2026-10-18 - 2 Chronicles Extraction
- Extracted and aligned 2 Chronicles (822 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 27 books; numbers written inside verses (such as 3,600) no longer get mistaken for verse markers. Not yet retrained, so it is not reflected in the metrics.

## 2026-10-18 - Run 14 Evaluation (Leviticus)
- Retrained twice on 25,746 pairs including Leviticus and recorded the average in the README (Ki to En 32.13 BLEU, En to Ki 31.37); both directions are lower than Run 13, but the two runs differed by up to 17 BLEU on identical data, so this is most likely noise rather than a real regression

## 2026-10-18 - Agent Instructions
- Added owner authorisations to CLAUDE.md and AGENTS.md: agents may try better methods, grow the corpus with verified data, and use free GPU providers such as Kaggle, with steps for supplying credentials.
