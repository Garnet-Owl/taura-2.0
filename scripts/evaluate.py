"""Offline translation evaluation pipeline using SacreBLEU and ChrF."""

import csv
import json
import os
from typing import List, Tuple, Dict
import numpy as np
import fasttext
import sacrebleu

from app.api.embeddings import CrossLingualTranslator


def load_test_data(tsv_path: str) -> Tuple[List[str], List[str]]:
    """Loads Kikuyu and English sentence pairs from a TSV file."""
    ki_sentences = []
    en_sentences = []
    if not os.path.exists(tsv_path):
        raise FileNotFoundError(f"Test file not found: {tsv_path}")

    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ki = row.get("kikuyu")
            en = row.get("english")
            if ki is not None and en is not None:
                ki_sentences.append(str(ki).strip())
                en_sentences.append(str(en).strip())
    return ki_sentences, en_sentences


def calculate_translation_scores(
    hypotheses: List[str], references: List[str]
) -> Tuple[float, float]:
    """Computes corpus BLEU and ChrF scores using sacrebleu."""
    bleu = sacrebleu.corpus_bleu(hypotheses, [references])
    chrf = sacrebleu.corpus_chrf(hypotheses, [references])
    return float(bleu.score), float(chrf.score)


def main() -> None:
    # Model and data paths
    ki_model_path = "models/ki.bin"
    en_model_path = "models/en.bin"
    proj_ki_en_path = "models/proj_ki_en.npy"
    proj_en_ki_path = "models/proj_en_ki.npy"
    train_tsv_path = "data/train.tsv"
    test_tsv_path = "data/test.tsv"
    metrics_json_path = "models/evaluation_metrics.json"

    # Verify everything exists
    for path in [
        ki_model_path,
        en_model_path,
        proj_ki_en_path,
        proj_en_ki_path,
        train_tsv_path,
        test_tsv_path,
    ]:
        if not os.path.exists(path):
            print(f"Error: Required file {path} is missing. Train models first.")
            return

    # Load FastText models
    print("Loading models...")
    ki_model = fasttext.load_model(ki_model_path)
    en_model = fasttext.load_model(en_model_path)

    # Load projection matrices
    W_ki_en = np.load(proj_ki_en_path)
    W_en_ki = np.load(proj_en_ki_path)

    # Load dictionaries for retrieval
    train_ki_sentences = []
    train_en_sentences = []
    with open(train_tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ki = row.get("kikuyu")
            en = row.get("english")
            if ki and en:
                train_ki_sentences.append(str(ki).strip())
                train_en_sentences.append(str(en).strip())

    # Initialize translators
    translator_ki_en = CrossLingualTranslator(
        ki_model, en_model, W_ki_en, train_en_sentences
    )
    translator_en_ki = CrossLingualTranslator(
        en_model, ki_model, W_en_ki, train_ki_sentences
    )

    # Load test split
    print("Loading test dataset...")
    test_ki, test_en = load_test_data(test_tsv_path)

    results: Dict[str, Dict[str, float]] = {
        "kikuyu_to_english_retrieval": {},
        "kikuyu_to_english_word_by_word": {},
        "english_to_kikuyu_retrieval": {},
        "english_to_kikuyu_word_by_word": {},
    }

    # 1. Kikuyu to English - Retrieval
    print("Evaluating Kikuyu to English (Retrieval)...")
    ki_en_ret_translations = [
        translator_ki_en.translate_sentence_retrieval(s) for s in test_ki
    ]
    b, c = calculate_translation_scores(ki_en_ret_translations, test_en)
    results["kikuyu_to_english_retrieval"] = {"bleu": b, "chrf": c}

    # 2. Kikuyu to English - Word-by-word
    print("Evaluating Kikuyu to English (Word-by-word)...")
    ki_en_wbw_translations = [
        translator_ki_en.translate_word_by_word(s) for s in test_ki
    ]
    b, c = calculate_translation_scores(ki_en_wbw_translations, test_en)
    results["kikuyu_to_english_word_by_word"] = {"bleu": b, "chrf": c}

    # 3. English to Kikuyu - Retrieval
    print("Evaluating English to Kikuyu (Retrieval)...")
    en_ki_ret_translations = [
        translator_en_ki.translate_sentence_retrieval(s) for s in test_en
    ]
    b, c = calculate_translation_scores(en_ki_ret_translations, test_ki)
    results["english_to_kikuyu_retrieval"] = {"bleu": b, "chrf": c}

    # 4. English to Kikuyu - Word-by-word
    print("Evaluating English to Kikuyu (Word-by-word)...")
    en_ki_wbw_translations = [
        translator_en_ki.translate_word_by_word(s) for s in test_en
    ]
    b, c = calculate_translation_scores(en_ki_wbw_translations, test_ki)
    results["english_to_kikuyu_word_by_word"] = {"bleu": b, "chrf": c}

    # Print results summary table
    print("\n### Translation Quality Summary")
    print("| Direction | Method | BLEU Score | ChrF Score |")
    print("| :--- | :--- | :---: | :---: |")
    for key, metrics in results.items():
        dir_label = (
            "Kikuyu -> English" if "kikuyu_to_english" in key else "English -> Kikuyu"
        )
        method_label = "Retrieval" if "retrieval" in key else "Word-by-Word"
        print(
            f"| {dir_label} | {method_label} | {metrics['bleu']:.2f} | {metrics['chrf']:.2f} |"
        )

    # Save to models/evaluation_metrics.json
    metrics_data = {}
    if os.path.exists(metrics_json_path):
        try:
            with open(metrics_json_path, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
        except json.JSONDecodeError:
            pass

    # Ensure sections exist and assign new metrics
    if "kikuyu_to_english" not in metrics_data:
        metrics_data["kikuyu_to_english"] = {}
    if "english_to_kikuyu" not in metrics_data:
        metrics_data["english_to_kikuyu"] = {}

    metrics_data["kikuyu_to_english"].update(
        {
            "bleu_retrieval": results["kikuyu_to_english_retrieval"]["bleu"],
            "chrf_retrieval": results["kikuyu_to_english_retrieval"]["chrf"],
            "bleu_word_by_word": results["kikuyu_to_english_word_by_word"]["bleu"],
            "chrf_word_by_word": results["kikuyu_to_english_word_by_word"]["chrf"],
        }
    )

    metrics_data["english_to_kikuyu"].update(
        {
            "bleu_retrieval": results["english_to_kikuyu_retrieval"]["bleu"],
            "chrf_retrieval": results["english_to_kikuyu_retrieval"]["chrf"],
            "bleu_word_by_word": results["english_to_kikuyu_word_by_word"]["bleu"],
            "chrf_word_by_word": results["english_to_kikuyu_word_by_word"]["chrf"],
        }
    )

    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"\nSaved metrics to {metrics_json_path}")


if __name__ == "__main__":
    main()
