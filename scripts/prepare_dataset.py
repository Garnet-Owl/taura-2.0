import os
import sys
import pandas as pd
from pathlib import Path

# Add root directory to sys.path to import app.api.split
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.api.split import split_data
from app.shared import config
from app.shared.logger import setup_logger

logger = setup_logger(__name__)


def main() -> None:
    logger.info("Starting dataset preparation pipeline...")
    all_pairs = []

    # We will load data exclusively from our processed Bible parallel dataset
    # instead of downloading the corrupted HuggingFace datasets.
    bible_csv_path = Path("data/processed/bible_parallel.csv")

    if bible_csv_path.exists():
        logger.info(
            f"Loading high-quality Bible parallel dataset from {bible_csv_path}"
        )
        df = pd.read_csv(bible_csv_path)
        if "English" in df.columns and "Kikuyu" in df.columns:
            df = df.dropna(subset=["English", "Kikuyu"])
            for _, row in df.iterrows():
                en = str(row["English"]).strip()
                ki = str(row["Kikuyu"]).strip()
                if en and ki:
                    all_pairs.append((ki, en))
        logger.info(f"Extracted {len(all_pairs)} pairs from the Bible dataset.")
    else:
        logger.warning(f"No Bible parallel dataset found at {bible_csv_path}.")
        logger.warning("Pipeline is awaiting execution of the PDF parser.")
        # We exit early because without clean data, generating splits is useless.
        logger.warning("Skipping TSV split generation until dataset is available.")
        sys.exit(0)

    # Create data/ directory if it doesn't exist
    os.makedirs(config.DATA_DIR, exist_ok=True)

    # Split dataset
    train, val, test = split_data(
        all_pairs, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42
    )

    # Save as TSV files
    for split_name, split_data_list, file_path in [
        ("train", train, config.TRAIN_TSV_PATH),
        ("val", val, config.VAL_TSV_PATH),
        ("test", test, config.TEST_TSV_PATH),
    ]:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("kikuyu\tenglish\n")
            for ki, en in split_data_list:
                ki_clean = ki.replace("\t", " ").replace("\n", " ").replace("\r", " ")
                en_clean = en.replace("\t", " ").replace("\n", " ").replace("\r", " ")
                f.write(f"{ki_clean}\t{en_clean}\n")
        logger.info("Saved %s pairs to %s", len(split_data_list), file_path)

    # Also save raw monolingual text files for training FastText embeddings.
    # Use APPEND mode so that any existing large scraped corpora are preserved.
    from app.api.preprocessing import normalize_text

    for lang, idx, train_lang_path in [
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
