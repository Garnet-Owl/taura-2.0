# Design Spec: Phase 2 Evaluation Pipeline & Web UI

This document specifies the architecture, components, and data flow for Phase 2 of the Taura 2.0 machine translation project.

## Goals

1. **Standard Evaluation Pipeline:** Compute corpus-level BLEU and ChrF scores using `sacrebleu` on the `data/test.tsv` split to baseline translation quality.
2. **Web User Interface:** Develop a simple, sleek Single-Page Application (SPA) using FastAPI (Jinja2 templates + Vanilla CSS/JS) for real-time translation, alignment visualization, and user feedback submission.

---

## 1. Offline Evaluation Pipeline

We will create a script `scripts/evaluate.py` to evaluate translation performance:

### Data Loading & Processing
- Load `data/test.tsv` which contains Kikuyu and English sentence pairs.
- Extract source sentences and reference target sentences.

### Metrics & Libraries
- We will install `sacrebleu` to compute standard MT corpus-level metrics:
  - `sacrebleu.corpus_bleu`
  - `sacrebleu.corpus_chrf`
- We will run evaluation for both directions:
  - `ki` -> `en` (using `retrieval` and `word-by-word` modes)
  - `en` -> `ki` (using `retrieval` and `word-by-word` modes)

### Outputs
- Print a markdown-formatted table of results to the terminal.
- Update `models/evaluation_metrics.json` with the new metrics under keys `bleu` and `chrf` without destroying the existing word-level metrics.

---

## 2. Web User Interface & API Routes

### Directory Structure Updates
- `app/serve/templates/index.html`: Main HTML template.
- `app/serve/static/style.css`: Clean, modern glassmorphic styling.
- `app/serve/static/main.js`: Fetch operations, language swap, word alignment visualization.

### FastAPI Integration
1. **Static Files & Templates:** Mount static assets and Jinja2 templates:
   ```python
   from fastapi.staticfiles import StaticFiles
   from fastapi.templating import Jinja2Templates

   app.mount("/static", StaticFiles(directory="app/serve/static"), name="static")
   templates = Jinja2Templates(directory="app/serve/templates")
   ```
2. **Frontend UI Route:** Map `/` to render `index.html`.
3. **Feedback Endpoint:** Define a `POST /feedback` endpoint that accepts:
   ```python
   class FeedbackRequest(BaseModel):
       source_text: str
       target_text: str
       source_lang: str
       target_lang: str
       method: str
       rating: int  # 1 for thumb-up, -1 for thumb-down
       comment: Optional[str] = None
   ```
   Append incoming feedback to `data/feedback.jsonl` as JSON lines.

### Frontend User Experience (UX)
- **Visual Design:** Sleek dark background with semi-transparent glassmorphic cards, vibrant neon accent colors (e.g., violet/cyan gradients), and clean typography.
- **Language Swapping:** Quick click toggle to swap source and target languages.
- **Word Alignment Visualizer:** For `word-by-word` translations, display word-level mappings underneath the translation box with confidence values based on cosine similarity scores.
- **Feedback Collection:** Embedded Thumbs-up/down icons and feedback text field.

---

## 3. Testing & Verification

- **Unit Tests:** Add tests verifying:
  - Evaluation functions run without errors.
  - `/feedback` endpoint correctly validates inputs and appends to `data/feedback.jsonl`.
  - Static file mounting and home route rendering.
- **Manual Verification:** Build, format, run, and manually translate via browser.
