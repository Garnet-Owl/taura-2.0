"""
Core definitions and structural specifications for the Book of 1 Corinthians.
"""

from typing import Dict, List, Tuple


class Corinthians1Extractor:
    ENGLISH_NAME = "1 Corinthians"
    KIKUYU_NAME = "1 Akorinitho"

    KIKUYU_START_PAGE = 1368
    KIKUYU_END_PAGE = 1383
    ENGLISH_START_PAGE = 1450
    ENGLISH_END_PAGE = 1464

    CHAPTER_VERSES_MAP = {
        1: 31,
        2: 16,
        3: 23,
        4: 21,
        5: 13,
        6: 20,
        7: 40,
        8: 13,
        9: 27,
        10: 33,
        11: 34,
        12: 31,
        13: 13,
        14: 40,
        15: 58,
        16: 24,
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
