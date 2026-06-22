"""
Utility script to generate a complete Bible structure Python module.

This script reads the complete Bible structure from bible_books.json
and generates an updated bible_structure.py with all 66 books.
"""

import json
from pathlib import Path

# Define path to JSON file and output Python file
CURRENT_DIR = Path(__file__).parent
JSON_PATH = CURRENT_DIR / "bible_books.json"
OUTPUT_PATH = CURRENT_DIR / "bible_structure.py"

# Kikuyu names for all 66 books (based on available translations)
KIKUYU_NAMES = {
    "Genesis": "Kĩambĩrĩria",
    "Exodus": "Woima",
    "Leviticus": "Alawii",
    "Numbers": "Ndari",
    "Deuteronomy": "Gũcookerithia Watho",
    "Joshua": "Joshua",
    "Judges": "Atiirĩrĩri",
    "Ruth": "Ruthu",
    "1 Samuel": "1 Samũeli",
    "2 Samuel": "2 Samũeli",
    "1 Kings": "1 Athamaki",
    "2 Kings": "2 Athamaki",
    "1 Chronicles": "1 Maũndũ ma Matukũ",
    "2 Chronicles": "2 Maũndũ ma Matukũ",
    "Ezra": "Ezira",
    "Nehemiah": "Nehemia",
    "Esther": "Esiteri",
    "Job": "Ayubu",
    "Psalms": "Thaburi",
    "Proverbs": "Thimo",
    "Ecclesiastes": "Mũhubĩri",
    "Song of Solomon": "Rwĩmbo rwa Solomoni",
    "Isaiah": "Isaia",
    "Jeremiah": "Jeremia",
    "Lamentations": "Macakaya",
    "Ezekiel": "Ezekieli",
    "Daniel": "Danieli",
    "Hosea": "Hosea",
    "Joel": "Joeli",
    "Amos": "Amosi",
    "Obadiah": "Obadia",
    "Jonah": "Jona",
    "Micah": "Mika",
    "Nahum": "Nahumu",
    "Habakkuk": "Habakuku",
    "Zephaniah": "Zefania",
    "Haggai": "Hagai",
    "Zechariah": "Zekaria",
    "Malachi": "Malaki",
    "Matthew": "Mathayo",
    "Mark": "Mariko",
    "Luke": "Luka",
    "John": "Johana",
    "Acts": "Atũmwo",
    "Romans": "Aroma",
    "1 Corinthians": "1 Akorintho",
    "2 Corinthians": "2 Akorintho",
    "Galatians": "Agalatia",
    "Ephesians": "Aefeso",
    "Philippians": "Afilipi",
    "Colossians": "Akolosai",
    "1 Thessalonians": "1 Athesalonike",
    "2 Thessalonians": "2 Athesalonike",
    "1 Timothy": "1 Timotheo",
    "2 Timothy": "2 Timotheo",
    "Titus": "Tito",
    "Philemon": "Filemoni",
    "Hebrews": "Ahibrania",
    "James": "Jakubu",
    "1 Peter": "1 Petero",
    "2 Peter": "2 Petero",
    "1 John": "1 Johana",
    "2 John": "2 Johana",
    "3 John": "3 Johana",
    "Jude": "Juda",
    "Revelation": "Kũguũrĩrio",
}


