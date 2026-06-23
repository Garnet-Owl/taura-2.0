"""Offline translation evaluation pipeline using SacreBLEU, ChrF, Top-K Accuracy, and MRR."""

import csv
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import fasttext
import numpy as np
import sacrebleu

from app.api.embeddings import CrossLingualTranslator, get_sentence_embedding
from app.shared import config
from app.shared.logger import setup_logger

logger = setup_logger(__name__)


def load_all_parallel_csvs(parallel_dir: str) -> Tuple[List[str], List[str]]:
    """Loads all parallel CSV files from a directory, returning (ki_list, en_list)."""
    ki_list: List[str] = []
    en_list: List[str] = []
    csv_files = sorted(Path(parallel_dir).rglob("*.csv"))
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
        "Loaded %d sentence pairs from %d CSV files in %s",
        len(ki_list),
        len(csv_files),
        parallel_dir,
    )
    return ki_list, en_list


def calculate_translation_scores(
    hypotheses: List[str], references: List[str]
) -> Tuple[float, float]:
    """Computes corpus BLEU and ChrF scores using sacrebleu."""
    bleu = sacrebleu.corpus_bleu(hypotheses, [references])
    chrf = sacrebleu.corpus_chrf(hypotheses, [references])
    return float(bleu.score), float(chrf.score)


