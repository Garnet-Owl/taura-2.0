"""
Bible PDF parsing module for the Taura project.

This module extracts text from Kikuyu and English Bible PDFs,
aligns verses between languages, and creates parallel corpora for
training machine translation models.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from scripts.preprocessing.structure.bible_structure import (
    get_book_by_name,
    get_book_by_kikuyu_name,
    is_valid_reference,
    kikuyu_to_english_book_name,
)

# Ratio bounds for post-extraction quality filtering
_MIN_RATIO = 0.4
_MAX_RATIO = 2.5
_MIN_VERSE_CONTENT_LEN = 15

# Footnote / cross-reference patterns to strip from English verse text
_FOOTNOTE_RE = re.compile(
    r"""
    (?:                        # footnote markers
      [*†‡§]\s*\d+:\d+       #  * 7:7  / † 12:3
    | [*†‡§]\s*\d+           #  * 7
    | \b\d+:\d+\b            #  bare  7:7  at start/end
    )""",
    re.VERBOSE,
)

# Measurement / unit stubs that indicate a footnote fragment, not a verse
_MEASUREMENT_RE = re.compile(
    r"""^(?:
      (?:grams?|kg|kilograms?|ounces?|oz|pounds?|lb|liters?|litres?|
         milliliters?|ml|inches?|in|centimeters?|cm|kilometers?|km|miles?|
         cubits?|seah|ephah|hin|shekel)\s+(?:or|is|about|=|≈).*
    | [*†‡§;,]\s*\d[\d:,;\s*†‡§]*  # footnote-only content
    )$""",
    re.VERBOSE | re.IGNORECASE,
)

# Known Kikuyu paragraph continuation words that follow a section-digit
# e.g. "1 No rĩrĩa ..." is NOT verse 1 but a paragraph restart.
_KIK_PARAGRAPH_STARTERS = re.compile(
    r"^\d+\s+(No|Ningĩ|Na|Nake|Rĩrĩa|Nao|Arĩa|Naguo|Nokĩo|Nĩ\s)\b",
    re.UNICODE,
)

# Set paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PDF_DIR = DATA_DIR


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF (fitz).

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text from the PDF
    """
    try:
        import fitz  # PyMuPDF

        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"

        return text
    except ImportError:
        print(
            "PyMuPDF library not found. Please install it using 'pip install PyMuPDF'"
        )
        return ""
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""


def _clean_english_verse(text: str) -> str:
    """Strip footnote markers and measurement stubs from an English verse."""
    # Remove inline cross-reference markers like * 7:7  † 12:3  ‡ 9:4
    text = re.sub(r"[*†‡§]\s*\d+:\d+", "", text)
    text = re.sub(r"[*†‡§]\s*\d+", "", text)
    # Remove lone reference strings at line boundaries e.g. "  ; 18:18"
    text = re.sub(r"(?:^|\s)[;,]\s*\d+:\d+", "", text)
    # Remove parenthetical commentary that starts with a close paren
    text = re.sub(r"^\)\s*\.\s*", "", text.strip())
    return text.strip()


def _is_footnote_only(text: str) -> bool:
    """Return True if the text looks like a footnote stub, not a verse."""
    stripped = text.strip()
    if not stripped:
        return True
    if len(stripped) < _MIN_VERSE_CONTENT_LEN:
        return True
    if _MEASUREMENT_RE.match(stripped):
        return True
    return False


def preprocess_bible_text(text: str, language: str) -> str:
    """
    Preprocess Bible text to normalize formatting and make parsing easier.

    Args:
        text: Raw text from Bible PDF
        language: 'kikuyu' or 'english'

    Returns:
        Preprocessed text with normalized spacing and verse markers
    """
    # Step 1: Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Step 2: Fix inline verse numbers by adding a space before the word.
    # Guard against splitting numbers inside large figures (e.g. 35,400)
    if language == "kikuyu":
        text = re.sub(r"(\d+)([A-ZĨŨ])", r"\n\1 \2", text)
    else:
        text = re.sub(r"(\d+)([A-Z])", r"\n\1 \2", text)

    # Step 3: Break into paragraphs on book references
    if language == "kikuyu":
        book_pattern = (
            r"([A-ZĨŨ][A-Za-zĨŨĩũã\-]+(?:\s+[A-ZĨŨ][A-Za-zĨŨĩũã\-]+)*)\s+(\d+):(\d+)"
        )
    else:
        book_pattern = r"([A-Z][A-Za-z\-]+(?:\s+[A-Z][A-Za-z\-]+)*)\s+(\d+):(\d+)"

    text = re.sub(book_pattern, r"\n\1 \2:\3\n", text)

    # Step 4: Break at verse numbers that start a line
    text = re.sub(r"\s+(\d+)\s+", r"\n\1 ", text)

    return text


