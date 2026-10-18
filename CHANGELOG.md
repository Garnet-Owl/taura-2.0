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
- Recorded that the Kaggle API token is configured in the cloud environment and how agents should use it.

## 2026-10-18 - 1 Kings Extraction
- Extracted and aligned 1 Kings (816 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 28 books. Not yet retrained, so it is not reflected in the metrics.

## 2026-10-18 - Run 15 Evaluation (2 Chronicles)
- Retrained twice on 26,568 pairs including 2 Chronicles and recorded the average in the README (Ki to En 27.01 BLEU, En to Ki 34.30). Kikuyu to English fell for the fourth averaged run in a row, and this time both runs agree, so the drop is likely real. The probable cause is that the small validation set is all New Testament letters while every recent book added is Old Testament.

## 2026-10-18 - Seeded 80/10/10 Evaluation Split
- Training and evaluation now use a fixed, seeded random split across every book (80% train, 10% validation, 10% test) instead of the last 100 verses, so scores reflect the whole corpus rather than one New Testament letter. The split is rebuilt with `uv run python -m scripts.prepare_dataset` from all parallel CSVs, with 158 exact duplicate pairs removed so none can appear in both train and validation.
- Fixed loading of split files where a verse starts with a quotation mark, which previously merged many rows into one.

## 2026-10-18 - Agent Instructions
- Added GPU and compute hygiene rules for agents: check that no Taura Kaggle job is already running before starting one, make every GPU job finish on its own, and stop leftover local training at the end of each session, to save GPU and container hours.

## 2026-10-18 - Run 16 Evaluation (new split baseline)
- Retrained twice on the new seeded split (21,781 training pairs, 1 Kings included) and recorded the average in the README as a new baseline: Ki to En 30.82 BLEU, En to Ki 35.84, scored on 2,723 validation verses from every book. The two runs agree within 2.5 BLEU, so the new validation set is far more stable than the old 100-verse one; these numbers are not comparable with Runs 1-15.

## 2026-10-18 - Neural Translation Experiments
- Fine-tuned two compact neural models on the free Kaggle GPU and scored them on the new validation split: a small Marian model (78 MB per direction, trained in 20 minutes) reached 39.21 BLEU Kikuyu to English and 22.13 English to Kikuyu, and a larger NLLB-600M model reached 37.95 and 27.51 but runs about 3.5 times slower on CPU.
- The API's `/translate` endpoint now has a `neural` method that serves the Marian models on CPU (download them from the private Hugging Face repo Garnet-Owl/taura-marian-kikuyu-english into `models/marian-ct2-int8/`).

## 2026-10-18 - Stable Evaluation Split
- The 80/10/10 split now places each verse pair by a seeded hash of its text instead of a shuffle, so adding a new book only adds pairs and never moves existing ones between train, validation and test. Future runs can be compared on the same validation verses as the corpus grows (rebuilt split: 21,805 / 2,771 / 2,650 pairs).

## 2026-10-18 - 1 Samuel Extraction
- Extracted and aligned 1 Samuel (810 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 29 books. Two English PDF pages carry wrong headers (page 296 says 3:7-3:9 but runs to 4:9), so the extractor corrects them; otherwise 21 English verses would have been empty and their neighbours misaligned.

## 2026-10-18 - Run 17 Evaluation (1 Samuel, stable split baseline)
- Retrained twice with 1 Samuel on the new stable split (22,467 training pairs) and recorded the average in the README as a new baseline: Kikuyu to English 33.01 BLEU, English to Kikuyu 34.67, scored on 2,836 validation verses. The changes from Run 16 are within run-to-run noise, and later runs can now be compared directly with this one.

## 2026-10-18 - 2 Kings Extraction
- Extracted and aligned 2 Kings (719 verse pairs, zero missing and zero empty on both sides), bringing the Bible corpus to 30 books. Page headers in both PDFs were correct for this book, and the verses at every page break and the longest and shortest pairs were checked by hand to confirm the alignment.

## 2026-10-18 - Shorter README
- The README's performance section is now one small table with the starting run and the latest runs only, without the long per-run commentary; older results stay in this changelog and the git history.

## 2026-10-18 - Run 18 Evaluation (2 Kings)
- Retrained twice with 2 Kings (23,047 training pairs) and scored on the same stable validation verses as Run 17 plus 2 Kings' share (2,906 pairs): Kikuyu to English 31.42 BLEU, English to Kikuyu 34.33. Both are slightly below Run 17 but within its run-to-run spread, and the two runs agree within 0.8 BLEU, so adding 2 Kings did not measurably change quality.

## 2026-10-18 - Marian Retrain (N3)
- Retrained the small Marian neural models on the stable split, training English to Kikuyu for 7 full epochs instead of stopping at a time limit. English to Kikuyu rose from 22.13 to 25.19 BLEU and Kikuyu to English held at 39.56, measured on CPU (0.6 s and 1.3 s per sentence, 78 MB per direction). The new models replace the old ones in the Hugging Face repo Garnet-Owl/taura-marian-kikuyu-english.
