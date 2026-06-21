"""
Script to refine cross-lingual alignment matrices using iterative Procrustes.

Loads trained FastText models and existing projection matrices, applies N rounds
of iterative Procrustes refinement to improve Top-1 retrieval accuracy, and
persists the improved matrices alongside updated evaluation metrics.
"""

import json
import csv
import numpy as np
import fasttext

from app.api.embeddings import (
    get_sentence_embedding,
    iterative_procrustes,
    CrossLingualTranslator,
)
from app.api import config
from scripts.train_embeddings import evaluate_translator, save_metrics


N_REFINEMENT_ITERS: int = 5
MAX_EVAL_SENTENCES: int = 1000


def load_sentences(tsv_path: str) -> tuple[list[str], list[str]]:
    """Loads parallel Kikuyu and English sentences from a TSV file."""
    ki_list: list[str] = []
    en_list: list[str] = []
    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ki = row.get("kikuyu")
            en = row.get("english")
            if ki is None or en is None:
                continue
            ki_str = str(ki).strip()
            en_str = str(en).strip()
            if ki_str and en_str:
                ki_list.append(ki_str)
                en_list.append(en_str)
    return ki_list, en_list


def build_anchor_embeddings(
    ki_model: fasttext.FastText._FastText,
    en_model: fasttext.FastText._FastText,
    train_ki: list[str],
    train_en: list[str],
    dim: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Computes anchor embedding matrices from the training parallel sentences."""
    X = np.array([get_sentence_embedding(ki_model, s, dim=dim) for s in train_ki]).T
    Y = np.array([get_sentence_embedding(en_model, s, dim=dim) for s in train_en]).T
    return X, Y


def main() -> None:
    dim = config.EMBEDDING_DIM
    print("Loading trained FastText models...")
    ki_model = fasttext.load_model(config.KI_MODEL_PATH)
    en_model = fasttext.load_model(config.EN_MODEL_PATH)

    print("Loading existing projection matrices...")
    W_ki_en_init = np.load(config.PROJ_KI_EN_PATH)
    W_en_ki_init = np.load(config.PROJ_EN_KI_PATH)

    print("Loading training anchors for refinement...")
    train_ki, train_en = load_sentences(config.TRAIN_TSV_PATH)
    X, Y = build_anchor_embeddings(ki_model, en_model, train_ki, train_en, dim)

    print(f"Running {N_REFINEMENT_ITERS} iterations of Procrustes refinement...")
    W_ki_en = iterative_procrustes(X, Y, W_ki_en_init, n_iters=N_REFINEMENT_ITERS)
    W_en_ki = iterative_procrustes(Y, X, W_en_ki_init, n_iters=N_REFINEMENT_ITERS)

    np.save(config.PROJ_KI_EN_PATH, W_ki_en)
    np.save(config.PROJ_EN_KI_PATH, W_en_ki)
    print("Refined projection matrices saved.")

    print("Re-evaluating alignment quality on validation set...")
    val_ki, val_en = load_sentences(config.VAL_TSV_PATH)
    val_ki = val_ki[:MAX_EVAL_SENTENCES]
    val_en = val_en[:MAX_EVAL_SENTENCES]

    translator_ki_en = CrossLingualTranslator(ki_model, en_model, W_ki_en, val_en)
    translator_en_ki = CrossLingualTranslator(en_model, ki_model, W_en_ki, val_ki)

    metrics_ki_en = evaluate_translator(translator_ki_en, val_ki, val_en)
    metrics_en_ki = evaluate_translator(translator_en_ki, val_en, val_ki)

    metrics = {"kikuyu_to_english": metrics_ki_en, "english_to_kikuyu": metrics_en_ki}
    print("\nRefined Alignment Metrics:")
    print(json.dumps(metrics, indent=2))

    save_metrics(metrics)


if __name__ == "__main__":
    main()
