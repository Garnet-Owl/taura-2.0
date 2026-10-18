# Taura 2.0

> *"Taũra"* is Kikuyu for *"Translate."*

**Taura** is an open-source machine translation engine for **Kikuyu ↔ English**, one of the first of its kind for this low-resource Bantu language. The Kikuyu are Kenya's largest ethnic group, with 9 to 10 million speakers making up roughly 17 to 20% of the country's population.

Modern translation tools largely ignore Kikuyu. Taura exists to change that, starting with strong linguistic foundations: curated parallel corpora, morphological segmentation tuned to Kikuyu's agglutinative structure, and cross-lingual embedding alignment using Orthogonal Procrustes mapping.

![Taura 2.0 Web UI](data/assets/taura-iu-screenshot.png)

## What We're Building

Taura is not just a translation API. It is a full pipeline:

- **Corpus curation:** parallel sentence pairs from the Bible (30 books, one CSV each in `data/parallel/`) and agriculture sector data (coffee, dairy, poultry, potato, banana, mango, cabbage, avocado): over 28,000 curated pairs and growing
- **Cross-lingual alignment:** monolingual FastText embeddings aligned via iterative Orthogonal Procrustes with three anchor sources (parallel sentence embeddings, seed dictionary, and identical-string vocabulary pairs) and CSLS-based refinement
- **Translation API:** FastAPI service with retrieval and word-by-word modes, top-K candidates, a CPU neural mode (fine-tuned Marian), and a lightweight web UI

The long-term goal is to push translation quality to the point where Taura is genuinely useful to Kikuyu speakers, and to serve as a replicable blueprint for other low-resource African languages.

## Performance Progression

Starting point and the latest runs only; older runs are in `CHANGELOG.md` and git history.
FastText rows are mean of 2 retrains, scored on the validation split (`data/splits/val.tsv`, seeded hash 80/10/10).
Neural rows generate translations (beam 4) and are timed on CPU (CTranslate2 int8, 4 vCPU, one sentence at a time).

| Run | Model | Data / validation | Ki→En BLEU / chrF | En→Ki BLEU / chrF | Size, CPU latency |
|---|---|---|---|---|---|
| 1 (start) | FastText + simple Procrustes | old 100-verse set | 5.34 / - | 4.91 / - | - |
| 17 | FastText + hybrid Procrustes (retrieval) | 29 books; 2,836 val | 33.01 / 49.22 | 34.67 / 54.82 | - |
| 18 | same, + 2 Kings | 30 books; 2,906 val (Run 17's + 70) | 31.42 / 47.43 | 34.33 / 54.48 | - |
| N2 | Marian opus-mt fine-tuned (77M per direction) | Run 16 split; 2,723 val | 39.21 / 55.67 | 22.13 / 50.45 | 78 MB each; 0.86 s Ki→En, 2.2 s En→Ki |
| N3 | same, fixed epochs (Ki→En 4, En→Ki 7) | Run 17 train; Run 18's 2,906 val | **39.56 / 56.30** | **25.19 / 53.47** | 78 MB each; 0.59 s Ki→En, 1.34 s En→Ki |

N3 vs N2: En→Ki +3 BLEU from training it for 7 full epochs instead of a time cap (validation sets differ slightly; no overlap with training).
Run 18 vs 17: both directions within Run 17's 3.8 BLEU run-to-run spread, so 2 Kings made no measurable change.
FastText retrieval picks an existing validation sentence, so its BLEU is not directly comparable with the neural rows.

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

# Neural translation (needs the Marian models from Hugging Face in models/marian-ct2-int8/{ki_en,en_ki})
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
