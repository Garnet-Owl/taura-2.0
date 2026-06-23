"""
Core definitions and structural specifications for the Book of John (Johana) extractor.
"""

from typing import Dict, List, Tuple


class JohnExtractor:
    ENGLISH_NAME = "John"
    KIKUYU_NAME = "Johana"

    KIKUYU_START_PAGE = 1283
    KIKUYU_END_PAGE = 1311
    ENGLISH_START_PAGE = 1365
    ENGLISH_END_PAGE = 1394

    CHAPTER_VERSES_MAP = {
        1: 51,
        2: 25,
        3: 36,
        4: 54,
        5: 47,
        6: 71,
        7: 53,
        8: 59,
        9: 41,
        10: 42,
        11: 57,
        12: 50,
        13: 38,
        14: 31,
        15: 27,
        16: 33,
        17: 26,
        18: 40,
        19: 42,
        20: 31,
        21: 25,
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
