"""
Orchestrator to run preprocessing/extraction across different Bible books.
"""

import argparse
from pathlib import Path

from app.preprocessing.bible.matthew.service import MatthewExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate Bible extraction and alignment."
    )
    parser.add_argument(
        "--kikuyu-pdf",
        type=str,
        default="data/Kikuyu_Bible_all.pdf",
        help="Path to Kikuyu Bible PDF",
    )
    parser.add_argument(
        "--english-pdf",
        type=str,
        default="data/English_Bible_all.pdf",
        help="Path to English Bible PDF",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/parallel",
        help="Directory to save extracted parallel datasets",
    )
    args = parser.parse_args()

    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("Starting Book of Matthew Extraction...")
    extractor = MatthewExtractor()
    df = extractor.extract_and_align(args.kikuyu_pdf, args.english_pdf)

    # Save to CSV
    csv_file = output_path / "matthew_aligned.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8")
    print(f"Saved aligned Matthew verses to: {csv_file}")
    print(f"Total aligned verses: {len(df)}")


if __name__ == "__main__":
    main()
