"""
Core definitions and structural specifications for the Book of Acts (Atũmwo) extractor.
"""

from typing import Dict, List, Tuple


class ActsExtractor:
    ENGLISH_NAME = "Acts"
    KIKUYU_NAME = "Atũmwo"

    KIKUYU_START_PAGE = 1312
    KIKUYU_END_PAGE = 1349
    ENGLISH_START_PAGE = 1395
    ENGLISH_END_PAGE = 1433

    CHAPTER_VERSES_MAP = {
        1: 26,
        2: 47,
        3: 26,
        4: 37,
        5: 42,
        6: 15,
        7: 60,
        8: 40,
        9: 43,
        10: 48,
        11: 30,
        12: 25,
        13: 52,
        14: 28,
        15: 41,
        16: 40,
        17: 34,
        18: 28,
        19: 41,
        20: 38,
        21: 40,
        22: 30,
        23: 35,
        24: 27,
        25: 27,
        26: 32,
        27: 44,
        28: 31,
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
