import os
import sys
import pandas as pd
from huggingface_hub import hf_hub_download

# Add root directory to sys.path to import app.api.split
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.api.split import split_data
from app.api import config


def main() -> None:
    print("Downloading CGIAR dataset from Hugging Face...")
    all_pairs = []
    try:
        cgiar_path = hf_hub_download(
            repo_id=config.REPO_CGIAR,
            filename="English - Kikuyu Sentence Pairs Final (1).xlsx",
            repo_type="dataset",
        )
        print(f"Downloaded CGIAR dataset to {cgiar_path}")
        print("Parsing CGIAR Excel file...")
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
        print(f"Extracted {len(all_pairs)} pairs from CGIAR.")
    except Exception as e:
        print(f"Error downloading or parsing CGIAR dataset: {e}")
        sys.exit(1)

    print("Downloading Mich dataset from Hugging Face...")
    try:
        mich_path = hf_hub_download(
            repo_id=config.REPO_MICH,
            filename="English-Kikuyu_Sentence-Pairs.csv",
            repo_type="dataset",
        )
        print(f"Downloaded Mich dataset to {mich_path}")
        print("Parsing Mich CSV file...")
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
            print(f"Extracted {count_mich} pairs from Mich dataset.")
    except Exception as e:
        print(f"Error downloading or parsing Mich dataset: {e}")
        sys.exit(1)

    print(f"Extracted a total of {len(all_pairs)} valid sentence pairs.")

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
        print(f"Saved {len(split_data_list)} pairs to {file_path}")

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
        print(f"Saved raw normalized monolingual sentences to {train_lang_path}")


if __name__ == "__main__":
    main()