def evaluate_retrieval_accuracy(
    translator: CrossLingualTranslator,
    src_sentences: List[str],
    tgt_sentences: List[str],
) -> Dict[str, float]:
    """
    Computes Top-1 Accuracy, Top-5 Accuracy, and MRR for sentence retrieval.
    Each source sentence should map to the sentence at the same index in tgt_sentences.
    """
    correct_top1 = 0
    correct_top5 = 0
    mrr_sum = 0.0
    n = len(src_sentences)

    tgt_embs = translator.tgt_embeddings
    norms_tgt = np.linalg.norm(tgt_embs, axis=1)
    norms_tgt[norms_tgt < 1e-8] = 1.0

    segment_fn = getattr(translator, "src_segment_fn", None)

    for i, src_s in enumerate(src_sentences):
        query = segment_fn(src_s) if segment_fn is not None else src_s
        src_emb = get_sentence_embedding(translator.src_model, query)
        projected = translator.projection_matrix @ src_emb

        norm_projected = np.linalg.norm(projected)
        if norm_projected < 1e-8:
            mrr_sum += 1.0 / n
            continue

        scores = np.dot(tgt_embs, projected) / (norms_tgt * norm_projected)
        sorted_indices = np.argsort(scores)[::-1]

        try:
            rank = list(sorted_indices).index(i) + 1
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
    all_ki, all_en = load_all_parallel_csvs(config.PARALLEL_DATA_DIR)

    val_size = config.VAL_SIZE
    corpus_ki = all_ki[:-val_size]
    corpus_en = all_en[:-val_size]
    test_ki = all_ki[-val_size:]
    test_en = all_en[-val_size:]
    logger.info("Corpus: %d sentences | Test: %d sentences", len(corpus_ki), len(test_ki))

    for path in [
        config.KI_MODEL_PATH,
        config.EN_MODEL_PATH,
        config.PROJ_KI_EN_PATH,
        config.PROJ_EN_KI_PATH,
    ]:
        if not os.path.exists(path):
            logger.error("Required file %s is missing. Train models first.", path)
            return

    logger.info("Loading models...")
    ki_model = fasttext.load_model(config.KI_MODEL_PATH)
    en_model = fasttext.load_model(config.EN_MODEL_PATH)

    W_ki_en = np.load(config.PROJ_KI_EN_PATH)
    W_en_ki = np.load(config.PROJ_EN_KI_PATH)

    translator_ki_en = CrossLingualTranslator(ki_model, en_model, W_ki_en, corpus_en)
    translator_en_ki = CrossLingualTranslator(en_model, ki_model, W_en_ki, corpus_ki)

    # --- BLEU / ChrF ---
    logger.info("Evaluating Kikuyu -> English (Retrieval)...")
    ki_en_ret = [translator_ki_en.translate_sentence_retrieval(s) for s in test_ki]
    bleu_ki_en_ret, chrf_ki_en_ret = calculate_translation_scores(ki_en_ret, test_en)

    logger.info("Evaluating Kikuyu -> English (Word-by-word)...")
    ki_en_wbw = [translator_ki_en.translate_word_by_word(s) for s in test_ki]
    bleu_ki_en_wbw, chrf_ki_en_wbw = calculate_translation_scores(ki_en_wbw, test_en)

    logger.info("Evaluating English -> Kikuyu (Retrieval)...")
    en_ki_ret = [translator_en_ki.translate_sentence_retrieval(s) for s in test_en]
    bleu_en_ki_ret, chrf_en_ki_ret = calculate_translation_scores(en_ki_ret, test_ki)

    logger.info("Evaluating English -> Kikuyu (Word-by-word)...")
    en_ki_wbw = [translator_en_ki.translate_word_by_word(s) for s in test_en]
    bleu_en_ki_wbw, chrf_en_ki_wbw = calculate_translation_scores(en_ki_wbw, test_ki)

    # --- Accuracy / MRR (use a sub-translator whose sentence bank IS the test set
    #     so rank 1 = exact match, consistent with train_embeddings.py) ---
    logger.info("Evaluating retrieval accuracy / MRR...")
    acc_translator_ki_en = CrossLingualTranslator(ki_model, en_model, W_ki_en, test_en)
    acc_translator_en_ki = CrossLingualTranslator(en_model, ki_model, W_en_ki, test_ki)
    acc_ki_en = evaluate_retrieval_accuracy(acc_translator_ki_en, test_ki, test_en)
    acc_en_ki = evaluate_retrieval_accuracy(acc_translator_en_ki, test_en, test_ki)

    # --- Merge and save ---
    metrics_data: Dict = {}
    if os.path.exists(config.METRICS_JSON_PATH):
        try:
            with open(config.METRICS_JSON_PATH, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
        except json.JSONDecodeError:
            pass

    metrics_data.setdefault("kikuyu_to_english", {})
    metrics_data.setdefault("english_to_kikuyu", {})

    metrics_data["kikuyu_to_english"].update({
        "bleu_retrieval": bleu_ki_en_ret,
        "chrf_retrieval": chrf_ki_en_ret,
        "bleu_word_by_word": bleu_ki_en_wbw,
        "chrf_word_by_word": chrf_ki_en_wbw,
        **acc_ki_en,
    })
    metrics_data["english_to_kikuyu"].update({
        "bleu_retrieval": bleu_en_ki_ret,
        "chrf_retrieval": chrf_en_ki_ret,
        "bleu_word_by_word": bleu_en_ki_wbw,
        "chrf_word_by_word": chrf_en_ki_wbw,
        **acc_en_ki,
    })

    with open(config.METRICS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    logger.info("Saved metrics to %s", config.METRICS_JSON_PATH)

    # --- Summary table ---
    logger.info("\n### Translation Quality Summary")
    logger.info(
        "%-22s %-12s %6s %6s %8s %8s %6s",
        "Direction",
        "Method",
        "BLEU",
        "ChrF",
        "Top-1",
        "Top-5",
        "MRR",
    )
    logger.info("-" * 72)
    for direction, bleu_ret, chrf_ret, bleu_wbw, chrf_wbw, acc in [
        (
            "Kikuyu -> English",
            bleu_ki_en_ret,
            chrf_ki_en_ret,
            bleu_ki_en_wbw,
            chrf_ki_en_wbw,
            acc_ki_en,
        ),
        (
            "English -> Kikuyu",
            bleu_en_ki_ret,
            chrf_en_ki_ret,
            bleu_en_ki_wbw,
            chrf_en_ki_wbw,
            acc_en_ki,
        ),
    ]:
        logger.info(
            "%-22s %-12s %6.2f %6.2f %8.0f%% %8.0f%% %6.3f",
            direction,
            "Retrieval",
            bleu_ret,
            chrf_ret,
            acc["accuracy_top1"] * 100,
            acc["accuracy_top5"] * 100,
            acc["mrr"],
        )
        logger.info(
            "%-22s %-12s %6.2f %6.2f %8s %8s %6s",
            "",
            "Word-by-word",
            bleu_wbw,
            chrf_wbw,
            "-",
            "-",
            "-",
        )


if __name__ == "__main__":
    main()
