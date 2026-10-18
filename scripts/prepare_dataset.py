"""Builds the seeded 80/10/10 train/validation/test split from every parallel CSV.

Preprocessing steps:
1. Read every *.csv under the parallel data directory (Bible books and agriculture).
2. Drop rows where either side is empty, and drop exact duplicate (Kikuyu, English)
   pairs so the same pair cannot land in both train and validation/test.
3. Assign each pair to train (80%), validation (10%) or test (10%) from a SHA-256
   hash of the seed (42) and the pair's text. The assignment is stable: adding a
   book never moves an existing pair to another split. Proportions are approximate.
4. Write each split as a TSV with a "kikuyu\\tenglish" header to data/splits/.

Train only on train.tsv, tune and compare on val.tsv, and keep test.tsv for final
comparisons. Rebuild the split after adding a book: uv run python -m scripts.prepare_dataset
"""

import os

from app.api.split import split_by_hash
from app.shared import config
from app.shared.logger import setup_logger
from scripts.evaluate import load_all_parallel_csvs

logger = setup_logger(__name__)

SPLIT_SEED = 42


def load_parallel_pairs(parallel_dir: str) -> list[tuple[str, str]]:
    """Loads all (kikuyu, english) pairs, dropping exact duplicates in file order."""
    ki_list, en_list = load_all_parallel_csvs(parallel_dir)
    pairs = list(dict.fromkeys(zip(ki_list, en_list, strict=True)))
    logger.info("Kept %d unique pairs of %d loaded", len(pairs), len(ki_list))
    return pairs


def write_split_tsv(pairs: list[tuple[str, str]], file_path: str) -> None:
    """Writes pairs to a TSV file, flattening tabs and newlines inside sentences."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("kikuyu\tenglish\n")
        for ki, en in pairs:
            ki_clean = " ".join(ki.split())
            en_clean = " ".join(en.split())
            f.write(f"{ki_clean}\t{en_clean}\n")
    logger.info("Saved %d pairs to %s", len(pairs), file_path)


def build_splits(parallel_dir: str, splits_dir: str, seed: int = SPLIT_SEED) -> None:
    """Splits all parallel pairs about 80/10/10 by seeded hash and writes the TSVs."""
    pairs = load_parallel_pairs(parallel_dir)
    train, val, test = split_by_hash(
        pairs, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=seed
    )
    for name, split_pairs in [("train", train), ("val", val), ("test", test)]:
        write_split_tsv(split_pairs, os.path.join(splits_dir, f"{name}.tsv"))


def main() -> None:
    build_splits(config.PARALLEL_DATA_DIR, config.SPLITS_DIR)


if __name__ == "__main__":
    main()
