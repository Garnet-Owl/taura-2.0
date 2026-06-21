"""Script to train monolingual FastText models and learn cross-lingual alignment."""

import os
import json
import csv
import numpy as np
import fasttext
import datetime
import gc
import multiprocessing
import sentencepiece

from app.api.embeddings import (
    get_sentence_embedding,
    get_sentence_embeddings_parallel,
    learn_alignment_matrix,
    iterative_procrustes,
    CrossLingualTranslator,
    extract_identical_string_dictionary,
)
from app.api import config
from app.shared.logger import setup_logger

logger = setup_logger(__name__)

import argparse





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
    if os.path.exists(model_path):
        logger.info(f"Model already exists at {model_path}. Resuming and loading it.")
        return fasttext.load_model(model_path)
        
    logger.info(f"Training FastText model on {train_path}...")
    model = fasttext.train_unsupervised(
        train_path,
        model=config.FASTTEXT_MODEL_TYPE,
        dim=dim,
        epoch=config.FASTTEXT_EPOCH,
        lr=config.FASTTEXT_LR,
        ws=config.FASTTEXT_WS,
        minCount=config.FASTTEXT_MIN_COUNT,
        thread=max(1, multiprocessing.cpu_count()),
    )
    model.save_model(model_path)
    logger.info(f"Model saved to {model_path}")
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
    logger.info(f"Saved evaluation metrics to {metrics_path}")


def setup_and_get_state() -> tuple[dict, str]:
    latest_run = config.LATEST_RUN_DIR
    state_file = os.path.join(latest_run, "training_state.json")
    
    is_completed = False
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                if state.get("status") == "completed":
                    is_completed = True
        except Exception:
            pass
            
    if is_completed or latest_run == config.MODELS_DIR:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_run = os.path.join(config.MODELS_DIR, f"run_{timestamp}")
        os.makedirs(new_run, exist_ok=True)
        config.LATEST_RUN_DIR = new_run
        config.KI_MODEL_PATH = os.path.join(new_run, "ki.bin")
        config.EN_MODEL_PATH = os.path.join(new_run, "en.bin")
        config.PROJ_KI_EN_PATH = os.path.join(new_run, "proj_ki_en.npy")
        config.PROJ_EN_KI_PATH = os.path.join(new_run, "proj_en_ki.npy")
        config.TGT_EMBS_KI_PATH = os.path.join(new_run, "tgt_embs_ki.npy")
        config.TGT_EMBS_EN_PATH = os.path.join(new_run, "tgt_embs_en.npy")
        config.METRICS_JSON_PATH = os.path.join(new_run, "evaluation_metrics.json")
        config.SP_MODEL_PATH = os.path.join(new_run, "sentencepiece.model")
        state_file = os.path.join(new_run, "training_state.json")
        state = {"status": "in_progress", "steps": []}
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f)
        logger.info(f"Created new training run directory: {new_run}")
        return state, state_file

    logger.info(f"Resuming training run directory: {latest_run}")
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {"status": "in_progress", "steps": []}
    return state, state_file