def parse_kikuyu_verse(text: str) -> Dict[str, Dict[int, Dict[int, str]]]:
    """
    Parse Kikuyu Bible text to extract verses.

    Args:
        text: Raw text from the Kikuyu Bible PDF

    Returns:
        Dictionary with structure {book_name: {chapter: {verse: verse_text}}}
    """
    # Dictionary to store the parsed verses
    bible_dict = {}

    # First preprocess the text to normalize verses
    text = preprocess_bible_text(text, "kikuyu")

    # Current book, chapter, and verse tracking
    current_book = None
    current_chapter = None
    current_verse = None

    # Process text line by line
    lines = text.split("\n")

    # Patterns for matching
    book_pattern = r"([A-ZĨŨĩũãĩ][A-Za-zĨŨĩũãĩ\-]+(?:\s+[A-ZĨŨĩũãĩ][A-Za-zĨŨĩũãĩ\-]+)*)(\s+)(\d+):(\d+)"
    verse_pattern = r"^\s*(\d+)\s+(.*)"

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to match a book reference
        book_match = re.match(book_pattern, line, re.UNICODE)
        if book_match:
            book_name = book_match.group(1)
            chapter_num = int(book_match.group(3))
            verse_num = int(book_match.group(4))

            # Try to find the canonical book name
            canonical_book = get_book_by_kikuyu_name(book_name)

            if canonical_book:
                current_book = canonical_book["kikuyu_name"]
                current_chapter = chapter_num

                if current_book not in bible_dict:
                    bible_dict[current_book] = {}
                if current_chapter not in bible_dict[current_book]:
                    bible_dict[current_book][current_chapter] = {}

                # Only add verse if it's valid according to our structure
                english_book = canonical_book["book_name"]
                if is_valid_reference(english_book, chapter_num, verse_num):
                    if verse_num not in bible_dict[current_book][current_chapter]:
                        bible_dict[current_book][current_chapter][verse_num] = ""
                        current_verse = verse_num
            continue

        # Skip Kikuyu paragraph-restart lines (e.g. "1 No rĩrĩa ...") —
        # these are section markers inside a verse, not new verse numbers.
        if _KIK_PARAGRAPH_STARTERS.match(line):
            if current_book and current_chapter and current_verse:
                continuation = re.sub(r"^\d+\s+", "", line)
                if current_verse in bible_dict[current_book][current_chapter]:
                    bible_dict[current_book][current_chapter][current_verse] += (
                        " " + continuation
                    )
            continue

        # Try to match a verse
        verse_match = re.match(verse_pattern, line)
        if verse_match and current_book and current_chapter:
            verse_num = int(verse_match.group(1))
            verse_text = verse_match.group(2).strip()

            # Require a minimum of real content to avoid capturing lone digits
            if len(verse_text) < _MIN_VERSE_CONTENT_LEN:
                continue

            english_book = kikuyu_to_english_book_name(current_book)
            if english_book and is_valid_reference(
                english_book, current_chapter, verse_num
            ):
                bible_dict[current_book][current_chapter][verse_num] = verse_text
                current_verse = verse_num
            continue

        # If no match but we have context, append to the current verse
        if current_book and current_chapter and current_verse:
            if current_verse in bible_dict[current_book][current_chapter]:
                bible_dict[current_book][current_chapter][current_verse] += " " + line

    return bible_dict


def parse_english_verse(text: str) -> Dict[str, Dict[int, Dict[int, str]]]:
    """
    Parse English Bible text to extract verses.

    Args:
        text: Raw text from the English Bible PDF

    Returns:
        Dictionary with structure {book_name: {chapter: {verse: verse_text}}}
    """
    # Dictionary to store the parsed verses
    bible_dict = {}

    # First preprocess the text to normalize verses
    text = preprocess_bible_text(text, "english")

    # Current book, chapter, and verse tracking
    current_book = None
    current_chapter = None
    current_verse = None

    # Process text line by line
    lines = text.split("\n")

    # Patterns for matching
    book_pattern = r"([A-Z][A-Za-z\-]+(?:\s+[A-Z][A-Za-z\-]+)*)(\s+)(\d+):(\d+)"
    verse_pattern = r"^\s*(\d+)\s+(.*)"

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to match a book reference
        book_match = re.match(book_pattern, line)
        if book_match:
            book_name = book_match.group(1)
            chapter_num = int(book_match.group(3))
            verse_num = int(book_match.group(4))

            # Try to find the canonical book name
            canonical_book = get_book_by_name(book_name)

            if canonical_book:
                current_book = canonical_book["book_name"]
                current_chapter = chapter_num

                if current_book not in bible_dict:
                    bible_dict[current_book] = {}
                if current_chapter not in bible_dict[current_book]:
                    bible_dict[current_book][current_chapter] = {}

                # Only add verse if it's valid according to our structure
                if is_valid_reference(current_book, chapter_num, verse_num):
                    if verse_num not in bible_dict[current_book][current_chapter]:
                        bible_dict[current_book][current_chapter][verse_num] = ""
                        current_verse = verse_num
            continue

        # Try to match a verse
        verse_match = re.match(verse_pattern, line)
        if verse_match and current_book and current_chapter:
            verse_num = int(verse_match.group(1))
            verse_text = _clean_english_verse(verse_match.group(2))

            # Skip footnote-only content masquerading as a verse
            if _is_footnote_only(verse_text):
                continue

            if is_valid_reference(current_book, current_chapter, verse_num):
                bible_dict[current_book][current_chapter][verse_num] = verse_text
                current_verse = verse_num
            continue

        # If no match but we have context, append to current verse
        if current_book and current_chapter and current_verse:
            cleaned = _clean_english_verse(line)
            if cleaned and not _is_footnote_only(cleaned):
                if current_verse in bible_dict[current_book][current_chapter]:
                    bible_dict[current_book][current_chapter][current_verse] += (
                        " " + cleaned
                    )

    return bible_dict


