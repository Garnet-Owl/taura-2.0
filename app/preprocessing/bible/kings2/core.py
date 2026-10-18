"""
Core definitions and structural specifications for the Book of 2 Kings.
"""

from typing import Dict, List, Tuple


class Kings2Extractor:
    ENGLISH_NAME = "2 Kings"
    KIKUYU_NAME = "2 Athamaki"

    KIKUYU_START_PAGE = 397
    KIKUYU_END_PAGE = 431
    ENGLISH_START_PAGE = 394
    ENGLISH_END_PAGE = 426

    CHAPTER_VERSES_MAP = {
        1: 18, 2: 25, 3: 27, 4: 44, 5: 27, 6: 33, 7: 20, 8: 29, 9: 37, 10: 36, 11: 21, 12: 21, 13: 25, 14: 29, 15: 38, 16: 20, 17: 41, 18: 37, 19: 37, 20: 21, 21: 26, 22: 20, 23: 37, 24: 20, 25: 30,
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
