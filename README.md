# Taura 2.0

> *"Taũra"* is Kikuyu for *"Translate."*

**Taura** is an open-source machine translation engine for **Kikuyu ↔ English**, one of the first of its kind for this low-resource Bantu language. The Kikuyu are Kenya's largest ethnic group, with 9 to 10 million speakers (roughly 17 to 20% of the population), yet mainstream translation tools largely ignore the language.

![Taura 2.0 Web UI](data/assets/taura-iu-screenshot.png)

## What's Inside

- **Corpus:** Kikuyu-English parallel pairs from all 66 books of the Bible (one CSV each in `data/parallel/`) plus agriculture data (coffee, dairy, poultry, potato, banana, mango, cabbage, avocado). About 35,000 pairs, split 80/10/10 (seed 42) into `data/splits/`.
- **FastText + Procrustes:** monolingual embeddings aligned with iterative Orthogonal Procrustes; serves retrieval and word-by-word translation.
- **Neural (recommended):** fine-tuned Marian models, int8, CPU only, about 78 MB per direction.
- **API and web UI:** FastAPI service (`/translate`, `/translate/candidates`, `/model/info`) with a simple UI at `/`.

## Performance

Latest three evaluated runs on the validation split (`data/splits/val.tsv`). Older runs are in `CHANGELOG.md` and git history.

| Run | Model | Validation | Ki→En BLEU / chrF | En→Ki BLEU / chrF | Size, CPU latency |
|---|---|---|---|---|---|
| 34 | FastText + Procrustes, trained on all 66 books; single Kaggle run; the published FastText models were refreshed with a final train+val+test pass of this recipe. Ki→En down 1.3 BLEU, En→Ki up 3.3 BLEU: within the ~3 BLEU retrain noise | 3,510 val | 35.13 / 50.97 | 38.35 / 57.92 | 4.9 GB total (2 x 2.4 GB) |
| N5 | Marian opus-mt fine-tuned (77M), En→Ki 12 epochs (published neural model; Ki→En N3 scored 39.56 / 56.30) | 3,390 val | - | 26.79 / 54.93 | 78 MB each; 1.51 s En→Ki, 0.59 s Ki→En |
| N6 | Marian opus-mt fine-tuned (77M), both directions retrained on all 66 books; **published neural models refreshed** (release pass on train+val+test; scores are from the matching held-out run on train only) | 3,510 val | 41.33 / 57.93 | 26.74 / 54.80 | 78 MB each; 1.02 s Ki→En, 2.39 s En→Ki |

FastText retrieval returns an existing training sentence, so its BLEU is not directly comparable with the neural rows. Single FastText runs vary by about 3 BLEU between retrains, so differences smaller than that are noise. Neural rows use beam 4 on CPU (CTranslate2 int8, 4 vCPU, one sentence at a time).

## Quick Start

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/Garnet-Owl/taura-2.0.git
cd taura-2.0
uv sync
```

> **Data & models** are not bundled. Download source files from [Garnet-Owl/taura-datasets](https://huggingface.co/datasets/Garnet-Owl/taura-datasets) on Hugging Face and place them in `data/`. Parallel CSV files are already included in the repo.

### Train from scratch (optional)

Training runs on a GPU provider (Kaggle), not a laptop.

```bash
# 1. Prepare dataset
uv run python -m scripts.prepare_dataset

# 2. Train embeddings + alignment
uv run python -m scripts.train_embeddings

# 3. Serve
uv run uvicorn app.serve.main:app --reload
```

### Run the server (models auto-download)

Both the fine-tuned Marian models (CPU int8, recommended, ~78 MB per direction) and the FastText + Procrustes models (retrieval, word-by-word; ~2.4 GB each for `ki.bin`/`en.bin`) are public on Hugging Face: **[Garnet-Owl/taura-marian-kikuyu-english](https://huggingface.co/Garnet-Owl/taura-marian-kikuyu-english)**. No manual download is needed.

```bash
uv sync
uv run uvicorn app.serve.main:app
```

On every startup the server checks that Hub repo's latest revision and downloads straight into `models/marian-ct2-int8/` and `models/fasttext-deployed/` — always exactly one copy of each, replacing whatever was there before. If the local copy's revision already matches the Hub's, nothing is re-downloaded (no repeated multi-GB transfers on every restart). If Hugging Face is unreachable, the server logs a warning and serves with whatever is already on disk (or returns 503 for the affected methods if nothing is there yet).

Open http://localhost:8000 for the web UI (it only offers methods whose models are actually loaded) or http://localhost:8000/docs for the API docs. Through the API, `"method"` is one of `"neural"`, `"retrieval"` or `"word-by-word"` (see the API examples below). English to Kikuyu with the neural method takes about 2 s per sentence on 4 CPU cores; Kikuyu to English about 0.6 s.

To pre-fetch models without starting the server (e.g. warming a deploy image), or to force a re-download: `uv run python -m scripts.sync_models [--force]`.

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

# Neural translation (needs the Marian models; see 'Run the neural translator' above)
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "The Lord is my shepherd.", "source_lang": "en", "target_lang": "ki", "method": "neural"}'

# Model info
curl http://localhost:8000/model/info
```

## Tests

```bash
uv run pytest
```

## Contributing

Contributions are welcome, especially if you speak Kikuyu, work in low-resource NLP, or want to help expand the corpus. See [AGENTS.md](AGENTS.md) for project standards and [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## License

MIT. See [LICENSE](LICENSE).
