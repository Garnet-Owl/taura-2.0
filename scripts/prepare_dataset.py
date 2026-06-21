import os
import sys
import pandas as pd
from huggingface_hub import hf_hub_download

# Add root directory to sys.path to import app.api.split
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.api.split import split_data
from app.api import config
from app.shared.logger import setup_logger

logger = setup_logger(__name__)





def main() -> None:
    logger.info("Downloading CGIAR dataset from Hugging Face...")
    all_pairs = []
    try:
        cgiar_path = hf_hub_download(
            repo_id=config.REPO_CGIAR,
            filename="English - Kikuyu Sentence Pairs Final (1).xlsx",
            repo_type="dataset",
        )
        logger.info("Downloaded CGIAR dataset to %s", cgiar_path)
        logger.info("Parsing CGIAR Excel file...")
        xls = pd.ExcelFile(cgiar_path)

        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            if "English" not in df.columns or "Kikuyu" not in df.columns:
                continue

            df = df.dropna(subset=["English", "Kikuyu"])
            for _, row in df.iterrows():
                en = str(row["English"]).strip()
                ki = str(row["Kikuyu"]).strip()
                if en and ki:
                    all_pairs.append((ki, en))
        logger.info("Extracted %s pairs from CGIAR.", len(all_pairs))
    except Exception as e:
        logger.error("Error downloading or parsing CGIAR dataset: %s", e)
        sys.exit(1)

    logger.info("Downloading Mich dataset from Hugging Face...")
    try:
        mich_path = hf_hub_download(
            repo_id=config.REPO_MICH,
            filename="English-Kikuyu_Sentence-Pairs.csv",
            repo_type="dataset",
        )
        logger.info("Downloaded Mich dataset to %s", mich_path)
        logger.info("Parsing Mich CSV file...")
        mich_df = pd.read_csv(mich_path)
        if "English" in mich_df.columns and "Kikuyu" in mich_df.columns:
            mich_df = mich_df.dropna(subset=["English", "Kikuyu"])
            count_mich = 0
            for _, row in mich_df.iterrows():
                en = str(row["English"]).strip()
                ki = str(row["Kikuyu"]).strip()
                if en and ki:
                    all_pairs.append((ki, en))
                    count_mich += 1
            logger.info("Extracted %s pairs from Mich dataset.", count_mich)
    except Exception as e:
        logger.error("Error downloading or parsing Mich dataset: %s", e)
        sys.exit(1)

    logger.info("Extracted a total of %s valid sentence pairs.", len(all_pairs))

    # Create data/ directory if it doesn't exist
    os.makedirs(config.DATA_DIR, exist_ok=True)

    # Split dataset
    train, val, test = split_data(
        all_pairs, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42
    )

    # Save as TSV files
    for split_name, split_data_list in [("train", train), ("val", val), ("test", test)]:
        file_path = os.path.join(config.DATA_DIR, f"{split_name}.tsv")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("kikuyu\tenglish\n")
            for ki, en in split_data_list:
                # Replace any tabs/newlines in sentences to preserve TSV format
                ki_clean = ki.replace("\t", " ").replace("\n", " ").replace("\r", " ")
                en_clean = en.replace("\t", " ").replace("\n", " ").replace("\r", " ")
                f.write(f"{ki_clean}\t{en_clean}\n")
        logger.info("Saved %s pairs to %s", len(split_data_list), file_path)

    # Also save raw monolingual text files for training FastText embeddings
    # (one sentence per line)
    from app.api.preprocessing import normalize_text

    for lang, idx in [("kikuyu", 0), ("english", 1)]:
        train_lang_path = os.path.join(config.DATA_DIR, f"train.{lang}")
        with open(train_lang_path, "w", encoding="utf-8") as f:
            for pair in train:
                sentence = pair[idx]
                normalized = normalize_text(sentence)
                if normalized:
                    f.write(f"{normalized}\n")
        logger.info("Saved raw normalized monolingual sentences to %s", train_lang_path)




if __name__ == "__main__":
    main()
