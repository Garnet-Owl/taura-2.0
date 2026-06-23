"""
Core definitions and structural specifications for the Book of Mark (Mariko) extractor.
"""

from typing import Dict, List, Tuple


class MarkExtractor:
    """
    Specifies the structural context and validation logic for the Book of Mark.
    """

    ENGLISH_NAME = "Mark"
    KIKUYU_NAME = "Mariko"

    KIKUYU_START_PAGE = 1218
    KIKUYU_END_PAGE = 1241
    ENGLISH_START_PAGE = 1301
    ENGLISH_END_PAGE = 1324

    CHAPTER_VERSES_MAP = {
        1: 45,
        2: 28,
        3: 35,
        4: 41,
        5: 43,
        6: 56,
        7: 37,
        8: 38,
        9: 50,
        10: 52,
        11: 33,
        12: 44,
        13: 37,
        14: 72,
        15: 47,
        16: 20,
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
        Validates parsed data against the expected Mark structure.
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
