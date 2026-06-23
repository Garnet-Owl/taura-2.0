"""
Core definitions and structural specifications for the Book of Matthew (Mathayo) extractor.
"""

from typing import Dict, List, Tuple


class MatthewExtractor:
    """
    Specifies the structural context and validation logic for the Book of Matthew.
    """

    ENGLISH_NAME = "Matthew"
    KIKUYU_NAME = "Mathayo"

    # Start and end pages in the complete Bible PDFs for Matthew
    KIKUYU_START_PAGE = 1179
    KIKUYU_END_PAGE = 1217
    ENGLISH_START_PAGE = 1263
    ENGLISH_END_PAGE = 1300

    # Matthew contains 28 chapters with standard verse counts
    CHAPTER_VERSES_MAP = {
        1: 25,
        2: 23,
        3: 17,
        4: 25,
        5: 48,
        6: 34,
        7: 29,
        8: 34,
        9: 38,
        10: 42,
        11: 30,
        12: 50,
        13: 58,
        14: 36,
        15: 39,
        16: 28,
        17: 27,
        18: 35,
        19: 30,
        20: 34,
        21: 46,
        22: 46,
        23: 39,
        24: 51,
        25: 46,
        26: 75,
        27: 66,
        28: 20,
    }

    @property
    def total_verses(self) -> int:
        return sum(self.CHAPTER_VERSES_MAP.values())

    def get_expected_verses(self) -> List[Tuple[int, int]]:
        """
        Returns a list of expected (chapter, verse) tuples for Matthew.
        """
        expected = []
        for ch, max_v in self.CHAPTER_VERSES_MAP.items():
            for v in range(1, max_v + 1):
                expected.append((ch, v))
        return expected

    def validate_extracted_verses(
        self, parsed_data: Dict[int, Dict[int, str]]
    ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Validates parsed data against the expected Matthew structure.
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
