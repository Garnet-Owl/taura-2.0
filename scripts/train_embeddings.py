"""Script to train monolingual FastText models and learn cross-lingual alignment."""

import os
import json
import csv
import numpy as np
import fasttext

from app.api.embeddings import (
    get_sentence_embedding,
    learn_alignment_matrix,
    iterative_procrustes,
    CrossLingualTranslator,
)
from app.api import config


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
    train_path: str, model_path: str, dim: int = 150
) -> fasttext.FastText._FastText:
    """Trains a monolingual FastText skipgram model on raw text."""
    print(f"Training FastText model on {train_path}...")
    model = fasttext.train_unsupervised(
        train_path,
        model=config.FASTTEXT_MODEL_TYPE,
        dim=dim,
        epoch=config.FASTTEXT_EPOCH,
        lr=config.FASTTEXT_LR,
        ws=config.FASTTEXT_WS,
        minCount=config.FASTTEXT_MIN_COUNT,
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


def save_metrics(
    metrics: dict[str, dict[str, float]], metrics_path: str = config.METRICS_JSON_PATH
) -> None:
    """Saves metrics, merging with existing data to preserve offline evaluation scores."""
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                existing_metrics = json.load(f)

            for lang_pair in ["kikuyu_to_english", "english_to_kikuyu"]:
                if lang_pair not in existing_metrics:
                    existing_metrics[lang_pair] = {}
                existing_metrics[lang_pair].update(metrics.get(lang_pair, {}))

            metrics = existing_metrics
        except (json.JSONDecodeError, OSError):
            pass

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved evaluation metrics to {metrics_path}")


def main() -> None:
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    dim = config.EMBEDDING_DIM

    train_ki_path = config.TRAIN_KI_TXT
    train_en_path = config.TRAIN_EN_TXT

    tokenizer = None
    if os.path.exists(config.SP_MODEL_PATH):
        print("SentencePiece model found. Tokenizing training corpora...")
        from app.api.preprocessing import SubwordTokenizer
        tokenizer = SubwordTokenizer(config.SP_MODEL_PATH)
        
        sp_ki_path = train_ki_path + ".sp"
        sp_en_path = train_en_path + ".sp"
        
        for in_path, out_path in [(train_ki_path, sp_ki_path), (train_en_path, sp_en_path)]:
            print(f"Applying SentencePiece to {in_path} -> {out_path}")
            with open(in_path, "r", encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8") as fout:
                for line in fin:
                    pieces = tokenizer.encode(line.strip())
                    fout.write(" ".join(pieces) + "\n")
                    
        train_ki_path = sp_ki_path
        train_en_path = sp_en_path
    else:
        print("WARNING: SentencePiece model not found. Falling back to raw text for FastText training.")

    # 1. Train Monolingual Models
    ki_model = train_monolingual(train_ki_path, config.KI_MODEL_PATH, dim=dim)
    en_model = train_monolingual(train_en_path, config.EN_MODEL_PATH, dim=dim)

    # 2. Learn Cross-Lingual Alignment (SVD + iterative Procrustes refinement)
    train_ki, train_en = load_sentences(config.TRAIN_TSV_PATH)
    print(f"Aligning spaces using {len(train_ki)} parallel sentences as anchors...")

    if tokenizer:
        train_ki = [" ".join(tokenizer.encode(s)) for s in train_ki]
        train_en = [" ".join(tokenizer.encode(s)) for s in train_en]

    X = np.array([get_sentence_embedding(ki_model, s, dim=dim) for s in train_ki]).T
    Y = np.array([get_sentence_embedding(en_model, s, dim=dim) for s in train_en]).T

    W_ki_en_init = learn_alignment_matrix(X, Y)
    W_en_ki_init = learn_alignment_matrix(Y, X)

    W_ki_en = iterative_procrustes(
        X, Y, W_ki_en_init, n_iters=config.ALIGNMENT_REFINEMENT_ITERS
    )
    W_en_ki = iterative_procrustes(
        Y, X, W_en_ki_init, n_iters=config.ALIGNMENT_REFINEMENT_ITERS
    )

    np.save(config.PROJ_KI_EN_PATH, W_ki_en)
    np.save(config.PROJ_EN_KI_PATH, W_en_ki)
    print("Alignment projection matrices saved.")

    # 3. Evaluate on Validation Set
    val_ki, val_en = load_sentences(config.VAL_TSV_PATH)
    # Limit evaluation to 1000 sentences to avoid O(N^2) hang
    val_ki = val_ki[:1000]
    val_en = val_en[:1000]
    print(f"Evaluating alignment on {len(val_ki)} validation sentences...")

    if tokenizer:
        val_ki_sp = [" ".join(tokenizer.encode(s)) for s in val_ki]
        val_en_sp = [" ".join(tokenizer.encode(s)) for s in val_en]
        translator_ki_en = CrossLingualTranslator(ki_model, en_model, W_ki_en, val_en_sp)
        translator_en_ki = CrossLingualTranslator(en_model, ki_model, W_en_ki, val_ki_sp)
        metrics_ki_en = evaluate_translator(translator_ki_en, val_ki_sp, val_en_sp)
        metrics_en_ki = evaluate_translator(translator_en_ki, val_en_sp, val_ki_sp)
    else:
        translator_ki_en = CrossLingualTranslator(ki_model, en_model, W_ki_en, val_en)
        translator_en_ki = CrossLingualTranslator(en_model, ki_model, W_en_ki, val_ki)
        metrics_ki_en = evaluate_translator(translator_ki_en, val_ki, val_en)
        metrics_en_ki = evaluate_translator(translator_en_ki, val_en, val_ki)

    metrics = {"kikuyu_to_english": metrics_ki_en, "english_to_kikuyu": metrics_en_ki}

    print("\nEvaluation Metrics:")
    print(json.dumps(metrics, indent=2))

    save_metrics(metrics)


if __name__ == "__main__":
    main()
