import os
import sys
import pandas as pd
from huggingface_hub import hf_hub_download

# Add root directory to sys.path to import app.api.split
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.api.split import split_data


def main() -> None:
    print("Downloading dataset from Hugging Face...")
    try:
        path = hf_hub_download(
            repo_id="CGIAR/KikuyuEnglish_translation",
            filename="English - Kikuyu Sentence Pairs Final (1).xlsx",
            repo_type="dataset",
        )
        print(f"Downloaded to {path}")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        sys.exit(1)

    print("Parsing Excel file...")
    xls = pd.ExcelFile(path)
    all_pairs = []

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        # Ensure correct columns exist
        if "English" not in df.columns or "Kikuyu" not in df.columns:
            print(f"Skipping sheet {sheet} due to missing columns")
            continue

        # Clean rows
        df = df.dropna(subset=["English", "Kikuyu"])
        for _, row in df.iterrows():
            en = str(row["English"]).strip()
            ki = str(row["Kikuyu"]).strip()
            if en and ki:
                all_pairs.append((ki, en))

    print(f"Extracted {len(all_pairs)} valid sentence pairs.")

    # Create data/ directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Split dataset
    train, val, test = split_data(
        all_pairs, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42
    )

    # Save as TSV files
    for split_name, split_data_list in [("train", train), ("val", val), ("test", test)]:
        file_path = os.path.join("data", f"{split_name}.tsv")
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
    for lang, idx in [("kikuyu", 0), ("english", 1)]:
        train_lang_path = os.path.join("data", f"train.{lang}")
        with open(train_lang_path, "w", encoding="utf-8") as f:
            for pair in train:
                sentence = pair[idx].replace("\n", " ").replace("\r", " ")
                f.write(f"{sentence}\n")
        print(f"Saved raw monolingual sentences to {train_lang_path}")


if __name__ == "__main__":
    main()
