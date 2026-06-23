"""
Core definitions and structural specifications for the Book of Ephesians.
"""

from typing import Dict, List, Tuple


class EphesiansExtractor:
    ENGLISH_NAME = "Ephesians"
    KIKUYU_NAME = "Aefeso"

    KIKUYU_START_PAGE = 1401
    KIKUYU_END_PAGE = 1406
    ENGLISH_START_PAGE = 1481
    ENGLISH_END_PAGE = 1486

    CHAPTER_VERSES_MAP = {
        1: 23,
        2: 22,
        3: 21,
        4: 32,
        5: 33,
        6: 24,
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
