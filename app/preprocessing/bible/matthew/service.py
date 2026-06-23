"""
Implementation of the Book of Matthew (Mathayo) extractor.
"""

import re
from typing import Dict, Optional
import pandas as pd
import fitz

from app.preprocessing.bible.base.core import (
    BaseBibleParser,
    VERSE_TO_IDX,
    ALL_VERSES_SEQ,
)
from app.preprocessing.bible.matthew.core import (
    MatthewExtractor as MatthewExtractorBase,
)


class MatthewExtractor(BaseBibleParser, MatthewExtractorBase):
    """
    Extractor to parse, clean, and align the Book of Matthew.
    """

    def __init__(self):
        BaseBibleParser.__init__(self)

    def parse_book_verses(self, pdf_path: str, lang: str) -> Dict[int, Dict[int, str]]:
        """
        Parses pages of the PDF corresponding to Matthew.
        Returns:
            Dict of {chapter_no: {verse_no: verse_text}}
        """
        start_page = (
            self.KIKUYU_START_PAGE if lang == "kikuyu" else self.ENGLISH_START_PAGE
        )
        end_page = self.KIKUYU_END_PAGE if lang == "kikuyu" else self.ENGLISH_END_PAGE

        # Build page ranges specifically for Matthew
        page_ranges = self.build_page_ranges(pdf_path, lang, start_page, end_page)
        doc = fitz.open(pdf_path)
        parsed_verses = {}

        target_book = "Matthew"

        for page_idx in range(start_page, end_page + 1):
            r_range = page_ranges.get(page_idx)
            if not r_range:
                continue

            start_ref, end_ref = r_range

            # Clamp the start and end refs to Matthew to prevent leakage
            start_ref_clamped = start_ref
            if start_ref[0] != target_book:
                start_ref_clamped = (target_book, 1, 1)
            end_ref_clamped = end_ref
            if end_ref[0] != target_book:
                end_ref_clamped = (target_book, 28, 20)

            if (
                start_ref_clamped not in VERSE_TO_IDX
                or end_ref_clamped not in VERSE_TO_IDX
            ):
                continue

            start_idx = VERSE_TO_IDX[start_ref_clamped]
            end_idx = VERSE_TO_IDX[end_ref_clamped]

            page_verses = [
                ref
                for ref in ALL_VERSES_SEQ[start_idx : end_idx + 1]
                if ref[0] == target_book
            ]

            if not page_verses:
                continue

            page = doc[page_idx]
            body_text = self.extract_page_body_text(page)

            current_pos = 0
            verse_positions = []

            for bname, ch_no, v_no in page_verses:
                match = None
                if v_no == 1:
                    # Chapter start pattern:
                    # e.g., "2 1 Now when..." or "26 1 Rĩrĩa..." or "1 1 The book..."
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
                    match = self.find_next_verse_pos(body_text, v_no, current_pos)

                if match:
                    verse_positions.append(
                        {
                            "ref": (ch_no, v_no),
                            "start_pos": match.end(),
                            "marker_pos": match.start(),
                        }
                    )
                    current_pos = match.end()
                else:
                    verse_positions.append(
                        {
                            "ref": (ch_no, v_no),
                            "start_pos": current_pos,
                            "marker_pos": current_pos,
                            "missing": True,
                        }
                    )

            # Set end_pos and yield text
            for idx in range(len(verse_positions)):
                curr = verse_positions[idx]
                if curr.get("missing"):
                    curr["start_pos"] = 0
                    curr["end_pos"] = 0
                else:
                    # Find the next actually matched verse to determine where this one ends
                    next_matched = None
                    for next_curr in verse_positions[idx + 1 :]:
                        if not next_curr.get("missing"):
                            next_matched = next_curr
                            break

                    if next_matched:
                        curr["end_pos"] = next_matched["marker_pos"]
                    else:
                        curr["end_pos"] = len(body_text)

                ch_no, v_no = curr["ref"]
                v_text = body_text[curr["start_pos"] : curr["end_pos"]].strip()

                if lang == "english":
                    v_text = self.clean_english_verse(v_text)
                    if self.is_footnote_only(v_text):
                        v_text = ""

                if ch_no not in parsed_verses:
                    parsed_verses[ch_no] = {}
                parsed_verses[ch_no][v_no] = v_text

        return parsed_verses

    def find_next_verse_pos(
        self, body_text: str, v_no: int, current_pos: int
    ) -> Optional[re.Match]:
        """
        Regex logic to locate a verse marker on the page body.
        """
        pattern = re.compile(rf"(?<!\d){v_no}(?!\d)")
        matches = list(pattern.finditer(body_text, current_pos))
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]

        first_match = matches[0]
        # If the match is close to current position, it is very likely the verse number
        if first_match.start() - current_pos < 300:
            return first_match

        # Match starting with capital letters, quotes, etc.
        strict_suffix = re.compile(
            r"^\s*[“\"'\‘\“A-Z\u0128\u0168\u00C0-\u00DE\u0100-\u017F]"
        )
        for m in matches:
            if strict_suffix.match(body_text[m.end() :]):
                return m
        return first_match

    def extract_and_align(
        self, kikuyu_pdf_path: str, english_pdf_path: str
    ) -> pd.DataFrame:
        """
        Extracts verses from both PDFs and aligns them.
        """
        kik_data = self.parse_book_verses(kikuyu_pdf_path, "kikuyu")
        eng_data = self.parse_book_verses(english_pdf_path, "english")

        # Run validation
        kik_missing, kik_empty = self.validate_extracted_verses(kik_data)
        eng_missing, eng_empty = self.validate_extracted_verses(eng_data)

        print("Extraction Validation for Matthew:")
        print(f"Kikuyu missing verses: {len(kik_missing)} / empty: {len(kik_empty)}")
        print(f"English missing verses: {len(eng_missing)} / empty: {len(eng_empty)}")

        aligned_verses = []
        for ch, verses in self.CHAPTER_VERSES_MAP.items():
            k_ch = kik_data.get(ch, {})
            e_ch = eng_data.get(ch, {})
            for v in range(1, verses + 1):
                k_text = k_ch.get(v, "").strip()
                e_text = e_ch.get(v, "").strip()

                # Align if both exist and are not empty
                if k_text and e_text:
                    ref = f"Matthew {ch}:{v}"
                    aligned_verses.append((ref, k_text, e_text))

        df = pd.DataFrame(aligned_verses, columns=["Reference", "Kikuyu", "English"])
        return df
