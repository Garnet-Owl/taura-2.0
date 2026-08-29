"""
Core definitions and structural specifications for the Book of Exodus.
"""

from typing import Dict, List, Tuple


class ExodusExtractor:
    ENGLISH_NAME = "Exodus"
    KIKUYU_NAME = "Thaama"

    KIKUYU_START_PAGE = 63
    KIKUYU_END_PAGE = 108
    ENGLISH_START_PAGE = 62
    ENGLISH_END_PAGE = 108

    CHAPTER_VERSES_MAP = {
        1: 22, 2: 25, 3: 22, 4: 31, 5: 23, 6: 30, 7: 25, 8: 32, 9: 35, 10: 29,
        11: 10, 12: 51, 13: 22, 14: 31, 15: 27, 16: 36, 17: 16, 18: 27, 19: 25,
        20: 26, 21: 36, 22: 31, 23: 33, 24: 18, 25: 40, 26: 37, 27: 21, 28: 43,
        29: 46, 30: 38, 31: 18, 32: 35, 33: 23, 34: 35, 35: 35, 36: 38, 37: 29,
        38: 31, 39: 43, 40: 38,
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
