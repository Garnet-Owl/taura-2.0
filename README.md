# Taura 2.0

> *"Taũra"* is Kikuyu for *"Translate."*

**Taura** is an open-source machine translation engine for **Kikuyu ↔ English**, one of the first of its kind for this low-resource Bantu language. The Kikuyu are Kenya's largest ethnic group, with 9 to 10 million speakers making up roughly 17 to 20% of the country's population.

Modern translation tools largely ignore Kikuyu. Taura exists to change that, starting with strong linguistic foundations: curated parallel corpora, morphological segmentation tuned to Kikuyu's agglutinative structure, and cross-lingual embedding alignment using Orthogonal Procrustes mapping.

![Taura 2.0 Web UI](data/assets/taura-iu-screenshot.png)


## What We're Building

Taura is not just a translation API. It is a full pipeline:

- **Corpus curation:** parallel sentence pairs from the Bible (Matthew, Mark, Luke, John, Acts, Romans, 1–2 Corinthians) and agriculture sector data (coffee, dairy, poultry, potato, banana, mango, cabbage, avocado) — over 9,700 curated pairs and growing
- **Cross-lingual alignment:** monolingual FastText embeddings aligned via iterative Orthogonal Procrustes with three anchor sources (parallel sentence embeddings, seed dictionary, and identical-string vocabulary pairs) and CSLS-based refinement
- **Translation API:** FastAPI service with retrieval and word-by-word modes, top-K candidates, and a lightweight web UI

The long-term goal is to push translation quality to the point where Taura is genuinely useful to Kikuyu speakers, and to serve as a replicable blueprint for other low-resource African languages.


## Performance Progression

> This section tracks the evolution of Taura's cross-lingual alignment. Every row represents a real training run, evaluated on a 100-sentence held-out validation set.

> [!NOTE]
> **Metrics Key:**
> - **BLEU / chrF:** Measures translation similarity to a human reference. Higher is better.
> - **Top-1 / Top-5:** The percentage of times the exact correct translation was in the #1 or Top 5 retrieved results.
> - **MRR (Mean Reciprocal Rank):** How close the correct translation was to rank #1 on average.
> - **MNN (Mutual Nearest Neighbors):** The number of Kikuyu and English vocabulary words that perfectly aligned. Higher means a better vocabulary bridge.

| Run | Direction | BLEU | chrF | Top-1 | Top-5 | MRR | MNN |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Baseline**<br>Raw FastText + simple Procrustes | Ki→En<br>En→Ki | 5.34<br>4.91 | —<br>— | —<br>— | —<br>— | —<br>— | — |
| **2. Hybrid alignment**<br>Sentence anchors + seed dict + identical strings; iterative Procrustes with MNN+CSLS | Ki→En<br>En→Ki | 21.00<br>35.09 | —<br>— | —<br>— | —<br>— | —<br>— | 3,007 |
| **3. Agriculture + Proper-Nouns**<br>+3,852 agri pairs; proper-noun anchors; restored default n-grams | Ki→En<br>En→Ki | 23.36<br>34.92 | 44.16<br>51.92 | 6%<br>27% | 32%<br>50% | 0.208<br>0.398 | 4,788 |
| **4. Expanded Bible Corpus**<br>+Galatians, Ephesians, Philippians, Colossians, 1 Thess (10,255 pairs) | Ki→En<br>En→Ki | 35.27<br>34.38 | 49.10<br>55.18 | 20%<br>22% | 38%<br>41% | 0.305<br>0.320 | 4,859 |
| **5. Psalms Expansion**<br>+Psalms (12,716 pairs total) | Ki→En<br>En→Ki | 33.18<br>35.96 | 49.02<br>56.75 | 25%<br>22% | 44%<br>46% | 0.345<br>0.342 | 5,654 |
| **6. Genesis, Proverbs, Ecclesiastes**<br>+2,630 pairs (15,346 pairs total) | Ki→En<br>En→Ki | 34.04<br>37.22 | 48.59<br>55.15 | 18%<br>24% | 34%<br>51% | 0.275<br>0.360 | 6,521 |

The hybrid alignment was the single biggest jump — a **4× BLEU improvement** from baseline.
The recent expansion of the Bible corpus significantly balanced the model, driving Kikuyu→English BLEU up by +12 points and pushing Mutual Nearest Neighbors to 4,859.

**What drove the 5 → 21 BLEU jump:**
Three alignment anchor sources were combined — parallel sentence embeddings, a seed dictionary, and identical-string vocabulary pairs — giving the Procrustes solver a much richer and more diverse set of constraints. Iterative refinement with Mutual Nearest Neighbors and CSLS de-hubbing then pushed the MNN count from near-zero to 3,007, meaning 3,007 Kikuyu vocabulary words found their correct English counterpart through the learned projection.

**What the literature says for similar low-resource Bantu scenarios:**
- Supervised cross-lingual alignment (what we do) consistently outperforms unsupervised methods when at least 1–5k parallel pairs are available [(Conneau et al., MUSE)](https://github.com/facebookresearch/MUSE)
- Cross-lingual transfer from related high-resource languages (e.g. Swahili → Kikuyu) can add 1.5–3.5 BLEU in low-resource Bantu pairs [(Congolese Swahili study)](https://arxiv.org/pdf/2103.10734)
- Chain-of-languages multilingual anchors (English → Swahili → Kikuyu) have shown promise for zero-resource directions [(multilingual anchor chains)](https://arxiv.org/pdf/2311.12489)


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
