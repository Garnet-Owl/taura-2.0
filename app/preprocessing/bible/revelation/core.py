"""
Core definitions and structural specifications for the Book of Revelation.
"""

from typing import Dict, List, Tuple


class RevelationExtractor:
    ENGLISH_NAME = "Revelation"
    KIKUYU_NAME = "Kũguũrĩrio"

    KIKUYU_START_PAGE = 1467
    KIKUYU_END_PAGE = 1488
    ENGLISH_START_PAGE = 1543
    ENGLISH_END_PAGE = 1560

    CHAPTER_VERSES_MAP = {
        1: 20,
        2: 29,
        3: 22,
        4: 11,
        5: 14,
        6: 17,
        7: 17,
        8: 13,
        9: 21,
        10: 11,
        11: 19,
        12: 17,
        13: 18,
        14: 20,
        15: 8,
        16: 21,
        17: 18,
        18: 24,
        19: 21,
        20: 15,
        21: 27,
        22: 21,
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
