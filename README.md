# Taura 2.0

Machine translation model and API service for translating between Kikuyu and English.

The name "taura" is derived from the Kikuyu word "Taũra", which means "Translate".

---

## Features

- **FastText Word Embeddings:** Monolingual embeddings trained specifically on curated Kikuyu and English sentence datasets.
- **Orthogonal Procrustes Alignment:** Learns a linear translation matrix mapping between Kikuyu and English embedding spaces using parallel anchor points.
- **Dual Translation Modes:**
  - `retrieval`: Finds the closest aligned candidate sentence from a target text corpus using cosine similarity (best for semantic phrase matching).
  - `word-by-word`: Projects each source word to the target space and retrieves the closest target vocabulary item (best for lexical translation).
- **FastAPI Web Service:** Endpoints for real-time bidirectional translation with validation.
- **Robust Verification:** Complete suite of unit and integration tests using BDD-style assertions.

---

## Getting Started

### 1. Prerequisites

- Python 3.12+
- Poetry (for dependency management)

### 2. Installation & Setup

Clone the repository and install the project dependencies:

```bash
git clone https://github.com/Garnet-Owl/taura-2.0.git
cd taura-2.0
poetry install
```

*Note on Windows:* If the poetry installation hangs due to C++ compilation of `fasttext`, verify you are running Python 3.12 and install dependencies via the precompiled wheel:
```bash
poetry run pip install fasttext-wheel numpy pydantic fastapi uvicorn httpx
```

---

## Running the Pipeline

### Step 1: Preprocess the Dataset
Downloads the parallel Kikuyu-English corpus from Hugging Face, cleans the text, and splits it into `train`, `val`, and `test` datasets:

```bash
poetry run python -m scripts.prepare_dataset
```

### Step 2: Train Embeddings and Alignment Matrices
Trains monolingual FastText models and solves the orthogonal Procrustes problem to generate projection matrices:

```bash
poetry run python -m scripts.train_embeddings
```
Training metrics (e.g., top-1/top-5 accuracy and MRR) will be printed and saved to `models/evaluation_metrics.json`.

### Step 3: Start the FastAPI API Service
Run the development server:

```bash
poetry run uvicorn app.serve.main:app --reload
```

---

## API Usage Examples

### Health Check
Check the API server health status:
```bash
curl http://localhost:8000/
```
Response:
```json
{
  "status": "healthy",
  "service": "Taura Kikuyu-English Translation Service"
}
```

### Translate Sentence (Retrieval Method)
Translate a Kikuyu phrase into English using retrieval mode:
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Mũndũ ũmwe nĩ arakorirũo na thĩna", "source_lang": "ki", "target_lang": "en", "method": "retrieval"}'
```

### Translate Sentence (Word-by-Word Method)
Translate an English sentence into Kikuyu using word-by-word lexical translation:
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "the man is reading a book", "source_lang": "en", "target_lang": "ki", "method": "word-by-word"}'
```

---

## Running Tests

Execute the automated test suite containing 18 unit and integration tests:

```bash
poetry run pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
