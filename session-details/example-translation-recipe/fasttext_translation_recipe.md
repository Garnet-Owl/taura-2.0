# FastText Translation Recipe — Embedding-Based Word Translation

## Overview

This recipe documents how to use aligned FastText embeddings to perform word/phrase
translation via nearest-neighbour search in a shared vector space. It is the conceptual
foundation for the Taura 2.0 cross-lingual retrieval system and the basis for the HNSW
experiment in `var/hnsw-experiment/`.

---

## Core Idea

FastText (Facebook Research) maps every word in a language to a 100-300 dimensional
float vector. When you train (or download) models for two languages using the same
algorithm on comparable corpora, the resulting vector spaces have a similar geometric
structure. A linear projection matrix (solved via orthogonal Procrustes) can then
*align* the two spaces so that the English vector for "fast" lands near the Kikuyu
vector for "haraka", etc.

Once aligned, translation becomes **nearest-neighbour search**:

```
source word  →  src embedding  →  project into target space  →  find closest target word
```

---

## Step-by-Step Recipe

### 1. Train (or load) monolingual FastText models

```python
import fasttext

en_model = fasttext.load_model("models/run_latest/en.bin")
ki_model = fasttext.load_model("models/run_latest/ki.bin")
```

### 2. Build a seed dictionary (anchor pairs)

Use identical strings (names, numbers, loanwords) as the initial anchor set,
then refine iteratively with Mutual Nearest Neighbours (MNN).

```python
# identical-string pairs are a zero-cost, no-dictionary baseline
common = set(en_model.get_words()) & set(ki_model.get_words())
seed_words = sorted(w for w in common if len(w) > 2)[:5000]
```

### 3. Learn the alignment matrix (Procrustes)

Given parallel anchor embeddings X (source) and Y (target):

```
M   = Y @ X.T
U, _, Vt = np.linalg.svd(M)
W   = U @ Vt          # orthogonal projection matrix
```

Iterate: project source vocab → find MNN with CSLS → re-solve Procrustes (5 rounds typical).

### 4. Build a nearest-neighbour index over the target vocabulary

**Brute-force (current approach, O(N) per query):**
```python
scores = tgt_vocab_embeddings @ projected_src_vec   # cosine after normalisation
best   = np.argmax(scores)
```

**HNSW (fast approximate NN, O(log N) per query):**
```python
import hnswlib

dim   = 100
index = hnswlib.Index(space="cosine", dim=dim)
index.init_index(max_elements=len(tgt_words), ef_construction=200, M=16)
index.add_items(tgt_vocab_embeddings)           # normalised vectors
index.set_ef(50)                                 # query-time accuracy

labels, distances = index.knn_query(projected_src_vec, k=5)
translations = [tgt_words[i] for i in labels[0]]
```

### 5. Apply CSLS re-ranking (reduces hubness)

Cross-Lingual Similarity Scaling penalises "hub" vectors that appear as neighbours
of many unrelated source words:

```
csls(x, y) = 2 * cos(x, y) - r_T(x) - r_S(y)
```

Where `r_T(x)` is the mean cosine of `x` to its k-NN in the target space, and
`r_S(y)` is the mean cosine of `y` to its k-NN in the source space.

Retrieve the top-50 HNSW candidates, then re-rank with CSLS — best of both worlds.

### 6. Sentence-level translation (retrieval)

For sentence pairs (parallel corpus retrieval):

```
src sentence  →  mean-pool word embeddings  →  project  →  cosine search over tgt sentence bank
```

The sentence bank embeddings are precomputed once and stored as `precomputed_tgt_embeddings`.

---

## Algorithm Comparison

| Algorithm         | Query complexity | Index build  | Notes                              |
|-------------------|------------------|--------------|------------------------------------|
| Brute-force cosine| O(N · d)         | None         | Current production approach        |
| HNSW              | O(log N · d)     | O(N log N)   | Best accuracy/speed tradeoff       |
| FAISS IVF-Flat    | O(N/C · d)       | O(N)         | Needs GPU for best speed           |
| Annoy             | O(log N · d)     | O(N log N)   | Memory-mapped, read-only           |

For our vocabulary size (~50k–200k words), HNSW from `hnswlib` is the recommended
upgrade path. It maintains >95% recall versus brute-force at 10–50× the query speed.

---

## Taura 2.0 Specifics

| Item               | Value                                              |
|--------------------|----------------------------------------------------|
| Source languages   | English (en) ↔ Kikuyu (ki)                        |
| Embedding dim      | 100 (configurable at training time)                |
| Alignment file     | `models/run_latest/proj_en_ki.npy` (and reverse)  |
| Current search     | Brute-force cosine + CSLS (embeddings.py)          |
| Experiment         | `var/hnsw-experiment/` — HNSW index + CSLS rerank |

---

## References

- [fastText aligned vectors](https://fasttext.cc/docs/en/aligned-vectors.html)
- [hnswlib — Hierarchical Navigable Small Worlds](https://github.com/nmslib/hnswlib)
- [CSLS paper — Lample et al. 2018](https://arxiv.org/abs/1710.04087)
- [Instant Distance (Rust HNSW)](https://github.com/instant-labs/instant-distance)
- [FAISS](https://github.com/facebookresearch/faiss)
