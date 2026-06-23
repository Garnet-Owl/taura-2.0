"""
Core definitions and structural specifications for the Book of Philippians.
"""

from typing import Dict, List, Tuple


class PhilippiansExtractor:
    ENGLISH_NAME = "Philippians"
    KIKUYU_NAME = "Afilipi"

    KIKUYU_START_PAGE = 1407
    KIKUYU_END_PAGE = 1411
    ENGLISH_START_PAGE = 1487
    ENGLISH_END_PAGE = 1490

    CHAPTER_VERSES_MAP = {
        1: 30,
        2: 30,
        3: 21,
        4: 23,
    }

    @property
    def total_verses(self) -> int:
        return sum(self.CHAPTER_VERSES_MAP.values())

    def get_expected_verses(self) -> List[Tuple[int, int]]:
        expected = []
        for ch, max_v in self.CHAPTER_VERSES_MAP.items():
            for v in range(1, max_v + 1):
                expected.append((ch, v))
        return expected

    def validate_extracted_verses(
        self, parsed_data: Dict[int, Dict[int, str]]
    ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        missing = []
        empty = []
        for ch, max_v in self.CHAPTER_VERSES_MAP.items():
            ch_data = parsed_data.get(ch, {})
            for v in range(1, max_v + 1):
                if v not in ch_data:
                    missing.append((ch, v))
                elif not ch_data[v].strip():
                    empty.append((ch, v))
        return missing, empty
