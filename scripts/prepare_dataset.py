"""Builds the seeded 80/10/10 train/validation/test split from data/parallel.

Run with: uv run python -m scripts.prepare_dataset
"""

import os
from pathlib import Path

import pandas as pd

from app.api.preprocessing import normalize_text
from app.api.split import split_data
from app.shared import config
from app.shared.logger import setup_logger

logger = setup_logger(__name__)


def load_parallel_pairs(parallel_dir: str) -> list[tuple[str, str]]:
    """Loads (kikuyu, english) pairs from every CSV under parallel_dir.

    Files are read in sorted path order, both sides are stripped, rows with an
    empty side are skipped, and exact duplicate pairs are kept once so the same
    pair cannot land in both train and validation.
    """
    csv_files = sorted(Path(parallel_dir).rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {parallel_dir}")
    pairs: dict[tuple[str, str], None] = {}
    for csv_path in csv_files:
        df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
        for ki, en in zip(df["Kikuyu"], df["English"], strict=True):
            pair = (ki.strip(), en.strip())
            if pair[0] and pair[1]:
                pairs.setdefault(pair, None)
    logger.info(f"Loaded {len(pairs)} distinct pairs from {len(csv_files)} CSV files")
    return list(pairs)


def _flatten(text: str) -> str:
    return text.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def write_split_tsv(pairs: list[tuple[str, str]], file_path: str) -> None:
    """Writes pairs to a kikuyu/english TSV, flattening tabs and newlines."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("kikuyu\tenglish\n")
        for ki, en in pairs:
            f.write(f"{_flatten(ki)}\t{_flatten(en)}\n")
    logger.info("Saved %s pairs to %s", len(pairs), file_path)


def main() -> None:
    logger.info("Starting dataset preparation pipeline...")
    all_pairs = load_parallel_pairs(config.PARALLEL_DATA_DIR)

    train, val, test = split_data(
        all_pairs, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42
    )
    write_split_tsv(train, config.TRAIN_TSV_PATH)
    write_split_tsv(val, config.VAL_TSV_PATH)
    write_split_tsv(test, config.TEST_TSV_PATH)

    # Also save raw monolingual text files for training FastText embeddings.
    # Use APPEND mode so that any existing large scraped corpora are preserved.
    for _lang, idx, train_lang_path in [
        ("kikuyu", 0, config.TRAIN_KI_TXT),
        ("english", 1, config.TRAIN_EN_TXT),
    ]:
        os.makedirs(os.path.dirname(train_lang_path), exist_ok=True)
        with open(train_lang_path, "a", encoding="utf-8") as f:
            for pair in train:
                sentence = pair[idx]
                normalized = normalize_text(sentence)
                if normalized:
                    f.write(f"{normalized}\n")
        logger.info("Appended normalized monolingual sentences to %s", train_lang_path)


if __name__ == "__main__":
    main()
