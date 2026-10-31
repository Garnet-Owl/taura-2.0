"""
Core definitions and structural specifications for the Book of Hosea.
"""

from typing import Dict, List, Tuple


class HoseaExtractor:
    ENGLISH_NAME = "Hosea"
    KIKUYU_NAME = "Hosea"

    KIKUYU_START_PAGE = 1097
    KIKUYU_END_PAGE = 1112
    ENGLISH_START_PAGE = 910
    ENGLISH_END_PAGE = 919

    CHAPTER_VERSES_MAP = {
        1: 11, 2: 23, 3: 5, 4: 19, 5: 15, 6: 11, 7: 16,
        8: 14, 9: 17, 10: 15, 11: 12, 12: 14, 13: 16, 14: 9,
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
