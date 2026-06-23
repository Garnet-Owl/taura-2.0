"""
Base Bible parser module containing shared structures, models, and parsing utilities.
"""

import re
from typing import Dict, List, Optional, Tuple, Union

import fitz  # PyMuPDF

from scripts.preprocessing.structure.bible_structure import (
    BIBLE_BOOKS,
    kikuyu_to_english_book_name,
)

# Quality filtering constants (disabled by default, set to None)
MIN_RATIO = None
MAX_RATIO = None
MIN_VERSE_CONTENT_LEN = None


# Kikuyu headers mapped to English names
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


class PatternConfig:
    def __init__(
        self,
        patterns: Dict[str, Dict[str, Union[re.Pattern, callable]]],
        ignored_fonts: Optional[List[str]] = None,
    ):
        """
        Initialize PatternConfig with a dictionary of patterns.
        Each pattern is a dictionary with:
            - 'pattern': compiled regex pattern or list of patterns
            - 'converter': a callable that converts/modifies matches (optional)
        """
        self.patterns = patterns
        self.ignored_fonts = ignored_fonts or []


class BaseBibleParser:
    """
    Base class containing common structures, algorithms, and configuration
    for Bible PDF parsing.
    """

    def __init__(self, config: Optional[PatternConfig] = None):
        self.config = config
        self.min_ratio = MIN_RATIO
        self.max_ratio = MAX_RATIO
        self.min_verse_content_len = MIN_VERSE_CONTENT_LEN

    def parse_page_header(
        self, header_text: str, lang: str
    ) -> Optional[Tuple[str, int, int, str, int, int]]:
        """
        Parses page header text to extract verse boundaries.
        """
        if self.config and "header" in self.config.patterns:
            patterns_info = self.config.patterns["header"]
            pattern = patterns_info.get("pattern")
            converter = patterns_info.get("converter")
            if pattern:
                match = pattern.search(header_text)
                if match and converter:
                    return converter(match, lang)
        return parse_header_text(header_text, lang)

    def build_page_ranges(
        self, pdf_path: str, lang: str, start_page: int, end_page: Optional[int] = None
    ) -> Dict[int, Tuple[Tuple[str, int, int], Tuple[str, int, int]]]:
        """
        Calculates verse ranges for each page in the PDF by reading page headers.
        """
        doc = fitz.open(pdf_path)
        page_ranges = {}
        last_page = end_page if end_page is not None else len(doc) - 1

        for page_idx in range(start_page, last_page + 1):
            page = doc[page_idx]
            blocks = page.get_text("blocks")
            header_parsed = None

            for b in blocks:
                x0, y0, x1, y1, text, block_no, block_type = b
                if y0 < 100:
                    header_parsed = self.parse_page_header(text, lang)
                    if header_parsed:
                        break

            if header_parsed:
                canonical_bk1, ch1, v1, canonical_bk2, ch2, v2 = header_parsed
                page_ranges[page_idx] = (
                    (canonical_bk1, ch1, v1),
                    (canonical_bk2, ch2, v2),
                )
            else:
                page_ranges[page_idx] = None

        # Filter out backward jumps and invalid end < start refs
        raw_ranges = {}
        last_valid_idx = -1
        for page_idx in range(start_page, last_page + 1):
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
        for page_idx in range(start_page, last_page + 1):
            if page_ranges[page_idx] is None:
                prev_idx = page_idx - 1
                if prev_idx >= start_page and page_ranges[prev_idx] is not None:
                    _, prev_end = page_ranges[prev_idx]
                    next_start = get_next_verse(prev_end)
                    if next_start:
                        page_ranges[page_idx] = (next_start, next_start)

        # Backward propagation
        for page_idx in range(last_page, start_page - 1, -1):
            if page_idx + 1 <= last_page and page_ranges.get(page_idx + 1) is not None:
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
        for idx in range(start_page, last_page + 1):
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
            none_blocks.append((start_none, last_page))

        for start_none, end_none in none_blocks:
            prev_end_idx = None
            if start_none - 1 >= start_page and page_ranges[start_none - 1] is not None:
                prev_end_ref = page_ranges[start_none - 1][1]
                prev_end_idx = VERSE_TO_IDX[prev_end_ref]

            next_start_idx = None
            if end_none + 1 <= last_page and page_ranges.get(end_none + 1) is not None:
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

    def extract_page_body_text(self, page: fitz.Page, lang: str = "kikuyu") -> str:
        """
        Extracts body text from a page, filtering at the line level:
          - Header lines (ly1 < 71) are discarded.
          - Footer lines (ly0 >= 745) are discarded.
          - Bottom-region lines (ly0 > 650) with no span whose font size >= 10.0
            are discarded (main body is 12pt; footnotes/cross-refs are ~9pt).
          - Spans whose font name matches an ignored_fonts entry are dropped
            (only applied for Kikuyu; English italic marks disputed passages).
        """
        blocks = page.get_text("dict")["blocks"]
        body_blocks = []
        ignored_fonts = (
            (self.config.ignored_fonts if self.config else [])
            if lang == "kikuyu"
            else []
        )

        for b in blocks:
            if "lines" not in b:
                continue
            block_lines = []
            for line in b["lines"]:
                ly0, ly1 = line["bbox"][1], line["bbox"][3]
                if ly1 < 71:
                    continue
                if ly0 >= 745:
                    continue
                if ly0 > 650:
                    has_main_text = any(
                        s["size"] >= 10.0 and re.search(r"[A-Za-z0-9]", s["text"])
                        for s in line["spans"]
                    )
                    if not has_main_text:
                        continue
                line_spans = []
                for s in line["spans"]:
                    if ignored_fonts:
                        font_name = s["font"]
                        if any(
                            ign.lower() in font_name.lower() for ign in ignored_fonts
                        ):
                            continue
                    line_spans.append(s["text"])
                if line_spans:
                    block_lines.append("".join(line_spans))
            if block_lines:
                body_blocks.append("\n".join(block_lines))

        body_text = " ".join(body_blocks)
        return re.sub(r"\s+", " ", body_text).strip()

    def clean_english_verse(self, text: str) -> str:
        """Strip footnote markers and measurement stubs from an English verse."""
        if self.config and "english_cross_ref" in self.config.patterns:
            patterns_info = self.config.patterns["english_cross_ref"]
            pattern = patterns_info.get("pattern")
            converter = patterns_info.get("converter")
            if isinstance(pattern, list):
                for pat in pattern:
                    text = pat.sub("", text)
            elif pattern:
                text = pattern.sub("", text)
            if converter:
                text = converter(text)
            return text.strip()

        # Remove inline cross-reference markers like * 7:7  † 12:3  ‡ 9:4
        text = re.sub(r"[*†‡§]\s*\d+:\d+", "", text)
        text = re.sub(r"[*†‡§]\s*\d+", "", text)
        # Remove lone reference strings at line boundaries e.g. "  ; 18:18"
        text = re.sub(r"(?:^|\s)[;,]\s*\d+:\d+", "", text)
        # Remove parenthetical commentary that starts with a close paren
        text = re.sub(r"^\)\s*\.\s*", "", text.strip())
        return text.strip()

    def is_footnote_only(self, text: str) -> bool:
        """Return True if the text looks like a footnote stub, not a verse."""
        stripped = text.strip()
        if not stripped:
            return True
        if (
            self.min_verse_content_len is not None
            and len(stripped) < self.min_verse_content_len
        ):
            return True

        if self.config and "footnote_measurement" in self.config.patterns:
            patterns_info = self.config.patterns["footnote_measurement"]
            pattern = patterns_info.get("pattern")
            if pattern and pattern.match(stripped):
                return True
            return False

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

    def align_verses(
        self, kikuyu_dict: Dict, english_dict: Dict
    ) -> List[Tuple[str, str, str]]:
        """
        Aligns verses between Kikuyu and English dictionaries.
        """
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
                                if (
                                    self.min_ratio is not None
                                    and ratio < self.min_ratio
                                ):
                                    continue
                                if (
                                    self.max_ratio is not None
                                    and ratio > self.max_ratio
                                ):
                                    continue

                                reference = f"{kikuyu_book} {chapter_num}:{verse_num}"
                                aligned_verses.append(
                                    (reference, kikuyu_text, english_text)
                                )
        return aligned_verses