def load_bible_json():
    """Load the Bible structure from JSON file."""
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_bible_structure():
    """Generate the complete Bible structure Python module."""
    try:
        bible_books = load_bible_json()

        # Create the Python file header
        python_code = '''"""
Bible structure module.

This module provides a source of truth for the structure of the Bible,
including book names, chapter counts, and verse counts for each chapter.
This data will be used for validating and organizing the parsed Bible verses.
"""

from typing import Dict, List, Optional, Set, Tuple

# Bible structure data
# This structure contains information about each book in the Bible,
# including the number of chapters and the number of verses in each chapter.
BIBLE_BOOKS = [
'''

        # Process each book
        for book in bible_books:
            book_name = book["book_name"]
            kikuyu_name = KIKUYU_NAMES.get(book_name, book_name)

            python_code += f"""    {{
        "book_name": "{book_name}",
        "kikuyu_name": "{kikuyu_name}",
        "num_chapters": {book["num_chapters"]},
        "chapters": [
"""

            # Add each chapter
            for chapter in book["chapters"]:
                python_code += f'            {{"chapter_no": {chapter["chapter_no"]}, "num_verses": {chapter["num_verses"]}}},\n'

            python_code += """        ]
    },
"""

        # Close the BIBLE_BOOKS list
        python_code += ''']

# Build book name mapping
BOOK_NAME_MAPPING = {book["kikuyu_name"]: book["book_name"] for book in BIBLE_BOOKS}

# Build lookup dictionaries for quick access
CHAPTER_VERSE_COUNTS = {}
for book in BIBLE_BOOKS:
    book_name = book["book_name"]
    CHAPTER_VERSE_COUNTS[book_name] = {}
    for chapter in book["chapters"]:
        CHAPTER_VERSE_COUNTS[book_name][chapter["chapter_no"]] = chapter["num_verses"]


def get_book_by_name(book_name: str) -> Optional[Dict]:
    """
    Get book information by name.

    Args:
        book_name: Name of the book (English)

    Returns:
        Book information dictionary or None if not found
    """
    for book in BIBLE_BOOKS:
        if book["book_name"].lower() == book_name.lower():
            return book
    return None


def get_book_by_kikuyu_name(kikuyu_name: str) -> Optional[Dict]:
    """
    Get book information by Kikuyu name.

    Args:
        kikuyu_name: Kikuyu name of the book

    Returns:
        Book information dictionary or None if not found
    """
    for book in BIBLE_BOOKS:
        if book["kikuyu_name"].lower() == kikuyu_name.lower():
            return book
    return None


def get_verse_count(book_name: str, chapter_no: int) -> Optional[int]:
    """
    Get the number of verses in a chapter.

    Args:
        book_name: Name of the book (English)
        chapter_no: Chapter number

    Returns:
        Number of verses or None if not found
    """
    book_chapters = CHAPTER_VERSE_COUNTS.get(book_name)
    if book_chapters:
        return book_chapters.get(chapter_no)
    return None


def is_valid_reference(book_name: str, chapter_no: int, verse_no: int) -> bool:
    """
    Check if a Bible reference is valid.

    Args:
        book_name: Name of the book (English)
        chapter_no: Chapter number
        verse_no: Verse number

    Returns:
        True if the reference is valid, False otherwise
    """
    verse_count = get_verse_count(book_name, chapter_no)
    if verse_count is None:
        return False
    return 1 <= verse_no <= verse_count


def get_verse_id(book_name: str, chapter_no: int, verse_no: int) -> str:
    """
    Generate a unique ID for a verse.

    Args:
        book_name: Name of the book (English)
        chapter_no: Chapter number
        verse_no: Verse number

    Returns:
        Unique verse ID in the format "Book.Chapter.Verse"
    """
    return f"{book_name}.{chapter_no}.{verse_no}"


def get_all_books() -> List[str]:
    """
    Get a list of all book names (English).

    Returns:
        List of book names
    """
    return [book["book_name"] for book in BIBLE_BOOKS]


def get_all_kikuyu_books() -> List[str]:
    """
    Get a list of all Kikuyu book names.

    Returns:
        List of Kikuyu book names
    """
    return [book["kikuyu_name"] for book in BIBLE_BOOKS]


def get_all_chapter_numbers(book_name: str) -> List[int]:
    """
    Get all chapter numbers for a book.

    Args:
        book_name: Name of the book (English)

    Returns:
        List of chapter numbers
    """
    book = get_book_by_name(book_name)
    if book:
        return [chapter["chapter_no"] for chapter in book["chapters"]]
    return []


def get_all_verse_numbers(book_name: str, chapter_no: int) -> List[int]:
    """
    Get all verse numbers for a chapter.

    Args:
        book_name: Name of the book (English)
        chapter_no: Chapter number

    Returns:
        List of verse numbers
    """
    verse_count = get_verse_count(book_name, chapter_no)
    if verse_count:
        return list(range(1, verse_count + 1))
    return []


def english_to_kikuyu_book_name(english_name: str) -> Optional[str]:
    """
    Convert English book name to Kikuyu book name.

    Args:
        english_name: English book name

    Returns:
        Kikuyu book name or None if not found
    """
    for book in BIBLE_BOOKS:
        if book["book_name"].lower() == english_name.lower():
            return book["kikuyu_name"]
    return None


def kikuyu_to_english_book_name(kikuyu_name: str) -> Optional[str]:
    """
    Convert Kikuyu book name to English book name.

    Args:
        kikuyu_name: Kikuyu book name

    Returns:
        English book name or None if not found
    """
    return BOOK_NAME_MAPPING.get(kikuyu_name)


def get_missing_verses(parsed_verses: Dict[str, Dict[int, Dict[int, str]]],
                       book_name: str) -> List[Tuple[int, int]]:
    """
    Get missing verses for a book in the parsed verses.

    Args:
        parsed_verses: Dictionary of parsed verses
        book_name: Name of the book (English)

    Returns:
        List of (chapter_no, verse_no) tuples for missing verses
    """
    missing_verses = []
    book = get_book_by_name(book_name)

    if not book or book_name not in parsed_verses:
        return missing_verses

    for chapter in book["chapters"]:
        chapter_no = chapter["chapter_no"]
        verse_count = chapter["num_verses"]

        if chapter_no not in parsed_verses[book_name]:
            missing_verses.extend([(chapter_no, verse_no) for verse_no in range(1, verse_count + 1)])
            continue

        parsed_chapter = parsed_verses[book_name][chapter_no]
        for verse_no in range(1, verse_count + 1):
            if verse_no not in parsed_chapter:
                missing_verses.append((chapter_no, verse_no))

    return missing_verses


def get_extra_verses(parsed_verses: Dict[str, Dict[int, Dict[int, str]]],
                     book_name: str) -> List[Tuple[int, int]]:
    """
    Get extra verses in the parsed verses that shouldn't exist.

    Args:
        parsed_verses: Dictionary of parsed verses
        book_name: Name of the book (English)

    Returns:
        List of (chapter_no, verse_no) tuples for extra verses
    """
    extra_verses = []

    if book_name not in parsed_verses:
        return extra_verses

    for chapter_no, verses in parsed_verses[book_name].items():
        for verse_no in verses:
            if not is_valid_reference(book_name, chapter_no, verse_no):
                extra_verses.append((chapter_no, verse_no))

    return extra_verses
'''

        # Write the Python file
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(python_code)

        print(f"Successfully generated {OUTPUT_PATH}")
        return True

    except Exception as e:
        print(f"Error generating Bible structure: {e}")
        return False


if __name__ == "__main__":
    generate_bible_structure()
