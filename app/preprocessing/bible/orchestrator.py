"""
Orchestrator to run preprocessing/extraction across different Bible books.
"""

import argparse
from pathlib import Path

from app.preprocessing.bible.matthew.service import MatthewExtractor
from app.preprocessing.bible.mark.service import MarkExtractor
from app.preprocessing.bible.luke.service import LukeExtractor
from app.preprocessing.bible.john.service import JohnExtractor
from app.preprocessing.bible.acts.service import ActsExtractor
from app.preprocessing.bible.romans.service import RomansExtractor
from app.preprocessing.bible.corinthians1.service import Corinthians1Extractor
from app.preprocessing.bible.corinthians2.service import Corinthians2Extractor
from app.preprocessing.bible.galatians.service import GalatiansExtractor
from app.preprocessing.bible.ephesians.service import EphesiansExtractor
from app.preprocessing.bible.philippians.service import PhilippiansExtractor
from app.preprocessing.bible.colossians.service import ColossiansExtractor
from app.preprocessing.bible.thessalonians1.service import Thessalonians1Extractor
from app.preprocessing.bible.psalms.service import PsalmsExtractor
from app.preprocessing.bible.genesis.service import GenesisExtractor
from app.preprocessing.bible.proverbs.service import ProverbsExtractor
from app.preprocessing.bible.ecclesiastes.service import EcclesiastesExtractor
from app.preprocessing.bible.jeremiah.service import JeremiahExtractor

BOOKS = [
    ("Matthew", MatthewExtractor, "matthew_aligned.csv"),
    ("Mark", MarkExtractor, "mark_aligned.csv"),
    ("Luke", LukeExtractor, "luke_aligned.csv"),
    ("John", JohnExtractor, "john_aligned.csv"),
    ("Acts", ActsExtractor, "acts_aligned.csv"),
    ("Romans", RomansExtractor, "romans_aligned.csv"),
    ("1 Corinthians", Corinthians1Extractor, "corinthians1_aligned.csv"),
    ("2 Corinthians", Corinthians2Extractor, "corinthians2_aligned.csv"),
    ("Galatians", GalatiansExtractor, "galatians_aligned.csv"),
    ("Ephesians", EphesiansExtractor, "ephesians_aligned.csv"),
    ("Philippians", PhilippiansExtractor, "philippians_aligned.csv"),
    ("Colossians", ColossiansExtractor, "colossians_aligned.csv"),
    ("1 Thessalonians", Thessalonians1Extractor, "thessalonians1_aligned.csv"),
    ("Psalms", PsalmsExtractor, "psalms_aligned.csv"),
    ("Genesis", GenesisExtractor, "genesis_aligned.csv"),
    ("Proverbs", ProverbsExtractor, "proverbs_aligned.csv"),
    ("Ecclesiastes", EcclesiastesExtractor, "ecclesiastes_aligned.csv"),
    ("Jeremiah", JeremiahExtractor, "jeremiah_aligned.csv"),
]


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
    parser.add_argument(
        "--book",
        type=str,
        default=None,
        help="Extract a single book by name (e.g. Matthew, Mark). Omit to run all.",
    )
    args = parser.parse_args()

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    books_to_run = [
        (name, cls, fname)
        for name, cls, fname in BOOKS
        if args.book is None or args.book.lower() == name.lower()
    ]

    for book_name, ExtractorClass, csv_name in books_to_run:
        print(f"\nStarting Book of {book_name} Extraction...")
        extractor = ExtractorClass()
        df = extractor.extract_and_align(args.kikuyu_pdf, args.english_pdf)

        csv_file = output_path / csv_name
        df.to_csv(csv_file, index=False, encoding="utf-8")
        print(f"Saved aligned {book_name} verses to: {csv_file}")
        print(f"Total aligned verses: {len(df)}")


if __name__ == "__main__":
    main()
