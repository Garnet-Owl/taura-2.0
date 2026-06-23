"""
Bible PDF parsing module for the Taura project.

This module extracts text from Kikuyu and English Bible PDFs,
aligns verses between languages, and creates parallel corpora for
training machine translation models.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import pandas as pd

from scripts.preprocessing.structure.bible_structure import (
    BIBLE_BOOKS,
    kikuyu_to_english_book_name,
)

# Ratio bounds for post-extraction quality filtering
_MIN_RATIO = 0.4
_MAX_RATIO = 2.5
_MIN_VERSE_CONTENT_LEN = 15

# Map of Kikuyu headers to standard English names
KIKUYU_BOOK_HEADERS = {
    "Genesis": "Kĩambĩrĩria",
    "Exodus": "Thaama",
    "Leviticus": "Alawii",
    "Numbers": "Ndari",
    "Deuteronomy": "Gũcookerithia",
    "Joshua": "Joshua",
    "Judges": "Atiirĩrĩri",
    "Ruth": "Ruthu",
    "1 Samuel": "1 Samũeli",
    "2 Samuel": "2 Samũeli",
    "1 Kings": "1 Athamaki",
    "2 Kings": "2 Athamaki",
    "1 Chronicles": "1 Maũndũ",
    "2 Chronicles": "2 Maũndũ",
    "Ezra": "Ezara",
    "Nehemiah": "Nehemia",
    "Esther": "Esiteri",
    "Job": "Ayubu",
    "Psalms": "Thaburi",
    "Proverbs": "Thimo",
    "Ecclesiastes": "Kohelethu",
    "Song of Solomon": "Rwĩmbo",
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
    "1 Corinthians": "1 Akorinitho",
    "2 Corinthians": "2 Akorinitho",
    "Galatians": "Agalatia",
    "Ephesians": "Aefeso",
    "Philippians": "Afilipi",
    "Colossians": "Akolosai",
    "1 Thessalonians": "1 Athesalonike",
    "2 Thessalonians": "2 Athesalonike",
    "1 Timothy": "1 Timotheo",
    "2 Timothy": "2 Timotheo",
    "Titus": "Tito",
    "Philemon": "Filemona",
    "Hebrews": "Ahibirania",
    "James": "Jakubu",
    "1 Peter": "1 Petero",
    "2 Peter": "2 Petero",
    "1 John": "1 Johana",
    "2 John": "2 Johana",
    "3 John": "3 Johana",
    "Jude": "Judasi",
    "Revelation": "Kũguũrĩrio",
}


def clean_book_name(s: str) -> str:
    s = s.strip().lower()
    match = re.match(r"^([1-3])\s*(.*)", s)
    if match:
        digit = match.group(1)
        rest = match.group(2)
        rest_cleaned = re.sub(r"[^a-z\u00C0-\u017F\u0100-\u017F]", "", rest)
        return digit + rest_cleaned
    return re.sub(r"[^a-z\u00C0-\u017F\u0100-\u017F]", "", s)


# Build cleaned mappings
CLEAN_KIKUYU_MAP = {}
CLEAN_ENGLISH_MAP = {}
for book in BIBLE_BOOKS:
    cname = book["book_name"]
    CLEAN_KIKUYU_MAP[clean_book_name(book["kikuyu_name"])] = cname
    if cname in KIKUYU_BOOK_HEADERS:
        CLEAN_KIKUYU_MAP[clean_book_name(KIKUYU_BOOK_HEADERS[cname])] = cname
    CLEAN_ENGLISH_MAP[clean_book_name(cname)] = cname

CLEAN_KIKUYU_MAP["1maũndũmamatukũmatene"] = "1 Chronicles"
CLEAN_KIKUYU_MAP["2maũndũmamatukũmatene"] = "2 Chronicles"
CLEAN_KIKUYU_MAP["1maũndũ"] = "1 Chronicles"
CLEAN_KIKUYU_MAP["2maũndũ"] = "2 Chronicles"
CLEAN_ENGLISH_MAP["song"] = "Song of Solomon"
CLEAN_ENGLISH_MAP["psalm"] = "Psalms"
ENG_TO_KIK_BOOK = {book["book_name"]: book["kikuyu_name"] for book in BIBLE_BOOKS}

# Flat sequence of all canonical verses
ALL_VERSES_SEQ = []
for book in BIBLE_BOOKS:
    bname = book["book_name"]
    for ch in book["chapters"]:
        ch_no = ch["chapter_no"]
        v_count = ch["num_verses"]
        for v_no in range(1, v_count + 1):
            ALL_VERSES_SEQ.append((bname, ch_no, v_no))

VERSE_TO_IDX = {ref: idx for idx, ref in enumerate(ALL_VERSES_SEQ)}


def get_next_verse(ref: Tuple[str, int, int]) -> Optional[Tuple[str, int, int]]:
    idx = VERSE_TO_IDX.get(ref)
    if idx is not None and idx + 1 < len(ALL_VERSES_SEQ):
        return ALL_VERSES_SEQ[idx + 1]
    return None


def get_previous_verse(ref: Tuple[str, int, int]) -> Optional[Tuple[str, int, int]]:
    idx = VERSE_TO_IDX.get(ref)
    if idx is not None and idx - 1 >= 0:
        return ALL_VERSES_SEQ[idx - 1]
    return None


HEADER_PATTERN = re.compile(
    r"([1-3]?\s*[a-zA-Z\u00C0-\u017F\u0100-\u017Fʼ\s\(\)-]+?)\s+(\d+)(?::(\d+))?\s+(\d+)\s+([1-3]?\s*[a-zA-Z\u00C0-\u017F\u0100-\u017Fʼ\s\(\)-]+?)\s+(\d+)(?::(\d+))?"
)


def parse_header_text(
    header_text: str, lang: str
) -> Optional[Tuple[str, int, int, str, int, int]]:
    match = HEADER_PATTERN.search(header_text)
    if not match:
        return None

    raw_bk1 = match.group(1)
    ch1 = int(match.group(2))
    v1 = int(match.group(3)) if match.group(3) else 1

    raw_bk2 = match.group(5)
    ch2 = int(match.group(6))
    v2 = int(match.group(7)) if match.group(7) else 1

    bk1 = clean_book_name(raw_bk1)
    bk2 = clean_book_name(raw_bk2)

    map_dict = CLEAN_KIKUYU_MAP if lang == "kikuyu" else CLEAN_ENGLISH_MAP

    canonical_bk1 = map_dict.get(bk1)
    canonical_bk2 = map_dict.get(bk2)

    if not canonical_bk1 or not canonical_bk2:
        return None

    return (canonical_bk1, ch1, v1, canonical_bk2, ch2, v2)


def build_page_ranges(
    pdf_path: str, lang: str, start_page: int
) -> Dict[int, Tuple[Tuple[str, int, int], Tuple[str, int, int]]]:
    doc = fitz.open(pdf_path)
    page_ranges = {}

    for page_idx in range(start_page, len(doc)):
        page = doc[page_idx]
        blocks = page.get_text("blocks")
        header_parsed = None

        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            if y0 < 100:
                header_parsed = parse_header_text(text, lang)
                if header_parsed:
                    break

        if header_parsed:
            canonical_bk1, ch1, v1, canonical_bk2, ch2, v2 = header_parsed
            page_ranges[page_idx] = ((canonical_bk1, ch1, v1), (canonical_bk2, ch2, v2))
        else:
            page_ranges[page_idx] = None

    # Filter out backward jumps and invalid end < start refs
    raw_ranges = {}
    last_valid_idx = -1
    for page_idx in range(start_page, len(doc)):
        r = page_ranges.get(page_idx)
        if r is None:
            raw_ranges[page_idx] = None
            continue
        ref1, ref2 = r
        if ref1 not in VERSE_TO_IDX or ref2 not in VERSE_TO_IDX:
            raw_ranges[page_idx] = None
            continue
        idx1 = VERSE_TO_IDX[ref1]
        idx2 = VERSE_TO_IDX[ref2]
        if idx1 > idx2:
            raw_ranges[page_idx] = None
            continue

        if last_valid_idx != -1:
            prev_end_ref = raw_ranges[last_valid_idx][1]
            prev_end_idx = VERSE_TO_IDX[prev_end_ref]
            if idx1 < prev_end_idx:
                raw_ranges[page_idx] = None
                continue

        raw_ranges[page_idx] = (ref1, ref2)
        last_valid_idx = page_idx

    page_ranges = dict(raw_ranges)

    # Forward propagation
    for page_idx in range(start_page, len(doc)):
        if page_ranges[page_idx] is None:
            prev_idx = page_idx - 1
            if prev_idx >= start_page and page_ranges[prev_idx] is not None:
                _, prev_end = page_ranges[prev_idx]
                next_start = get_next_verse(prev_end)
                if next_start:
                    page_ranges[page_idx] = (next_start, next_start)

    # Backward propagation
    for page_idx in range(len(doc) - 1, start_page - 1, -1):
        if page_idx + 1 < len(doc) and page_ranges[page_idx + 1] is not None:
            next_start, _ = page_ranges[page_idx + 1]
            prev_end = get_previous_verse(next_start)
            if prev_end:
                if page_ranges[page_idx] is None:
                    page_ranges[page_idx] = (prev_end, prev_end)
                else:
                    start_ref, _ = page_ranges[page_idx]
                    page_ranges[page_idx] = (start_ref, prev_end)

    # Equal split for contiguous None blocks
    none_blocks = []
    in_block = False
    start_none = None
    for idx in range(start_page, len(doc)):
        is_none = raw_ranges[idx] is None
        if is_none:
            if not in_block:
                start_none = idx
                in_block = True
        else:
            if in_block:
                none_blocks.append((start_none, idx - 1))
                in_block = False
    if in_block:
        none_blocks.append((start_none, len(doc) - 1))

    for start_none, end_none in none_blocks:
        prev_end_idx = None
        if start_none - 1 >= start_page and page_ranges[start_none - 1] is not None:
            prev_end_ref = page_ranges[start_none - 1][1]
            prev_end_idx = VERSE_TO_IDX[prev_end_ref]

        next_start_idx = None
        if end_none + 1 < len(doc) and page_ranges[end_none + 1] is not None:
            next_start_ref = page_ranges[end_none + 1][0]
            next_start_idx = VERSE_TO_IDX[next_start_ref]

        if prev_end_idx is not None and next_start_idx is not None:
            missing_verses = ALL_VERSES_SEQ[prev_end_idx + 1 : next_start_idx]
            num_pages = end_none - start_none + 1
            if missing_verses:
                verses_per_page = max(1, len(missing_verses) // num_pages)
                for offset, p_idx in enumerate(range(start_none, end_none + 1)):
                    s_i = offset * verses_per_page
                    e_i = (offset + 1) * verses_per_page - 1
                    if p_idx == end_none:
                        e_i = len(missing_verses) - 1
                    page_ranges[p_idx] = (missing_verses[s_i], missing_verses[e_i])

    return page_ranges


def find_next_verse_pos(
    body_text: str, v_no: int, current_pos: int
) -> Optional[re.Match]:
    pattern = re.compile(rf"(?<!\d){v_no}(?!\d)")
    matches = list(pattern.finditer(body_text, current_pos))
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    first_match = matches[0]
    if first_match.start() - current_pos < 300:
        return first_match
    strict_suffix = re.compile(
        r"^\s*[“\"'\‘\“A-Z\u0128\u0168\u00C0-\u00DE\u0100-\u017F]"
    )
    for m in matches:
        if strict_suffix.match(body_text[m.end() :]):
            return m
    return first_match


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF (fitz).
    """
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text
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
    # Measurement / unit stubs that indicate a footnote fragment, not a verse
    measurement_re = re.compile(
        r"""^(?:
          (?:grams?|kg|kilograms?|ounces?|oz|pounds?|lb|liters?|litres?|
             milliliters?|ml|inches?|in|centimeters?|cm|kilometers?|km|miles?|
             cubits?|seah|ephah|hin|shekel)\s+(?:or|is|about|=|≈).*
        | [*†‡§;,]\s*\d[\d:,;\s*†‡§]*  # footnote-only content
        )$""",
        re.VERBOSE | re.IGNORECASE,
    )
    if measurement_re.match(stripped):
        return True
    return False


