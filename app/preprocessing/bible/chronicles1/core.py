"""
Core definitions and structural specifications for the Book of 1 Chronicles.
"""

from typing import Dict, List, Tuple


class Chronicles1Extractor:
    ENGLISH_NAME = "1 Chronicles"
    KIKUYU_NAME = "1 Maũndũ"

    KIKUYU_START_PAGE = 432
    KIKUYU_END_PAGE = 470
    ENGLISH_START_PAGE = 427
    ENGLISH_END_PAGE = 458

    CHAPTER_VERSES_MAP = {
        1: 54, 2: 55, 3: 24, 4: 43, 5: 26, 6: 81, 7: 40, 8: 40, 9: 44, 10: 14, 11: 47, 12: 40, 13: 14, 14: 17, 15: 29, 16: 43, 17: 27, 18: 17, 19: 19, 20: 8, 21: 30, 22: 19, 23: 32, 24: 31, 25: 31, 26: 32, 27: 34, 28: 21, 29: 30,
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
