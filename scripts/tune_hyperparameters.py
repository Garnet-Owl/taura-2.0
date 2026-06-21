"""Script to search for optimal FastText hyperparameters on validation set."""

import numpy as np
import fasttext
from typing import Any, Dict, Tuple
from app.api import config
from app.api.embeddings import (
    get_sentence_embedding,
    learn_alignment_matrix,
    CrossLingualTranslator,
)
from scripts.train_embeddings import load_sentences, evaluate_translator


def tune_model(
    train_ki_path: str,
    train_en_path: str,
    train_tsv_path: str,
    val_tsv_path: str,
    params: Dict[str, Any],
) -> Tuple[float, float]:
    """Trains FastText and returns Kikuyu->English and English->Kikuyu validation Top-1 accuracy."""
    dim = params.get("dim", 100)
    epoch = params.get("epoch", 15)
    lr = params.get("lr", 0.1)
    ws = params.get("ws", 5)
    minCount = params.get("minCount", 1)
    model_type = params.get("model", "skipgram")
    minn = params.get("minn", 3)
    maxn = params.get("maxn", 6)

    # Train temporary models
    ki_model = fasttext.train_unsupervised(
        train_ki_path,
        model=model_type,
        dim=dim,
        epoch=epoch,
        lr=lr,
        ws=ws,
        minCount=minCount,
        minn=minn,
        maxn=maxn,
        thread=4,
    )
    en_model = fasttext.train_unsupervised(
        train_en_path,
        model=model_type,
        dim=dim,
        epoch=epoch,
        lr=lr,
        ws=ws,
        minCount=minCount,
        minn=minn,
        maxn=maxn,
        thread=4,
    )

    # Learn alignment matrices
    train_ki, train_en = load_sentences(train_tsv_path)
    X = np.array([get_sentence_embedding(ki_model, s, dim=dim) for s in train_ki]).T
    Y = np.array([get_sentence_embedding(en_model, s, dim=dim) for s in train_en]).T

    W_ki_en = learn_alignment_matrix(X, Y)
    W_en_ki = learn_alignment_matrix(Y, X)

    # Evaluate
    val_ki, val_en = load_sentences(val_tsv_path)
    translator_ki_en = CrossLingualTranslator(ki_model, en_model, W_ki_en, val_en)
    translator_en_ki = CrossLingualTranslator(en_model, ki_model, W_en_ki, val_ki)

    metrics_ki_en = evaluate_translator(translator_ki_en, val_ki, val_en)
    metrics_en_ki = evaluate_translator(translator_en_ki, val_en, val_ki)

    return metrics_ki_en["accuracy_top1"], metrics_en_ki["accuracy_top1"]


def main() -> None:
    train_ki = config.TRAIN_KI_TXT
    train_en = config.TRAIN_EN_TXT
    train_tsv = config.TRAIN_TSV_PATH
    val_tsv = config.VAL_TSV_PATH

    # Hyperparameter Grid
    grid = []
    for model_type in ["skipgram", "cbow"]:
        for dim in [100, 150]:
            for epoch in [15, 25]:
                for lr in [0.05, 0.1]:
                    for ws in [5, 8]:
                        grid.append(
                            {
                                "model": model_type,
                                "dim": dim,
                                "epoch": epoch,
                                "lr": lr,
                                "ws": ws,
                                "minCount": 1,
                                "minn": 3,
                                "maxn": 6,
                            }
                        )

    print(f"Starting grid search over {len(grid)} configurations...")
    best_ki_en = 0.0
    best_en_ki = 0.0
    best_params = {}

    for idx, params in enumerate(grid):
        print(f"\n[{idx + 1}/{len(grid)}] Evaluating params: {params}")
        try:
            ki_en_acc, en_ki_acc = tune_model(
                train_ki, train_en, train_tsv, val_tsv, params
            )
            avg_acc = (ki_en_acc + en_ki_acc) / 2.0
            print(
                f"Val Accuracy -> ki_en: {ki_en_acc:.4f}, en_ki: {en_ki_acc:.4f}, avg: {avg_acc:.4f}"
            )

            if avg_acc > (best_ki_en + best_en_ki) / 2.0:
                best_ki_en = ki_en_acc
                best_en_ki = en_ki_acc
                best_params = params
                print(f"New best average accuracy: {avg_acc:.4f}!")
        except Exception as e:
            print(f"Error evaluating config: {e}")

    print("\n=== Grid Search Completed ===")
    print(f"Best Configuration: {best_params}")
    print(f"Best Val Accuracy -> ki_en: {best_ki_en:.4f}, en_ki: {best_en_ki:.4f}")


if __name__ == "__main__":
    main()
