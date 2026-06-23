"""
Implementation of the Book of Psalms extractor.
"""

import re
from typing import Dict, List, Optional, Tuple, Union

import fitz
import pandas as pd

from app.preprocessing.bible.base.core import (
    ALL_VERSES_SEQ,
    BaseBibleParser,
    PatternConfig,
    VERSE_TO_IDX,
)
from app.preprocessing.bible.psalms.core import PsalmsExtractor as PsalmsExtractorBase

_UPPER = r"[\"''A-Z\u00C0-\u017F]"


class PsalmsExtractor(BaseBibleParser, PsalmsExtractorBase):
    """
    Extractor to parse, clean, and align the Book of Psalms.
    """

    def __init__(self):
        PsalmsExtractorBase.__init__(self)
        self.pattern_config = PatternConfig(
            self._default_patterns(), ignored_fonts=["Italic"]
        )
        BaseBibleParser.__init__(self, self.pattern_config)

    @staticmethod
    def _default_patterns() -> Dict[
        str, Dict[str, Union[re.Pattern, callable, List[re.Pattern]]]
    ]:
        upper = _UPPER
        return {
            "verse_marker_strict": {"pattern": re.compile(r"^\s*" + upper)},
            "footnote_measurement": {
                "pattern": re.compile(
                    r"""^(?:
                      (?:grams?|kg|kilograms?|ounces?|oz|pounds?|lb|liters?|litres?|
                         milliliters?|ml|inches?|in|centimeters?|cm|kilometers?|km|miles?|
                         cubits?|seah|ephah|hin|shekel)\s+(?:or|is|about|=|approx).*
                    | [*†‡§;,]\s*\d[\d:,;\s*†‡§]*
                    )$""",
                    re.VERBOSE | re.IGNORECASE,
                )
            },
            "english_cross_ref": {
                "pattern": [
                    re.compile(r"[*†‡§]\s*\d+:\d+"),
                    re.compile(r"[*†‡§]\s*\d+"),
                    re.compile(r"(?:^|\s)[;,]\s*\d+:\d+"),
                    re.compile(r"^\)\s*\.\s*"),
                ]
            },
        }

    def parse_book_verses(self, pdf_path: str, lang: str) -> Dict[int, Dict[int, str]]:
        start_page = (
            self.KIKUYU_START_PAGE if lang == "kikuyu" else self.ENGLISH_START_PAGE
        )
        end_page = self.KIKUYU_END_PAGE if lang == "kikuyu" else self.ENGLISH_END_PAGE

        page_ranges = self.build_page_ranges(pdf_path, lang, start_page, end_page)
        doc = fitz.open(pdf_path)
        parsed_verses = {}
        target_book = "Psalms"

        for page_idx in range(start_page, end_page + 1):
            r_range = page_ranges.get(page_idx)
            if not r_range:
                continue

            clamped_range = self._get_clamped_page_range(r_range, target_book)
            if not clamped_range:
                continue

            start_ref_clamped, end_ref_clamped = clamped_range
            page_verses = self._get_page_verses(
                start_ref_clamped, end_ref_clamped, target_book
            )
            if not page_verses:
                continue

            body_text = self.extract_page_body_text(doc[page_idx], lang)
            verse_positions = self._find_verse_positions(body_text, page_verses)
            self._append_leading_continuation(
                body_text, verse_positions, lang, parsed_verses
            )
            self._extract_and_clean_verses(
                body_text, verse_positions, lang, parsed_verses
            )

        return parsed_verses

    def _get_clamped_page_range(
        self,
        r_range: Tuple[Tuple[str, int, int], Tuple[str, int, int]],
        target_book: str,
    ) -> Optional[Tuple[Tuple[str, int, int], Tuple[str, int, int]]]:
        start_ref, end_ref = r_range
        start_ref_clamped = (
            start_ref if start_ref[0] == target_book else (target_book, 1, 1)
        )
        end_ref_clamped = (
            end_ref if end_ref[0] == target_book else (target_book, 150, 6)
        )
        if start_ref_clamped not in VERSE_TO_IDX or end_ref_clamped not in VERSE_TO_IDX:
            return None
        return start_ref_clamped, end_ref_clamped

    def _get_page_verses(
        self,
        start_ref: Tuple[str, int, int],
        end_ref: Tuple[str, int, int],
        target_book: str,
    ) -> List[Tuple[str, int, int]]:
        start_idx = VERSE_TO_IDX[start_ref]
        end_idx = VERSE_TO_IDX[end_ref]
        return [
            ref
            for ref in ALL_VERSES_SEQ[start_idx : end_idx + 1]
            if ref[0] == target_book
        ]

    def _find_verse_positions(
        self, body_text: str, page_verses: List[Tuple[str, int, int]]
    ) -> List[dict]:
        current_pos = 0
        verse_positions = []

        for bname, ch_no, v_no in page_verses:
            if v_no == 1:
                match = self._locate_verse_one(body_text, ch_no, current_pos)
            else:
                match = self.find_next_verse_pos(body_text, v_no, current_pos)

            if match:
                if v_no == 1:
                    r_idx = match.group().rfind("1")
                    start_pos = match.start() + r_idx + 1
                else:
                    start_pos = match.end()
                verse_positions.append(
                    {
                        "ref": (ch_no, v_no),
                        "start_pos": start_pos,
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
        return verse_positions

    def _locate_verse_one(
        self, body_text: str, ch_no: int, current_pos: int
    ) -> Optional[re.Match]:
        upper = _UPPER
        pattern_strict = re.compile(
            rf"(?<!\d){ch_no}(?!\d)[^0-9]{{1,100}}(?<!\d)1(?!\d)\s*{upper}"
        )
        pattern_relaxed = re.compile(
            rf"(?<!\d){ch_no}(?!\d)[^0-9]{{1,100}}(?<!\d)1(?!\d)"
        )
        pattern_one = re.compile(rf"(?<!\d)1(?!\d)\s*{upper}")
        pattern_one_relaxed = re.compile(r"(?<!\d)1(?!\d)")

        candidates = []
        for pat in [pattern_strict, pattern_relaxed, pattern_one, pattern_one_relaxed]:
            m = pat.search(body_text, current_pos)
            if m:
                candidates.append(m)
        if candidates:
            return min(candidates, key=lambda x: x.start())
        return None

    def _extract_and_clean_verses(
        self,
        body_text: str,
        verse_positions: List[dict],
        lang: str,
        parsed_verses: dict,
    ) -> None:
        for idx in range(len(verse_positions)):
            curr = verse_positions[idx]
            if curr.get("missing"):
                curr["start_pos"] = 0
                curr["end_pos"] = 0
            else:
                next_matched = None
                for next_curr in verse_positions[idx + 1 :]:
                    if not next_curr.get("missing"):
                        next_matched = next_curr
                        break
                curr["end_pos"] = (
                    next_matched["marker_pos"] if next_matched else len(body_text)
                )

            ch_no, v_no = curr["ref"]
            v_text = body_text[curr["start_pos"] : curr["end_pos"]].strip()

            if lang == "english":
                v_text = self.clean_english_verse(v_text)
                if self.is_footnote_only(v_text):
                    v_text = ""

            if ch_no not in parsed_verses:
                parsed_verses[ch_no] = {}
            parsed_verses[ch_no][v_no] = v_text

    def find_next_verse_pos(
        self, body_text: str, v_no: int, current_pos: int
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

        strict_pattern_info = (
            self.config.patterns.get("verse_marker_strict") if self.config else None
        )
        strict_suffix = (
            strict_pattern_info.get("pattern")
            if strict_pattern_info
            else re.compile(r"^\s*" + _UPPER)
        )
        for m in matches:
            if strict_suffix.match(body_text[m.end() :]):
                return m
        return first_match

    def extract_and_align(
        self, kikuyu_pdf_path: str, english_pdf_path: str
    ) -> pd.DataFrame:
        kik_data = self.parse_book_verses(kikuyu_pdf_path, "kikuyu")
        eng_data = self.parse_book_verses(english_pdf_path, "english")

        kik_missing, kik_empty = self.validate_extracted_verses(kik_data)
        eng_missing, eng_empty = self.validate_extracted_verses(eng_data)

        print("Extraction Validation for Psalms:")
        print(f"Kikuyu missing verses: {len(kik_missing)} / empty: {len(kik_empty)}")
        print(f"English missing verses: {len(eng_missing)} / empty: {len(eng_empty)}")

        aligned_verses = []
        for ch, verses in self.CHAPTER_VERSES_MAP.items():
            k_ch = kik_data.get(ch, {})
            e_ch = eng_data.get(ch, {})
            for v in range(1, verses + 1):
                k_text = k_ch.get(v, "").strip()
                e_text = e_ch.get(v, "").strip()
                if k_text and e_text:
                    ref = f"Psalms {ch}:{v}"
                    aligned_verses.append((ref, k_text, e_text))

        return pd.DataFrame(aligned_verses, columns=["Reference", "Kikuyu", "English"])
