# Taura 2.0 - Progress Update (2026-08-29)

Progress updates are milestone snapshots. Fine-grained implementation details
belong in `CHANGELOG.md` and handoff notes.

## Overall Status

Still in Milestone 3: corpus expansion and quality control.

The local branch had drifted 26 commits ahead of remote `main` with an NLLB-200 /
BM25 hybrid rewrite of the translation stack. That rewrite performed worse than
the retrieval stack already on `main`, so it was set aside rather than pushed. It
is preserved on the `backup/local-26-commits` branch and the
`pre-reset-2026-08-29` tag if any of it is needed later.

The branch was rebuilt on top of remote `main`. The active algorithm is again the
remote's FastText + Orthogonal Procrustes retrieval pipeline.

## Current Phase

Corpus additions kept from the local work:

- Exodus: 1,213 aligned verse pairs, zero missing and zero empty verses.
- Isaiah: 1,292 aligned verse pairs, zero missing and zero empty verses.
- Parallel corpus size after these additions: 19,255 sentence pairs (20 Bible books).

Latest evaluated checkpoint is still Run 7 (Jeremiah, 16,750 pairs):

- Kikuyu -> English: 39.18 BLEU, 54.38 chrF.
- English -> Kikuyu: 38.73 BLEU, 57.62 chrF.

## Next Work

1. Manually run `uv run python -m scripts.train_embeddings` to retrain on the
   expanded 19,255-pair corpus.
2. Record the new metrics as Run 8 in `README.md` and compare against Run 7.
3. Continue extracting the next large Bible book once the retraining result is in.

## Blockers

Long-running training and evaluation commands are run manually by the user, not
inside agent context.
