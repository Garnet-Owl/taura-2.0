# Taura 2.0

> *"Taũra"* is Kikuyu for *"Translate."*

**Taura** is an open-source machine translation engine for **Kikuyu ↔ English**, one of the first of its kind for this low-resource Bantu language. The Kikuyu are Kenya's largest ethnic group, with 9 to 10 million speakers making up roughly 17 to 20% of the country's population.

Modern translation tools largely ignore Kikuyu. Taura exists to change that, starting with strong linguistic foundations: curated parallel corpora, morphological segmentation tuned to Kikuyu's agglutinative structure, and cross-lingual embedding alignment using Orthogonal Procrustes mapping.

![Taura 2.0 Web UI](data/assets/taura-iu-screenshot.png)


## What We're Building

Taura is not just a translation API. It is a full pipeline:

- **Corpus curation:** parallel sentence pairs from the Bible (Matthew, Mark, Luke, John, Acts, Romans, 1–2 Corinthians) and agriculture sector data (coffee, dairy, poultry, potato, banana, mango, cabbage, avocado) — over 9,700 curated pairs and growing
- **Morfessor morphological segmentation:** unsupervised segmentation of Kikuyu text before FastText training, splitting agglutinative prefixes and verb suffixes into separate tokens so the model learns cleaner morpheme-level representations
- **Cross-lingual alignment:** monolingual FastText embeddings aligned via iterative Orthogonal Procrustes with three anchor sources (parallel sentence embeddings, seed dictionary, and identical-string vocabulary pairs) and CSLS-based refinement
- **Translation API:** FastAPI service with retrieval and word-by-word modes, top-K candidates, and a lightweight web UI

The long-term goal is to push translation quality to the point where Taura is genuinely useful to Kikuyu speakers, and to serve as a replicable blueprint for other low-resource African languages.


## How We Improved

> This section is updated as new techniques and data are added. Every row represents a real training run.

The table below shows how retrieval BLEU changed as alignment techniques were introduced. Numbers marked `—` were not measured for that run.

| Run | Key Changes | BLEU Ki→En | BLEU En→Ki | Top-1 Ki→En | MNN Pairs |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Baseline** | Raw FastText + simple Procrustes | 5.34 | 4.91 | — | — |
| **Hybrid alignment** | Sentence-pair anchors + seed dictionary + identical-string anchors; iterative Procrustes with MNN + CSLS | 21.00 | 35.09 | — | 3,007 |
| **Agriculture + Proper-Nouns** | +3,852 agriculture pairs; parallel proper-noun anchors added; Morfessor removed; default n-grams (`minn=3 / maxn=6`) restored | 23.35 | 34.92 | 27% | 4,788 |

The hybrid alignment is the single biggest jump — a **4× BLEU improvement** from baseline. The agriculture and proper-noun anchor run confirms the embedding space is still improving, with MNN growth to 4,751.

**What drove the 5 → 21 BLEU jump:**
Three alignment anchor sources were combined — parallel sentence embeddings, a seed dictionary, and identical-string vocabulary pairs — giving the Procrustes solver a much richer and more diverse set of constraints. Iterative refinement with Mutual Nearest Neighbors and CSLS de-hubbing then pushed the MNN count from near-zero to 3,007, meaning 3,007 Kikuyu vocabulary words found their correct English counterpart through the learned projection.

**What the literature says for similar low-resource Bantu scenarios:**
- Supervised cross-lingual alignment (what we do) consistently outperforms unsupervised methods when at least 1–5k parallel pairs are available [(Conneau et al., MUSE)](https://github.com/facebookresearch/MUSE)
- Cross-lingual transfer from related high-resource languages (e.g. Swahili → Kikuyu) can add 1.5–3.5 BLEU in low-resource Bantu pairs [(Congolese Swahili study)](https://arxiv.org/pdf/2103.10734)
- Chain-of-languages multilingual anchors (English → Swahili → Kikuyu) have shown promise for zero-resource directions [(multilingual anchor chains)](https://arxiv.org/pdf/2311.12489)


## Current Performance

> [!NOTE]
> **Metrics Key:**
> - **BLEU / chrF:** Measures translation similarity to a human reference. Higher is better.
> - **Top-1 / Top-5:** The percentage of times the exact correct translation was in the #1 or Top 5 retrieved results.
> - **MRR (Mean Reciprocal Rank):** How close the correct translation was to rank #1 on average.
> - **MNN (Mutual Nearest Neighbors):** The number of Kikuyu and English vocabulary words that perfectly aligned (each word is the other's #1 closest match). Higher means a better vocabulary bridge.

> Last measured: 2026-06-23.
> Trained on 9,812 pairs from Bible (8 books) and agriculture (8 crop sectors).

| Direction | BLEU (retrieval) | chrF (retrieval) | Top-1 | Top-5 | MRR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Kikuyu → English | 23.36 | 44.16 | 6% | 32% | 0.208 |
| English → Kikuyu | 34.92 | 51.92 | 27% | 50% | 0.398 |


## Quick Start

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/Garnet-Owl/taura-2.0.git
cd taura-2.0
uv sync
```

> **Data & models** are not bundled. Download source files from [Garnet-Owl/taura-datasets](https://huggingface.co/datasets/Garnet-Owl/taura-datasets) on Hugging Face and place them in `data/`. Parallel CSV files are already included in the repo.

```bash
# 1. Prepare dataset
uv run python -m scripts.prepare_dataset

# 2. Train embeddings + alignment
uv run python -m scripts.train_embeddings

# 3. Serve
uv run uvicorn app.serve.main:app --reload
```

Open **[http://localhost:8000](http://localhost:8000)** for the web UI or **[http://localhost:8000/docs](http://localhost:8000/docs)** for the API.


## API

```bash
# Translate
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Mũndũ ũmwe nĩ arakorirũo na thĩna", "source_lang": "ki", "target_lang": "en"}'

# Top-K candidates
curl -X POST http://localhost:8000/translate/candidates \
  -H "Content-Type: application/json" \
  -d '{"text": "the man is reading a book", "source_lang": "en", "target_lang": "ki", "k": 5}'

# Model info
curl http://localhost:8000/model/info
```


## Tests

```bash
uv run pytest
```

78 tests covering unit, integration, and BDD-style parser tests.


## Contributing

Contributions are welcome, especially if you speak Kikuyu, work in low-resource NLP, or want to help expand the corpus. See [AGENTS.md](AGENTS.md) for project standards and [CONTRIBUTING.md](CONTRIBUTING.md) to get started.


## License

MIT. See [LICENSE](LICENSE).