def save_state(state_file: str, state: dict) -> None:
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick-test", action="store_true", help="Run a quick test on a subset of data")
    args = parser.parse_args()

    os.makedirs(config.MODELS_DIR, exist_ok=True)
    state, state_file = setup_and_get_state()
    
    dim = config.EMBEDDING_DIM

    train_ki_path = config.TRAIN_KI_TXT
    train_en_path = config.TRAIN_EN_TXT
    
    if args.quick_test:
        import tempfile
        logger.info("Running in QUICK TEST mode using validation TSV as training data")
        temp_dir = tempfile.mkdtemp()
        train_ki_path = os.path.join(temp_dir, "test_ki.txt")
        train_en_path = os.path.join(temp_dir, "test_en.txt")
        val_ki, val_en = load_sentences(config.VAL_TSV_PATH)
        # write out to txt for fasttext
        with open(train_ki_path, "w", encoding="utf-8") as f:
            for line in val_ki: f.write(line + "\n")
        with open(train_en_path, "w", encoding="utf-8") as f:
            for line in val_en: f.write(line + "\n")
        config.FASTTEXT_EPOCH = 5
        
    tokenizer = None

    # 1. Train Monolingual Models
    ki_model = train_monolingual(train_ki_path, config.KI_MODEL_PATH, dim=dim)
    if "train_kikuyu" not in state["steps"]:
        state["steps"].append("train_kikuyu")
        save_state(state_file, state)
        
    en_model = train_monolingual(train_en_path, config.EN_MODEL_PATH, dim=dim)
    if "train_english" not in state["steps"]:
        state["steps"].append("train_english")
        save_state(state_file, state)

    # 2. Learn Cross-Lingual Alignment (SVD + iterative Procrustes refinement)
    if os.path.exists(config.PROJ_KI_EN_PATH) and os.path.exists(config.PROJ_EN_KI_PATH):
        logger.info("Projection matrices already exist. Resuming and loading them.")
        W_ki_en = np.load(config.PROJ_KI_EN_PATH)
        W_en_ki = np.load(config.PROJ_EN_KI_PATH)
    else:
        ki_words = ki_model.get_words()
        en_words = en_model.get_words()
        seed_words = extract_identical_string_dictionary(ki_words, en_words)
        
        logger.info(f"Extracted {len(seed_words)} identical strings to use as anchor dictionary.")
        
        X = np.array([ki_model.get_word_vector(w) for w in seed_words]).T
        Y = np.array([en_model.get_word_vector(w) for w in seed_words]).T

        if "precompute_embeddings" not in state["steps"]:
            # We skip precomputing huge corpus embeddings for serving right here since we aren't using parallel sentences
            state["steps"].append("precompute_embeddings")
            save_state(state_file, state)

        logger.info("Learning initial alignment matrices...")
        W_ki_en_init = learn_alignment_matrix(X, Y)
        W_en_ki_init = learn_alignment_matrix(Y, X)

        logger.info("Refining matrices via iterative Procrustes with CSLS...")
        # Get top 20,000 words for mutual nearest neighbor iterative alignment
        ki_top_words = ki_words[:20000]
        en_top_words = en_words[:20000]
        X_all = np.array([ki_model.get_word_vector(w) for w in ki_top_words]).T
        Y_all = np.array([en_model.get_word_vector(w) for w in en_top_words]).T

        W_ki_en = iterative_procrustes(
            X_all, Y_all, W_ki_en_init, n_iters=config.ALIGNMENT_REFINEMENT_ITERS
        )
        W_en_ki = iterative_procrustes(
            Y_all, X_all, W_en_ki_init, n_iters=config.ALIGNMENT_REFINEMENT_ITERS
        )
        
        del X
        del Y
        del X_all
        del Y_all
        del W_ki_en_init
        del W_en_ki_init
        gc.collect()

        np.save(config.PROJ_KI_EN_PATH, W_ki_en)
        np.save(config.PROJ_EN_KI_PATH, W_en_ki)
        logger.info("Alignment projection matrices saved.")
        if "align_models" not in state["steps"]:
            state["steps"].append("align_models")
            save_state(state_file, state)

    # 3. Evaluate on Validation Set
    val_ki, val_en = load_sentences(config.VAL_TSV_PATH)
    # Limit evaluation to 1000 sentences to avoid O(N^2) hang
    val_ki = val_ki[:1000]
    val_en = val_en[:1000]
    logger.info(f"Evaluating alignment on {len(val_ki)} validation sentences...")

    val_tgt_en = get_sentence_embeddings_parallel(config.EN_MODEL_PATH, val_en, dim=dim)
    val_tgt_ki = get_sentence_embeddings_parallel(config.KI_MODEL_PATH, val_ki, dim=dim)
    
    translator_ki_en = CrossLingualTranslator(ki_model, en_model, W_ki_en, val_en, precomputed_tgt_embeddings=val_tgt_en)
    translator_en_ki = CrossLingualTranslator(en_model, ki_model, W_en_ki, val_ki, precomputed_tgt_embeddings=val_tgt_ki)
    metrics_ki_en = evaluate_translator(translator_ki_en, val_ki, val_en)
    metrics_en_ki = evaluate_translator(translator_en_ki, val_en, val_ki)

    metrics = {"kikuyu_to_english": metrics_ki_en, "english_to_kikuyu": metrics_en_ki}

    logger.info("\nEvaluation Metrics:")
    logger.info(json.dumps(metrics, indent=2))

    save_metrics(metrics)
    
    state["status"] = "completed"
    save_state(state_file, state)
    logger.info("Training run completed successfully.")


if __name__ == "__main__":
    main()
