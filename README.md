# Taura 2.0

> *"Taũra"* is Kikuyu for *"Translate."*

**Taura** is an open-source machine translation engine for **Kikuyu ↔ English**, one of the first of its kind for this low-resource Bantu language. The Kikuyu are Kenya's largest ethnic group, with 9 to 10 million speakers making up roughly 17 to 20% of the country's population.

Modern translation tools largely ignore Kikuyu. Taura exists to change that, starting with strong linguistic foundations: curated parallel corpora, morphological segmentation tuned to Kikuyu's agglutinative structure, and cross-lingual embedding alignment using Orthogonal Procrustes mapping.

![Taura 2.0 Web UI](data/assets/taura-iu-screenshot.png)

## What We're Building

Taura is not just a translation API. It is a full pipeline:

- **Corpus curation:** parallel sentence pairs from the Bible (34 books, one CSV each in `data/parallel/`) and agriculture sector data (coffee, dairy, poultry, potato, banana, mango, cabbage, avocado): over 30,000 curated pairs and growing
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
| 19 | same, + 2 Samuel | 31 books; 2,984 val (Run 18's + 78) | 35.11 / 50.75 | 34.87 / 55.54 | - |
| 20 | same, + Joshua, Judges | 33 books; 3,096 val (Run 19's + Joshua's 58 + Judges' 54) | 31.79 / 47.13 | 35.87 / 55.17 | - |
| 21 | same, + Nehemiah | 34 books; 3,135 val (Run 20's + Nehemiah's 39) | 35.69 / 51.98 | 36.63 / 57.03 | - |
| N3 | Marian opus-mt fine-tuned (77M per direction), fixed epochs (Ki→En 4, En→Ki 7) | Run 17 train; Run 18's 2,906 val | **39.56 / 56.30** | 25.19 / 53.47 | 78 MB each; 0.59 s Ki→En, 1.34 s En→Ki |
| N4 | same, En→Ki only, 12 epochs (Ki→En stays N3) | 32 books; 3,042 val (Run 19's + Joshua's 58) | - | **26.39 / 54.36** | 78 MB; 2.05 s En→Ki (N3: 2.09 s, same 100 sentences) |

N4 vs N3: En→Ki +1.2 BLEU / +0.8 chrF with 12 epochs instead of 7 (both scored on CPU on the same 3,042 verses; on N3's original 2,906 it is 26.26 vs 25.19), at the same speed and size. N4 also had 1,651 more training pairs (2 Kings, 2 Samuel, Joshua), so part of the gain may come from data. The latency sample here has longer sentences than N3's earlier 1.34 s measurement.
Run 21 vs 20: Ki→En +3.9 BLEU, En→Ki +0.8, but Run 20's two retrains differed by 2.6 and 2.4 BLEU (the two Run 21 retrains agree within 0.05 and 0.9), and Run 19 scored 35.11 / 34.87, so the rise is within run-to-run noise and Nehemiah made no clearly measurable change. Run 21 retrains: 35.71 / 51.96 and 35.67 / 52.00 (Ki→En), 37.08 / 56.82 and 36.19 / 57.23 (En→Ki).
Run 20 vs 19: Ki→En -3.3 BLEU, En→Ki +1.0, but the two Run 20 retrains differ by 2.6 (Ki→En: 30.47 and 33.10) and 2.4 (En→Ki: 34.68 and 37.06) BLEU, the validation set gained 112 verses, and the earlier Run 19 pairs ranged 32.4-35.4, so Joshua and Judges made no clearly measurable change.
Run 19 vs 18: Ki→En +3.7 BLEU, En→Ki +0.5, but the two Run 19 retrains differ by 2.2 (Ki→En) and 0.5 (En→Ki) BLEU and the validation set gained 78 verses, so 2 Samuel made no clearly measurable change.
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

### Run the neural translator (recommended, CPU only)

The fine-tuned Marian models are public on Hugging Face: **[Garnet-Owl/taura-marian-kikuyu-english](https://huggingface.co/Garnet-Owl/taura-marian-kikuyu-english)**. You only need the two int8 folders (about 78 MB each); no GPU and no FastText training are required.

```bash
uv sync
uv run --with huggingface_hub hf download Garnet-Owl/taura-marian-kikuyu-english \
  --include "ki_en/ct2-int8/*" --include "en_ki/ct2-int8/*" --local-dir hf-download
rm -rf models/marian-ct2-int8
mkdir -p models/marian-ct2-int8/ki_en models/marian-ct2-int8/en_ki
cp hf-download/ki_en/ct2-int8/* models/marian-ct2-int8/ki_en/
cp hf-download/en_ki/ct2-int8/* models/marian-ct2-int8/en_ki/
uv run uvicorn app.serve.main:app
```

Repeat `--include` once per folder, and download into a folder inside the project (not `/tmp`), which also works on Windows. A startup warning that the FastText models are not found is expected and harmless: only the `neural` method needs the downloaded models.

Each folder must contain `model.bin` directly (check with `ls models/marian-ct2-int8/en_ki`). Open http://localhost:8000: the web UI uses the **Neural** method by default and falls back to Retrieval when the neural models are not installed. Through the API use `"method": "neural"` (see the examples below). English to Kikuyu takes about 2 s per sentence on 4 CPU cores; Kikuyu to English about 0.6 s.

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