def align_verses(kikuyu_dict: Dict, english_dict: Dict) -> List[Tuple[str, str, str]]:
    """
    Align verses between Kikuyu and English Bibles.

    Args:
        kikuyu_dict: Dictionary of parsed Kikuyu Bible
        english_dict: Dictionary of parsed English Bible

    Returns:
        List of (reference, Kikuyu verse, English verse) tuples
    """
    aligned_verses = []

    # Iterate through Kikuyu books
    for kikuyu_book, chapters in kikuyu_dict.items():
        english_book = kikuyu_to_english_book_name(kikuyu_book)

        if english_book and english_book in english_dict:
            # Iterate through chapters
            for chapter_num, verses in chapters.items():
                if chapter_num in english_dict[english_book]:
                    # Iterate through verses
                    for verse_num, kikuyu_text in verses.items():
                        if verse_num in english_dict[english_book][chapter_num]:
                            english_text = english_dict[english_book][chapter_num][
                                verse_num
                            ]

                            # Skip empty verses
                            if not kikuyu_text.strip() or not english_text.strip():
                                continue

                            # Fix 1: length-ratio filter — skip wildly mismatched pairs
                            ratio = len(kikuyu_text) / max(len(english_text), 1)
                            if ratio < _MIN_RATIO or ratio > _MAX_RATIO:
                                continue

                            # Fix 2: reject footnote-only English text
                            if _is_footnote_only(english_text):
                                continue

                            reference = f"{kikuyu_book} {chapter_num}:{verse_num}"
                            aligned_verses.append(
                                (reference, kikuyu_text, english_text)
                            )

    return aligned_verses


def create_dataset(
    aligned_verses: List[Tuple[str, str, str]], max_examples: Optional[int] = None
) -> pd.DataFrame:
    """
    Create a dataset from aligned verses.

    Args:
        aligned_verses: List of (reference, Kikuyu verse, English verse) tuples
        max_examples: Maximum number of examples to include (None for all)

    Returns:
        Pandas DataFrame with Reference, Kikuyu, and English columns
    """
    if max_examples is not None:
        aligned_verses = aligned_verses[:max_examples]

    df = pd.DataFrame(aligned_verses, columns=["Reference", "Kikuyu", "English"])
    return df


def process_bible_texts(
    kikuyu_pdf_path: str, english_pdf_path: str, max_examples: Optional[int] = None
) -> pd.DataFrame:
    """
    Process Bible texts from PDFs and create a parallel corpus.

    Args:
        kikuyu_pdf_path: Path to Kikuyu Bible PDF
        english_pdf_path: Path to English Bible PDF
        max_examples: Maximum number of examples to include (None for all)

    Returns:
        Pandas DataFrame with aligned verses
    """
    print(f"Extracting text from {kikuyu_pdf_path}...")
    kikuyu_text = extract_text_from_pdf(kikuyu_pdf_path)

    print(f"Extracting text from {english_pdf_path}...")
    english_text = extract_text_from_pdf(english_pdf_path)

    print("Parsing Kikuyu verses...")
    kikuyu_dict = parse_kikuyu_verse(kikuyu_text)

    print("Parsing English verses...")
    english_dict = parse_english_verse(english_text)

    print("Aligning verses...")
    aligned_verses = align_verses(kikuyu_dict, english_dict)

    print(f"Creating dataset with {len(aligned_verses)} verse pairs...")
    if max_examples:
        print(f"Limiting to {max_examples} examples as requested")

    df = create_dataset(aligned_verses, max_examples)

    return df


def save_bible_dataset(df: pd.DataFrame, output_path: Optional[str] = None) -> None:
    """
    Save the Bible dataset to a CSV file.

    Args:
        df: DataFrame with aligned verses
        output_path: Path to save the CSV file (default: DATA_DIR/processed/bible_parallel.csv)
    """
    if output_path is None:
        output_path = PROCESSED_DIR / "bible_parallel.csv"

    df.to_csv(output_path, index=False)
    print(f"Saved Bible dataset to {output_path}")


if __name__ == "__main__":
    # Define paths to PDF files
    kikuyu_pdf = PDF_DIR / "Kikuyu_Bible_all.pdf"
    english_pdf = PDF_DIR / "English_Bible_all.pdf"

    # Process the Bible texts
    df = process_bible_texts(str(kikuyu_pdf), str(english_pdf), max_examples=None)

    # Save the dataset
    save_bible_dataset(df)
