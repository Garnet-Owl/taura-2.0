"""Script to verify monolingual and cross-lingual semantic nearest neighbors of key Named Entities."""

import sys
import os
import numpy as np
import fasttext
from app.api import config
from app.api.embeddings import compute_csls_penalty

_TGT_CACHE = {}


def get_cross_lingual_neighbors(
    word: str,
    src_model,
    tgt_model,
    proj_matrix: np.ndarray,
    k: int = 5,
    use_csls: bool = True,
) -> list[tuple[str, float]]:
    """Finds cross-lingual nearest neighbors of a source word in target space."""
    v_src = src_model.get_word_vector(word)
    norm_src = np.linalg.norm(v_src)
    if norm_src < 1e-8:
        return []

    projected = proj_matrix @ v_src
    norm_proj = np.linalg.norm(projected)
    if norm_proj < 1e-8:
        return []

    model_id = id(tgt_model)
    if model_id not in _TGT_CACHE:
        print(
            f"Precomputing/caching vocabulary embeddings for target model {model_id}..."
        )
        tgt_words = tgt_model.get_words()[:50000]  # Cap vocabulary to speed up search
        tgt_embs = np.array([tgt_model.get_word_vector(w) for w in tgt_words])
        tgt_norms = np.linalg.norm(tgt_embs, axis=1)
        tgt_norms[tgt_norms < 1e-8] = 1.0

        if use_csls:
            penalty = compute_csls_penalty(tgt_embs, tgt_embs, k=10)
        else:
            penalty = np.zeros(len(tgt_words))

        _TGT_CACHE[model_id] = (tgt_words, tgt_embs, tgt_norms, penalty)

    tgt_words, tgt_embs, tgt_norms, penalty = _TGT_CACHE[model_id]

    # Cosine similarity
    scores = np.dot(tgt_embs, projected) / (tgt_norms * norm_proj)

    if use_csls:
        scores = 2 * scores - penalty

    best_idx = np.argsort(scores)[::-1][:k]
    return [(tgt_words[idx], float(scores[idx])) for idx in best_idx]


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-dir",
        type=str,
        default=config.LATEST_RUN_DIR,
        help="Run directory to evaluate",
    )
    args = parser.parse_args()

    run_dir = args.run_dir
    ki_model_path = os.path.join(run_dir, "ki.bin")
    en_model_path = os.path.join(run_dir, "en.bin")
    proj_ki_en_path = os.path.join(run_dir, "proj_ki_en.npy")
    proj_en_ki_path = os.path.join(run_dir, "proj_en_ki.npy")

    # Ensure models exist
    if not os.path.exists(ki_model_path) or not os.path.exists(en_model_path):
        print(
            f"Models not found at {ki_model_path} or {en_model_path}. Please train/resume first."
        )
        return

    print(f"Loading models from {run_dir}...")
    ki_model = fasttext.load_model(ki_model_path)
    en_model = fasttext.load_model(en_model_path)

    W_ki_en = np.load(proj_ki_en_path)
    W_en_ki = np.load(proj_en_ki_path)

    # Named Entity Test Words
    test_ki_words = ["ngai", "yesu", "kristũ", "mũndũ", "yerusalemu", "israeli"]
    test_en_words = ["god", "jesus", "christ", "man", "jerusalem", "israel"]

    print("\n=========================================")
    print("1. Monolingual Nearest Neighbors (Kikuyu)")
    print("=========================================")
    for word in test_ki_words:
        nn = ki_model.get_nearest_neighbors(word, k=5)
        print(f"\nNearest to Kikuyu '{word}':")
        for score, w in nn:
            print(f"  - {w} (score: {score:.4f})")

    print("\n=========================================")
    print("2. Cross-Lingual Nearest Neighbors (Kikuyu -> English)")
    print("=========================================")
    for word in test_ki_words:
        nn = get_cross_lingual_neighbors(word, ki_model, en_model, W_ki_en, k=5)
        print(f"\nNearest English words to Kikuyu '{word}':")
        for w, score in nn:
            print(f"  - {w} (score: {score:.4f})")

    print("\n=========================================")
    print("3. Cross-Lingual Nearest Neighbors (English -> Kikuyu)")
    print("=========================================")
    for word in test_en_words:
        nn = get_cross_lingual_neighbors(word, en_model, ki_model, W_en_ki, k=5)
        print(f"\nNearest Kikuyu words to English '{word}':")
        for w, score in nn:
            print(f"  - {w} (score: {score:.4f})")


if __name__ == "__main__":
    main()
