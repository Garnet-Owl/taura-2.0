# Changelog

Short history of what changed and why it matters. Detailed technical notes
belong in handoffs, tests, and code comments.

## 2026-06-23 - Planning and Tracking Cleanup
- Reworked planning docs so `MASTER_PLAN.md` explains milestones, progress updates show milestone status, and this changelog stays short.
- Updated agent instructions so future changelog entries use 1-2 plain-language bullets instead of long technical task lists.

## 2026-06-23 - Bible Corpus Extraction
- Improved Bible extraction reliability by fixing page-boundary truncation, header bleed, section-heading noise, and verse alignment issues.
- Added validated aligned corpora for Matthew, Mark, Luke, John, Acts, Romans, and 1 Corinthians; the test suite reached 70 passing tests.
- Added the 2 Corinthians extractor and aligned corpus with 257 validated verse pairs for the next corpus rebuild.

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
