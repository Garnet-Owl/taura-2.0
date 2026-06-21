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

from app.api.embeddings import CrossLingualTranslator, get_sentence_embedding
from app.api import config

APP_VERSION = "2.0.0"


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


class CandidatesRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Source text to translate")
    source_lang: str = Field(..., description="Source language code ('ki' or 'en')")
    target_lang: str = Field(..., description="Target language code ('ki' or 'en')")
    k: int = Field(5, ge=1, le=20, description="Number of top-K candidates to return")


class TranslationCandidate(BaseModel):
    text: str = Field(..., description="Candidate translation text")
    score: float = Field(..., description="Cosine similarity score")


class CandidatesResponse(BaseModel):
    candidates: list[TranslationCandidate] = Field(..., description="Top-K candidates")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")


class ModelInfoResponse(BaseModel):
    version: str = Field(..., description="API/model version")
    embedding_dim: int = Field(..., description="FastText embedding dimension")
    model_type: str = Field(..., description="FastText model type (skipgram/cbow)")
    epochs: int = Field(..., description="Training epochs")
    window_size: int = Field(..., description="Context window size")
    min_count: int = Field(..., description="Minimum word count threshold")
    metrics: dict = Field(default_factory=dict, description="Evaluation metrics")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Paths to model files
    ki_model_path = config.KI_MODEL_PATH
    en_model_path = config.EN_MODEL_PATH
    proj_ki_en_path = config.PROJ_KI_EN_PATH
    proj_en_ki_path = config.PROJ_EN_KI_PATH
    train_tsv_path = config.TRAIN_TSV_PATH

    tgt_embs_ki_path = config.TGT_EMBS_KI_PATH
    tgt_embs_en_path = config.TGT_EMBS_EN_PATH

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

        # Load precomputed target embeddings
        tgt_embs_ki = np.load(tgt_embs_ki_path) if os.path.exists(tgt_embs_ki_path) else None
        tgt_embs_en = np.load(tgt_embs_en_path) if os.path.exists(tgt_embs_en_path) else None

        # Initialize translators
        app.state.translators = {
            "ki_en": CrossLingualTranslator(ki_model, en_model, W_ki_en, en_sentences, precomputed_tgt_embeddings=tgt_embs_en),
            "en_ki": CrossLingualTranslator(en_model, ki_model, W_en_ki, ki_sentences, precomputed_tgt_embeddings=tgt_embs_ki),
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
    feedback_dir = os.path.dirname(config.FEEDBACK_FILE_PATH)
    os.makedirs(feedback_dir, exist_ok=True)
    feedback_file = config.FEEDBACK_FILE_PATH

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


@app.post("/translate/candidates", response_model=CandidatesResponse)
def translate_candidates(request: CandidatesRequest) -> CandidatesResponse:
    """Returns top-K candidate translations ranked by cosine similarity."""
    src = request.source_lang.strip().lower()
    tgt = request.target_lang.strip().lower()

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

    if not hasattr(app.state, "translators") or app.state.translators is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Translation models are not loaded. Please run model training first.",
        )

    key = f"{src}_{tgt}"
    translator = app.state.translators.get(key)
    if not translator:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translator for {src} to {tgt} is not loaded.",
        )

    candidates = _retrieve_top_k(translator, request.text, request.k)
    return CandidatesResponse(
        candidates=candidates,
        source_lang=src,
        target_lang=tgt,
    )


def _retrieve_top_k(
    translator: CrossLingualTranslator, src_sentence: str, k: int
) -> list[TranslationCandidate]:
    """Computes cosine similarity scores and returns the top-K target candidates."""
    if not translator.tgt_sentences:
        return []

    src_emb = get_sentence_embedding(translator.src_model, src_sentence)
    projected = translator.projection_matrix @ src_emb

    norm_projected = np.linalg.norm(projected)
    if norm_projected < 1e-8:
        return [TranslationCandidate(text=translator.tgt_sentences[0], score=0.0)]

    norms_tgt = np.linalg.norm(translator.tgt_embeddings, axis=1)
    norms_tgt[norms_tgt < 1e-8] = 1.0

    scores = np.dot(translator.tgt_embeddings, projected) / (norms_tgt * norm_projected)
    top_k_indices = np.argsort(scores)[::-1][: min(k, len(translator.tgt_sentences))]

    return [
        TranslationCandidate(
            text=translator.tgt_sentences[int(idx)],
            score=float(scores[int(idx)]),
        )
        for idx in top_k_indices
    ]


@app.get("/model/info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    """Returns model version, hyperparameters, and current evaluation metrics."""
    metrics: dict = {}
    if os.path.exists(config.METRICS_JSON_PATH):
        try:
            with open(config.METRICS_JSON_PATH, "r", encoding="utf-8") as f:
                metrics = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    return ModelInfoResponse(
        version=APP_VERSION,
        embedding_dim=config.EMBEDDING_DIM,
        model_type=config.FASTTEXT_MODEL_TYPE,
        epochs=config.FASTTEXT_EPOCH,
        window_size=config.FASTTEXT_WS,
        min_count=config.FASTTEXT_MIN_COUNT,
        metrics=metrics,
    )
