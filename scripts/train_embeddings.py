"""Script to train monolingual FastText models and learn cross-lingual alignment."""

import argparse
import csv
import datetime
import gc
import json
import multiprocessing
import os
import tempfile
from pathlib import Path

import fasttext
import numpy as np
import pandas as pd

from app.api.embeddings import (
    CrossLingualTranslator,
    extract_identical_string_dictionary,
    get_sentence_embedding,
    get_sentence_embeddings_parallel,
    iterative_procrustes,
    learn_alignment_matrix,
)
from app.shared import config
from app.shared.logger import setup_logger
from scripts.evaluate import calculate_translation_scores, evaluate_retrieval_accuracy

logger = setup_logger(__name__)


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


def load_all_parallel_csvs(parallel_dir: str) -> tuple[list[str], list[str]]:
    """Loads all parallel CSV files from a directory, returning (ki_list, en_list)."""
    ki_list: list[str] = []
    en_list: list[str] = []
    csv_files = sorted(Path(parallel_dir).glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {parallel_dir}")
    for csv_path in csv_files:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ki = row.get("Kikuyu", "").strip()
                en = row.get("English", "").strip()
                if ki and en:
                    ki_list.append(ki)
                    en_list.append(en)
    logger.info(
        f"Loaded {len(ki_list)} sentence pairs from {len(csv_files)} CSV files in {parallel_dir}"
    )
    return ki_list, en_list


def write_monolingual_txt(sentences: list[str], path: str) -> None:
    """Writes one sentence per line to a plain-text file for FastText training."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for s in sentences:
            f.write(s + "\n")
    logger.info(f"Wrote {len(sentences)} sentences to {path}")


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


def save_metrics(
    metrics: dict[str, dict[str, float]], metrics_path: str | None = None
) -> None:
    """Saves metrics, merging with existing data to preserve offline evaluation scores."""
    if metrics_path is None:
        metrics_path = config.METRICS_JSON_PATH
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
    parser.add_argument(
        "--quick-test", action="store_true", help="Run a quick test on a subset of data"
    )
    args = parser.parse_args()

    os.makedirs(config.MODELS_DIR, exist_ok=True)
    state, state_file = setup_and_get_state()

    dim = config.EMBEDDING_DIM

    # Load all parallel CSVs and split: last VAL_SIZE pairs held out for evaluation
    parallel_dir = config.PARALLEL_DATA_DIR
    all_ki, all_en = load_all_parallel_csvs(parallel_dir)

    VAL_SIZE = config.VAL_SIZE
    train_ki_sentences = all_ki[:-VAL_SIZE]
    train_en_sentences = all_en[:-VAL_SIZE]
    val_ki = all_ki[-VAL_SIZE:]
    val_en = all_en[-VAL_SIZE:]
    logger.info(
        f"Split: {len(train_ki_sentences)} train / {len(val_ki)} val sentence pairs"
    )

    # Write monolingual train files into the run directory so each run is self-contained
    train_ki_path = os.path.join(config.LATEST_RUN_DIR, "train.kikuyu")
    train_en_path = os.path.join(config.LATEST_RUN_DIR, "train.english")
    write_monolingual_txt(train_ki_sentences, train_ki_path)
    write_monolingual_txt(train_en_sentences, train_en_path)

    if args.quick_test:
        logger.info("Running in QUICK TEST mode — using first 200 pairs, 5 epochs")
        temp_dir = tempfile.mkdtemp()
        train_ki_path = os.path.join(temp_dir, "test_ki.txt")
        train_en_path = os.path.join(temp_dir, "test_en.txt")
        write_monolingual_txt(all_ki[:200], train_ki_path)
        write_monolingual_txt(all_en[:200], train_en_path)
        val_ki = all_ki[200:300]
        val_en = all_en[200:300]
        config.FASTTEXT_EPOCH = 5

    # 1. Train Monolingual Models
    ki_model = train_monolingual(train_ki_path, config.KI_MODEL_PATH, dim=dim)
    if "train_kikuyu" not in state["steps"]:
        state["steps"].append("train_kikuyu")
        save_state(state_file, state)

    en_model = train_monolingual(train_en_path, config.EN_MODEL_PATH, dim=dim)
    if "train_english" not in state["steps"]:
        state["steps"].append("train_english")
        save_state(state_file, state)

    # 2. Learn Cross-Lingual Alignment
    if os.path.exists(config.PROJ_KI_EN_PATH) and os.path.exists(config.PROJ_EN_KI_PATH):
        logger.info("Projection matrices already exist. Resuming and loading them.")
        W_ki_en = np.load(config.PROJ_KI_EN_PATH)
        W_en_ki = np.load(config.PROJ_EN_KI_PATH)
    else:
        ki_words = ki_model.get_words()
        en_words = en_model.get_words()

        # ── Supervised Procrustes from parallel sentence embeddings ──────────
        # Use the training pairs directly as alignment anchors — much stronger
        # than loanwords or identical strings alone.
        logger.info(
            f"Computing sentence embeddings for {len(train_ki_sentences)} training pairs..."
        )
        ki_sent_embs = np.array([
            get_sentence_embedding(ki_model, s) for s in train_ki_sentences
        ])  # (N, dim)
        en_sent_embs = np.array([
            get_sentence_embedding(en_model, s) for s in train_en_sentences
        ])  # (N, dim)

        # ── Source 2: seed dictionary word pairs (explicit translations) ────
        seed_dict_path = Path(config.SEED_DICTIONARY_PATH)
        if seed_dict_path.exists():
            logger.info(f"Augmenting anchors with seed dictionary from {seed_dict_path}")
            df_seed = pd.read_csv(seed_dict_path)
            seed_pairs = list(zip(df_seed["Kikuyu"], df_seed["English"], strict=False))
            seed_ki = np.array([ki_model.get_word_vector(str(k)) for k, _ in seed_pairs])
            seed_en = np.array([en_model.get_word_vector(str(e)) for _, e in seed_pairs])
            ki_sent_embs = np.vstack([ki_sent_embs, seed_ki])
            en_sent_embs = np.vstack([en_sent_embs, seed_en])
            logger.info(f"After seed dictionary: {len(ki_sent_embs)} anchor pairs")

        # ── Source 3: identical-string word pairs (vocabulary breadth) ────────
        # Same surface form in both vocabularies (shared proper nouns, numbers,
        # loanwords). Each model embeds them differently, so they carry real signal.
        identical_words = extract_identical_string_dictionary(ki_words, en_words)
        if identical_words:
            id_ki = np.array([ki_model.get_word_vector(w) for w in identical_words])
            id_en = np.array([en_model.get_word_vector(w) for w in identical_words])
            ki_sent_embs = np.vstack([ki_sent_embs, id_ki])
            en_sent_embs = np.vstack([en_sent_embs, id_en])
            logger.info(
                f"After identical strings: {len(ki_sent_embs)} total anchor pairs"
                f" ({len(identical_words)} identical-string pairs added)"
            )

        X = ki_sent_embs.T  # (dim, N)
        Y = en_sent_embs.T  # (dim, N)

        logger.info("Learning initial alignment matrices from supervised anchors...")
        W_ki_en_init = learn_alignment_matrix(X, Y)
        W_en_ki_init = learn_alignment_matrix(Y, X)

        del ki_sent_embs, en_sent_embs, X, Y
        gc.collect()

        # ── Iterative Procrustes refinement with MNN + CSLS ──────────────────
        logger.info("Refining matrices via iterative Procrustes with CSLS...")
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

        del X_all, Y_all, W_ki_en_init, W_en_ki_init
        gc.collect()

        np.save(config.PROJ_KI_EN_PATH, W_ki_en)
        np.save(config.PROJ_EN_KI_PATH, W_en_ki)
        logger.info("Alignment projection matrices saved.")
        if "align_models" not in state["steps"]:
            state["steps"].append("align_models")
            save_state(state_file, state)

    # 3. Full evaluation on the held-out val set
    logger.info(f"Evaluating on {len(val_ki)} validation sentences...")

    val_tgt_en = get_sentence_embeddings_parallel(config.EN_MODEL_PATH, val_en, dim=dim)
    val_tgt_ki = get_sentence_embeddings_parallel(config.KI_MODEL_PATH, val_ki, dim=dim)

    # Translators whose sentence bank IS the val set (required for accuracy/MRR)
    translator_ki_en = CrossLingualTranslator(
        ki_model, en_model, W_ki_en, val_en, precomputed_tgt_embeddings=val_tgt_en
    )
    translator_en_ki = CrossLingualTranslator(
        en_model, ki_model, W_en_ki, val_ki, precomputed_tgt_embeddings=val_tgt_ki
    )

    # Accuracy / MRR
    acc_ki_en = evaluate_retrieval_accuracy(translator_ki_en, val_ki, val_en)
    acc_en_ki = evaluate_retrieval_accuracy(translator_en_ki, val_en, val_ki)

    # BLEU / ChrF — retrieval
    ki_en_ret = [translator_ki_en.translate_sentence_retrieval(s) for s in val_ki]
    bleu_ki_en_ret, chrf_ki_en_ret = calculate_translation_scores(ki_en_ret, val_en)

    en_ki_ret = [translator_en_ki.translate_sentence_retrieval(s) for s in val_en]
    bleu_en_ki_ret, chrf_en_ki_ret = calculate_translation_scores(en_ki_ret, val_ki)

    # BLEU / ChrF — word-by-word
    ki_en_wbw = [translator_ki_en.translate_word_by_word(s) for s in val_ki]
    bleu_ki_en_wbw, chrf_ki_en_wbw = calculate_translation_scores(ki_en_wbw, val_en)

    en_ki_wbw = [translator_en_ki.translate_word_by_word(s) for s in val_en]
    bleu_en_ki_wbw, chrf_en_ki_wbw = calculate_translation_scores(en_ki_wbw, val_ki)

    metrics = {
        "kikuyu_to_english": {
            "bleu_retrieval": bleu_ki_en_ret,
            "chrf_retrieval": chrf_ki_en_ret,
            "bleu_word_by_word": bleu_ki_en_wbw,
            "chrf_word_by_word": chrf_ki_en_wbw,
            **acc_ki_en,
        },
        "english_to_kikuyu": {
            "bleu_retrieval": bleu_en_ki_ret,
            "chrf_retrieval": chrf_en_ki_ret,
            "bleu_word_by_word": bleu_en_ki_wbw,
            "chrf_word_by_word": chrf_en_ki_wbw,
            **acc_en_ki,
        },
    }

    logger.info("\nEvaluation Metrics:")
    logger.info(json.dumps(metrics, indent=2))

    save_metrics(metrics)

    state["status"] = "completed"
    save_state(state_file, state)
    logger.info("Training run completed successfully.")


if __name__ == "__main__":
    main()