def parse_pdf_verses(
    pdf_path: str, lang: str, start_page: int
) -> Dict[str, Dict[int, Dict[int, str]]]:
    page_ranges = build_page_ranges(pdf_path, lang, start_page)
    doc = fitz.open(pdf_path)
    parsed_verses = {}

    for page_idx in range(start_page, len(doc)):
        r_range = page_ranges.get(page_idx)
        if not r_range:
            continue

        start_ref, end_ref = r_range
        if start_ref not in VERSE_TO_IDX or end_ref not in VERSE_TO_IDX:
            continue

        start_idx = VERSE_TO_IDX[start_ref]
        end_idx = VERSE_TO_IDX[end_ref]
        page_verses = ALL_VERSES_SEQ[start_idx : end_idx + 1]

        page = doc[page_idx]
        blocks = page.get_text("blocks")
        body_blocks = []
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            if y1 >= 71 and y0 < 719:
                body_blocks.append(text)
        body_text = " ".join(body_blocks)
        body_text = re.sub(r"\s+", " ", body_text).strip()

        current_pos = 0
        verse_positions = []

        for bname, ch_no, v_no in page_verses:
            match = None
            if v_no == 1:
                # Start of a new chapter. Try patterns and pick the earliest match.
                pattern_strict = re.compile(
                    rf"(?<!\d){ch_no}(?!\d)[^0-9]{{1,100}}(?<!\d)1(?!\d)\s*[“\"'\‘\“A-Z\u0128\u0168\u00C0-\u00DE\u0100-\u017F]"
                )
                pattern_relaxed = re.compile(
                    rf"(?<!\d){ch_no}(?!\d)[^0-9]{{1,100}}(?<!\d)1(?!\d)"
                )
                pattern_one = re.compile(
                    r"(?<!\d)1(?!\d)\s*[“\"'\‘\“A-Z\u0128\u0168\u00C0-\u00DE\u0100-\u017F]"
                )
                pattern_one_relaxed = re.compile(r"(?<!\d)1(?!\d)")

                candidates = []
                for pat in [
                    pattern_strict,
                    pattern_relaxed,
                    pattern_one,
                    pattern_one_relaxed,
                ]:
                    m = pat.search(body_text, current_pos)
                    if m:
                        candidates.append(m)
                if candidates:
                    match = min(candidates, key=lambda x: x.start())
            else:
                match = find_next_verse_pos(body_text, v_no, current_pos)

            if match:
                verse_positions.append(
                    {
                        "ref": (bname, ch_no, v_no),
                        "start_pos": match.end(),
                        "marker_pos": match.start(),
                    }
                )
                current_pos = match.end()
            else:
                verse_positions.append(
                    {
                        "ref": (bname, ch_no, v_no),
                        "start_pos": current_pos,
                        "marker_pos": current_pos,
                        "missing": True,
                    }
                )

        # Set end_pos and yield text
        for idx in range(len(verse_positions)):
            curr = verse_positions[idx]
            if idx + 1 < len(verse_positions):
                curr["end_pos"] = verse_positions[idx + 1]["marker_pos"]
            else:
                curr["end_pos"] = len(body_text)

            ref = curr["ref"]
            bname, ch_no, v_no = ref
            v_text = body_text[curr["start_pos"] : curr["end_pos"]].strip()

            if lang == "english":
                v_text = _clean_english_verse(v_text)
                if _is_footnote_only(v_text):
                    v_text = ""

            ref_book = ENG_TO_KIK_BOOK[bname] if lang == "kikuyu" else bname
            if ref_book not in parsed_verses:
                parsed_verses[ref_book] = {}
            if ch_no not in parsed_verses[ref_book]:
                parsed_verses[ref_book][ch_no] = {}

            parsed_verses[ref_book][ch_no][v_no] = v_text

    return parsed_verses


