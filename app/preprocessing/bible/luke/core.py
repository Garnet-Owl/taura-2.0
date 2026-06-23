"""
Core definitions and structural specifications for the Book of Luke (Luka) extractor.
"""

from typing import Dict, List, Tuple


class LukeExtractor:
    """
    Specifies the structural context and validation logic for the Book of Luke.
    """

    ENGLISH_NAME = "Luke"
    KIKUYU_NAME = "Luka"

    KIKUYU_START_PAGE = 1242
    KIKUYU_END_PAGE = 1282
    ENGLISH_START_PAGE = 1325
    ENGLISH_END_PAGE = 1364

    CHAPTER_VERSES_MAP = {
        1: 80,
        2: 52,
        3: 38,
        4: 44,
        5: 39,
        6: 49,
        7: 50,
        8: 56,
        9: 62,
        10: 42,
        11: 54,
        12: 59,
        13: 35,
        14: 35,
        15: 32,
        16: 31,
        17: 37,
        18: 43,
        19: 48,
        20: 47,
        21: 38,
        22: 71,
        23: 56,
        24: 53,
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
        """
        Validates parsed data against the expected Luke structure.
        Returns:
            Tuple of (missing_verses, empty_verses)
        """
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
