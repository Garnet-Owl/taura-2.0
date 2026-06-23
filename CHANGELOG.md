# Changelog

Short history of what changed and why it matters. Detailed technical notes
belong in handoffs, tests, and code comments.

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
- Cleaned type and lint issues so the project stayed safe to build on before the next corpus pass.

## 2026-06-22 - Data Expansion
- Brought in legacy Kikuyu-English data and Bible-derived parallel text to strengthen the training corpus.
- Expanded monolingual Kikuyu and English data so FastText has more language context to learn from.

## 2026-06-21 - Model Visibility and Reproducibility
- Added API support for translation candidates and model information so users can inspect what the baseline model is doing.
- Added subword tokenization, alignment refinement, and versioned model runs to make training experiments easier to compare.

## 2026-06-20 and Earlier - Project Foundation
- Built the first working FastText translation baseline with preprocessing, train/test splits, evaluation, and a FastAPI service.
- Migrated the project to `uv`, added contributor docs, CI, linting, tests, a simple web UI, and release documentation.
