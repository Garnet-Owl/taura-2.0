"""
Core definitions and structural specifications for the Book of Hebrews.
"""

from typing import Dict, List, Tuple


class HebrewsExtractor:
    ENGLISH_NAME = "Hebrews"
    KIKUYU_NAME = "Ahibirania"

    KIKUYU_START_PAGE = 1433
    KIKUYU_END_PAGE = 1445
    ENGLISH_START_PAGE = 1511
    ENGLISH_END_PAGE = 1522

    CHAPTER_VERSES_MAP = {
        1: 14, 2: 18, 3: 19, 4: 16, 5: 14, 6: 20, 7: 28, 8: 13, 9: 28, 10: 39, 11: 40, 12: 29, 13: 25,
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
