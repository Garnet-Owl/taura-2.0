"""FastAPI application for Kikuyu-English bidirectional translation."""

import os
import csv
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import numpy as np
import fasttext
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.api.embeddings import CrossLingualTranslator


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Source text to translate")
    source_lang: str = Field(..., description="Source language code ('ki' or 'en')")
    target_lang: str = Field(..., description="Target language code ('ki' or 'en')")
    method: str = Field(
        "retrieval", description="Translation method ('retrieval' or 'word-by-word')"
    )


class TranslationResponse(BaseModel):
    translated_text: str = Field(..., description="Translated text")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    method: str = Field(..., description="Translation method used")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Paths to model files
    ki_model_path = "models/ki.bin"
    en_model_path = "models/en.bin"
    proj_ki_en_path = "models/proj_ki_en.npy"
    proj_en_ki_path = "models/proj_en_ki.npy"
    train_tsv_path = "data/train.tsv"

    # Check if models exist
    if not (
        os.path.exists(ki_model_path)
        and os.path.exists(en_model_path)
        and os.path.exists(proj_ki_en_path)
        and os.path.exists(proj_en_ki_path)
    ):
        app.state.translators = None
    else:
        # Load FastText models
        ki_model = fasttext.load_model(ki_model_path)
        en_model = fasttext.load_model(en_model_path)

        # Load alignment projection matrices
        W_ki_en = np.load(proj_ki_en_path)
        W_en_ki = np.load(proj_en_ki_path)

        # Load parallel sentences for retrieval fallback/dictionary
        ki_sentences = []
        en_sentences = []
        if os.path.exists(train_tsv_path):
            with open(train_tsv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    ki = row.get("kikuyu")
                    en = row.get("english")
                    if ki and en:
                        ki_sentences.append(str(ki).strip())
                        en_sentences.append(str(en).strip())

        # Initialize translators
        app.state.translators = {
            "ki_en": CrossLingualTranslator(ki_model, en_model, W_ki_en, en_sentences),
            "en_ki": CrossLingualTranslator(en_model, ki_model, W_en_ki, ki_sentences),
        }

    yield


app = FastAPI(
    title="Taura 2.0 Kikuyu-English Translation API",
    description="Cross-lingual embedding-based machine translation for Kikuyu and English.",
    version="2.0.0",
    lifespan=lifespan,
)


# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/serve/static"), name="static")
templates = Jinja2Templates(directory="app/serve/templates")


class FeedbackRequest(BaseModel):
    source_text: str = Field(..., min_length=1)
    target_text: str = Field(..., min_length=1)
    source_lang: str = Field(..., min_length=2, max_length=2)
    target_lang: str = Field(..., min_length=2, max_length=2)
    method: str = Field(...)
    rating: int = Field(..., description="1 for helpful, -1 for unhelpful")
    comment: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request) -> HTMLResponse:
    """Serves the translation web UI."""
    return templates.TemplateResponse(request=request, name="index.html")  # type: ignore[return-value]


@app.get("/health")
def read_health() -> dict[str, str]:
    """Health-check endpoint."""
    return {"status": "healthy", "service": "Taura Kikuyu-English Translation Service"}


@app.post("/feedback")
def submit_feedback(request: FeedbackRequest) -> dict[str, str]:
    """Appends user translation feedback to data/feedback.jsonl."""
    feedback_dir = "data"
    os.makedirs(feedback_dir, exist_ok=True)
    feedback_file = os.path.join(feedback_dir, "feedback.jsonl")

    feedback_entry = request.model_dump()
    with open(feedback_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_entry, ensure_ascii=False) + "\n")

    return {"status": "success", "message": "Feedback submitted successfully."}



@app.post("/translate", response_model=TranslationResponse)
def translate(request: TranslationRequest) -> TranslationResponse:
    """Performs bidirectional translation (Kikuyu <-> English)."""
    # 1. Validation
    src = request.source_lang.strip().lower()
    tgt = request.target_lang.strip().lower()
    method = request.method.strip().lower()

    if src not in ("ki", "en") or tgt not in ("ki", "en"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported language codes are 'ki' (Kikuyu) and 'en' (English).",
        )

    if src == tgt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and target languages must be different.",
        )

    if method not in ("retrieval", "word-by-word"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported translation methods are 'retrieval' and 'word-by-word'.",
        )

    # 2. Check if translators are initialized
    if not hasattr(app.state, "translators") or app.state.translators is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Translation models are not loaded. Please run model training first.",
        )

    # 3. Perform translation
    key = f"{src}_{tgt}"
    translator = app.state.translators.get(key)
    if not translator:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translator for {src} to {tgt} is not loaded.",
        )

    if method == "retrieval":
        translated_text = translator.translate_sentence_retrieval(request.text)
    else:
        translated_text = translator.translate_word_by_word(request.text)

    return TranslationResponse(
        translated_text=translated_text,
        source_lang=src,
        target_lang=tgt,
        method=method,
    )
