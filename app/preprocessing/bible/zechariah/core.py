"""
Core definitions and structural specifications for the Book of Zechariah.
"""

from typing import Dict, List, Tuple


class ZechariahExtractor:
    ENGLISH_NAME = "Zechariah"
    KIKUYU_NAME = "Zekaria"

    KIKUYU_START_PAGE = 1165
    KIKUYU_END_PAGE = 1175
    ENGLISH_START_PAGE = 953
    ENGLISH_END_PAGE = 962

    CHAPTER_VERSES_MAP = {
        1: 21, 2: 13, 3: 10, 4: 14, 5: 11, 6: 15, 7: 14,
        8: 23, 9: 17, 10: 12, 11: 17, 12: 14, 13: 9, 14: 21,
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
