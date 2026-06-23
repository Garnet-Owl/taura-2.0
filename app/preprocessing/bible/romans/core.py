"""
Core definitions and structural specifications for the Book of Romans (Aroma) extractor.
"""

from typing import Dict, List, Tuple


class RomansExtractor:
    ENGLISH_NAME = "Romans"
    KIKUYU_NAME = "Aroma"

    KIKUYU_START_PAGE = 1350
    KIKUYU_END_PAGE = 1367
    ENGLISH_START_PAGE = 1434
    ENGLISH_END_PAGE = 1449

    CHAPTER_VERSES_MAP = {
        1: 32,
        2: 29,
        3: 31,
        4: 25,
        5: 21,
        6: 23,
        7: 25,
        8: 39,
        9: 33,
        10: 21,
        11: 36,
        12: 21,
        13: 14,
        14: 23,
        15: 33,
        16: 27,
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
