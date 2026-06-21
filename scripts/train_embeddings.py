"""Script to train monolingual FastText models and learn cross-lingual alignment."""

import os
import json
import csv
import numpy as np
import fasttext

from app.api.embeddings import (
    get_sentence_embedding,
    learn_alignment_matrix,
    CrossLingualTranslator,
)


def load_sentences(tsv_path: str) -> tuple[list[str], list[str]]:
    """Loads parallel Kikuyu and English sentences from a TSV file."""
    ki_list = []
    en_list = []
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


def train_monolingual(
    train_path: str,
    model_path: str,
    dim: int = 150,
    epoch: int = 25,
    lr: float = 0.1,
    ws: int = 8,
) -> fasttext.FastText._FastText:
    """Trains a monolingual FastText skipgram model on raw text."""
    print(f"Training FastText model on {train_path}...")
    model = fasttext.train_unsupervised(
        train_path,
        model="skipgram",
        dim=dim,
        epoch=epoch,
        lr=lr,
        ws=ws,
        minCount=1,
        minn=3,
        maxn=6,
        thread=4,
    )
    model.save_model(model_path)
    print(f"Model saved to {model_path}")
    return model


def evaluate_translator(
    translator: CrossLingualTranslator,
    src_sentences: list[str],
    tgt_sentences: list[str],
) -> dict[str, float]:
    """
    Evaluates translation quality via cross-lingual sentence retrieval.
    Computes Top-1 Accuracy, Top-5 Accuracy, and Mean Reciprocal Rank (MRR).
    """
    correct_top1 = 0
    correct_top5 = 0
    mrr_sum = 0.0
    n = len(src_sentences)

    # Precompute target embeddings
    tgt_embs = translator.tgt_embeddings
    norms_tgt = np.linalg.norm(tgt_embs, axis=1)
    norms_tgt[norms_tgt < 1e-8] = 1.0

    for i, (src_s, true_tgt_s) in enumerate(zip(src_sentences, tgt_sentences)):
        src_emb = get_sentence_embedding(translator.src_model, src_s)
        projected = translator.projection_matrix @ src_emb

        norm_projected = np.linalg.norm(projected)
        if norm_projected < 1e-8:
            # Cannot align, rank is worst
            mrr_sum += 1.0 / n
            continue

        scores = np.dot(tgt_embs, projected) / (norms_tgt * norm_projected)

        # Sort indices by score descending
        sorted_indices = np.argsort(scores)[::-1]

        # Find index of true target sentence
        try:
            rank_idx = list(sorted_indices).index(i)
            rank = rank_idx + 1
        except ValueError:
            rank = n

        if rank == 1:
            correct_top1 += 1
        if rank <= 5:
            correct_top5 += 1
        mrr_sum += 1.0 / rank

    return {
        "accuracy_top1": correct_top1 / n,
        "accuracy_top5": correct_top5 / n,
        "mrr": mrr_sum / n,
    }


def main() -> None:
    os.makedirs("models", exist_ok=True)
    dim = 150

    # 1. Train Monolingual Models
    ki_model = train_monolingual("data/train.kikuyu", "models/ki.bin", dim=dim)
    en_model = train_monolingual("data/train.english", "models/en.bin", dim=dim)

    # 2. Learn Cross-Lingual Alignment
    train_ki, train_en = load_sentences("data/train.tsv")
    print(f"Aligning spaces using {len(train_ki)} parallel sentences as anchors...")

    X = np.array([get_sentence_embedding(ki_model, s, dim=dim) for s in train_ki]).T
    Y = np.array([get_sentence_embedding(en_model, s, dim=dim) for s in train_en]).T

    W_ki_en = learn_alignment_matrix(X, Y)
    W_en_ki = learn_alignment_matrix(Y, X)

    np.save("models/proj_ki_en.npy", W_ki_en)
    np.save("models/proj_en_ki.npy", W_en_ki)
    print("Alignment projection matrices saved.")

    # 3. Evaluate on Validation Set
    val_ki, val_en = load_sentences("data/val.tsv")
    print(f"Evaluating alignment on {len(val_ki)} validation sentences...")

    translator_ki_en = CrossLingualTranslator(ki_model, en_model, W_ki_en, val_en)
    translator_en_ki = CrossLingualTranslator(en_model, ki_model, W_en_ki, val_ki)

    metrics_ki_en = evaluate_translator(translator_ki_en, val_ki, val_en)
    metrics_en_ki = evaluate_translator(translator_en_ki, val_en, val_ki)

    metrics = {"kikuyu_to_english": metrics_ki_en, "english_to_kikuyu": metrics_en_ki}

    print("\nEvaluation Metrics:")
    print(json.dumps(metrics, indent=2))

    metrics_path = "models/evaluation_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved evaluation metrics to {metrics_path}")


if __name__ == "__main__":
    main()
