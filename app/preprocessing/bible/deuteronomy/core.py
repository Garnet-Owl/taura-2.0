"""
Core definitions and structural specifications for the Book of Deuteronomy.
"""

from typing import Dict, List, Tuple


class DeuteronomyExtractor:
    ENGLISH_NAME = "Deuteronomy"
    KIKUYU_NAME = "Gũcookerithia"

    KIKUYU_START_PAGE = 192
    KIKUYU_END_PAGE = 232
    ENGLISH_START_PAGE = 193
    ENGLISH_END_PAGE = 233

    CHAPTER_VERSES_MAP = {
        1: 46, 2: 37, 3: 29, 4: 49, 5: 33, 6: 25, 7: 26, 8: 20, 9: 29, 10: 22,
        11: 32, 12: 32, 13: 18, 14: 29, 15: 23, 16: 22, 17: 20, 18: 22, 19: 21, 20: 20,
        21: 23, 22: 30, 23: 25, 24: 22, 25: 19, 26: 19, 27: 26, 28: 68, 29: 29, 30: 20,
        31: 30, 32: 52, 33: 29, 34: 12,
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
