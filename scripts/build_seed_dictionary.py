import argparse
import logging
import pandas as pd
from collections import defaultdict
from pathlib import Path
import re

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def normalize_word(word: str) -> str:
    # Lowercase and strip punctuation including curly quotes
    word = word.lower().strip(".,!?;:\"'()[]{}«»”’“‘")
    # Transliterate macrons (ī/ū) to tildes (ĩ/ũ)
    trans = str.maketrans("īū", "ĩũ")
    word = word.translate(trans)
    return word


def build_seed_dictionary(xlsx_path: str, output_csv: str, top_k: int = 1000):
    logger.info(f"Loading dataset from {xlsx_path}")
    if xlsx_path.endswith(".csv"):
        df = pd.read_csv(xlsx_path)
        df = df[["English", "Kikuyu"]]
        logger.info(f"Loaded {len(df)} sentence pairs from CSV.")
    else:
        xls = pd.ExcelFile(xlsx_path)
        dfs = []
        for sheet in xls.sheet_names:
            df_sheet = xls.parse(sheet)
            if "English" in df_sheet.columns and "Kikuyu" in df_sheet.columns:
                dfs.append(df_sheet[["English", "Kikuyu"]])

        if not dfs:
            raise ValueError(
                "Dataset must contain sheets with 'English' and 'Kikuyu' columns."
            )

        df = pd.concat(dfs, ignore_index=True)
        logger.info(
            f"Loaded {len(df)} sentence pairs across {len(xls.sheet_names)} sheets."
        )

    eng_counts = defaultdict(int)
    kik_counts = defaultdict(int)
    co_occurrences = defaultdict(int)

    logger.info("Computing word co-occurrences...")
    for _, row in df.iterrows():
        eng_text = str(row["English"])
        kik_text = str(row["Kikuyu"])

        if pd.isna(eng_text) or pd.isna(kik_text) or not eng_text or not kik_text:
            continue

        eng_words = set(normalize_word(w) for w in eng_text.split() if w)
        kik_words = set(normalize_word(w) for w in kik_text.split() if w)

        # Filter out tiny words or empty strings
        eng_words = {w for w in eng_words if len(w) > 2}
        kik_words = {w for w in kik_words if len(w) > 2}

        for ew in eng_words:
            eng_counts[ew] += 1
        for kw in kik_words:
            kik_counts[kw] += 1

        for ew in eng_words:
            for kw in kik_words:
                co_occurrences[(ew, kw)] += 1

    logger.info("Calculating Dice coefficient to find best matches...")
    matches = []
    # Only consider pairs that co-occur at least 3 times to avoid noise
    for (ew, kw), co_count in co_occurrences.items():
        if co_count >= 3:
            dice = (2.0 * co_count) / (eng_counts[ew] + kik_counts[kw])
            matches.append((ew, kw, dice, co_count))

    # Sort by dice coefficient (descending), then by co-occurrence count
    matches.sort(key=lambda x: (x[2], x[3]), reverse=True)

    # Filter to ensure 1-to-1 mapping
    best_matches = []
    seen_eng = set()
    seen_kik = set()

    # Pre-add manual known pairs provided by the user (normalized)
    manual_pairs = [
        ("water", "maĩ"),
        ("god", "ngai"),
        ("hello", "niatia"),
        ("coffee", "kahũa"),
        ("tree", "mũtĩ"),
        ("food", "irio"),
    ]

    for ew, kw in manual_pairs:
        # Just in case, normalize manual pairs too
        ew_norm = normalize_word(ew)
        kw_norm = normalize_word(kw)
        best_matches.append((ew_norm, kw_norm))
        seen_eng.add(ew_norm)
        seen_kik.add(kw_norm)

    # Common English stopwords to avoid mapping to themselves in Kikuyu space
    ENGLISH_STOPWORDS = {
        "and",
        "the",
        "for",
        "with",
        "that",
        "this",
        "not",
        "but",
        "you",
        "your",
        "his",
        "her",
        "their",
        "they",
        "them",
        "from",
        "are",
        "was",
        "were",
        "been",
        "have",
        "has",
        "had",
        "will",
        "would",
        "shall",
        "should",
        "can",
        "could",
        "about",
        "into",
        "onto",
        "upon",
        "than",
        "then",
        "them",
        "more",
        "most",
    }

    # Add identical strings automatically (e.g. SL-28, Ruiru, numbers)
    for ew in eng_counts:
        if ew in kik_counts and ew not in seen_eng and ew not in seen_kik:
            if ew in ENGLISH_STOPWORDS:
                continue
            if re.match(r"^[a-z0-9\-]+$", ew) and eng_counts[ew] >= 2:
                best_matches.append((ew, ew))
                seen_eng.add(ew)
                seen_kik.add(ew)

    # Add statistical matches
    for ew, kw, dice, count in matches:
        if ew not in seen_eng and kw not in seen_kik:
            best_matches.append((ew, kw))
            seen_eng.add(ew)
            seen_kik.add(kw)
            if len(best_matches) >= top_k:
                break

    logger.info(f"Extracted {len(best_matches)} high-confidence word pairs.")

    # Save to CSV
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_df = pd.DataFrame(best_matches, columns=["English", "Kikuyu"])
    out_df.to_csv(out_path, index=False, encoding="utf-8")
    logger.info(f"Seed dictionary saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract seed dictionary from parallel sentences"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/English20Kikuyu20Pairs2029.xlsx",
        help="Input XLSX file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/seed_dictionary.csv",
        help="Output CSV file",
    )
    parser.add_argument(
        "--top-k", type=int, default=1000, help="Number of word pairs to extract"
    )

    args = parser.parse_args()
    build_seed_dictionary(args.input, args.output, args.top_k)