def align_verses(kikuyu_dict: Dict, english_dict: Dict) -> List[Tuple[str, str, str]]:
    aligned_verses = []

    # Iterate through Kikuyu books
    for kikuyu_book, chapters in kikuyu_dict.items():
        english_book = kikuyu_to_english_book_name(kikuyu_book)
        if english_book and english_book in english_dict:
            for chapter_num, verses in chapters.items():
                if chapter_num in english_dict[english_book]:
                    for verse_num, kikuyu_text in verses.items():
                        if verse_num in english_dict[english_book][chapter_num]:
                            english_text = english_dict[english_book][chapter_num][
                                verse_num
                            ]

                            if not kikuyu_text.strip() or not english_text.strip():
                                continue

                            ratio = len(kikuyu_text) / max(len(english_text), 1)
                            if ratio < _MIN_RATIO or ratio > _MAX_RATIO:
                                continue

                            reference = f"{kikuyu_book} {chapter_num}:{verse_num}"
                            aligned_verses.append(
                                (reference, kikuyu_text, english_text)
                            )
    return aligned_verses


def create_dataset(
    aligned_verses: List[Tuple[str, str, str]], max_examples: Optional[int] = None
) -> pd.DataFrame:
    if max_examples is not None:
        aligned_verses = aligned_verses[:max_examples]
    df = pd.DataFrame(aligned_verses, columns=["Reference", "Kikuyu", "English"])
    return df


def process_bible_texts(
    kikuyu_pdf_path: str, english_pdf_path: str, max_examples: Optional[int] = None
) -> pd.DataFrame:
    print(f"Extracting and parsing Kikuyu PDF {kikuyu_pdf_path}...")
    kikuyu_dict = parse_pdf_verses(kikuyu_pdf_path, "kikuyu", start_page=3)

    print(f"Extracting and parsing English PDF {english_pdf_path}...")
    english_dict = parse_pdf_verses(english_pdf_path, "english", start_page=6)

    print("Aligning verses...")
    aligned_verses = align_verses(kikuyu_dict, english_dict)

    print(f"Aligned {len(aligned_verses)} verse pairs.")
    df = create_dataset(aligned_verses, max_examples)
    return df


def save_bible_dataset(df: pd.DataFrame, output_path: Optional[str] = None) -> None:
    if output_path is None:
        output_path = Path("data/processed/bible_parallel.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved Bible dataset to {output_path}")


if __name__ == "__main__":
    kikuyu_pdf = "data/Kikuyu_Bible_all.pdf"
    english_pdf = "data/English_Bible_all.pdf"
    df = process_bible_texts(kikuyu_pdf, english_pdf)
    save_bible_dataset(df)
