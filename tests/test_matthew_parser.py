"""Unit tests for the Book of Matthew parser/extractor."""

import unittest
from unittest.mock import MagicMock

from givenpy import given, then, when
from hamcrest import assert_that, contains_string, equal_to, is_, not_

from app.preprocessing.bible.matthew.service import MatthewExtractor


class TestMatthewParser(unittest.TestCase):
    def test_matthew_extractor_constants(self):
        """Should initialize with correct start/end pages and chapter maps."""
        with given([]) as _:
            extractor = MatthewExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Mathayo")))
            assert_that(english_name, is_(equal_to("Matthew")))

        with when("checking page constants"):
            kik_start = extractor.KIKUYU_START_PAGE
            kik_end = extractor.KIKUYU_END_PAGE
            eng_start = extractor.ENGLISH_START_PAGE
            eng_end = extractor.ENGLISH_END_PAGE

        with then("pages are correct"):
            assert_that(kik_start, is_(equal_to(1179)))
            assert_that(kik_end, is_(equal_to(1217)))
            assert_that(eng_start, is_(equal_to(1263)))
            assert_that(eng_end, is_(equal_to(1300)))

    def test_clean_english_verse(self):
        """Should strip footnotes and cross-reference markers."""
        with given([]) as _:
            extractor = MatthewExtractor()
            raw_text = "This is a verse * 7:7 with a cross-reference."

        with when("cleaning english verse"):
            cleaned = extractor.clean_english_verse(raw_text)

        with then("cross-reference is removed"):
            assert_that(
                cleaned, is_(equal_to("This is a verse  with a cross-reference."))
            )

    def test_validation_logic(self):
        """Should correctly detect missing or empty verses."""
        with given([]) as _:
            extractor = MatthewExtractor()
            # Simulate a missing verse in ch 1, v 2
            parsed_data = {
                1: {
                    1: "Genealogy of Jesus",
                    # 2 is missing
                    3: "   ",  # Empty verse
                }
            }

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            # Chapter 1 has 25 verses. So 1:2 and 1:4..25 are missing, and 1:3 is empty.
            # Let's check that (1, 2) in missing and (1, 3) in empty.
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_find_next_verse_pos(self):
        """Should locate verse numbers correctly while ignoring sub-strings."""
        with given([]) as _:
            extractor = MatthewExtractor()
            body_text = "This is some text. 2 And he said to them... 22 But when..."

        with when("finding verse marker"):
            match = extractor.find_next_verse_pos(body_text, 2, 0)

        with then("marker is found correctly"):
            assert_that(match is not None, is_(True))
            assert_that(match.group(), is_(equal_to("2")))

    def test_extract_page_body_text_filters_headers_and_footnotes(self):
        """Should exclude header lines (ly1<71), footer lines (ly0>=719), and bottom-region small-font lines."""
        with given([]) as _:
            extractor = MatthewExtractor()
            mock_page = MagicMock()
            mock_page.get_text.return_value = {
                "blocks": [
                    {
                        "lines": [
                            # Header line: ly1=60 < 71 — must be excluded
                            {
                                "bbox": (50, 40, 500, 60),
                                "spans": [
                                    {
                                        "text": "1263 Matthew 4:9",
                                        "font": "NormalFont",
                                        "size": 12.0,
                                    }
                                ],
                            },
                            # Body line — must be included
                            {
                                "bbox": (50, 80, 500, 100),
                                "spans": [
                                    {
                                        "text": "In those days John came",
                                        "font": "NormalFont",
                                        "size": 12.0,
                                    }
                                ],
                            },
                            # Bottom-region, small font (9pt) — must be excluded
                            {
                                "bbox": (50, 660, 500, 675),
                                "spans": [
                                    {
                                        "text": "footnote ref 7:7",
                                        "font": "NormalFont",
                                        "size": 9.0,
                                    }
                                ],
                            },
                            # Footer line: ly0=720 >= 719 — must be excluded
                            {
                                "bbox": (50, 720, 500, 740),
                                "spans": [
                                    {
                                        "text": "page 3",
                                        "font": "NormalFont",
                                        "size": 12.0,
                                    }
                                ],
                            },
                        ]
                    }
                ]
            }

        with when("extracting body text"):
            body_text = extractor.extract_page_body_text(mock_page)

        with then("only body text survives"):
            assert_that(body_text, is_(equal_to("In those days John came")))
            assert_that(body_text, not_(contains_string("1263 Matthew 4:9")))
            assert_that(body_text, not_(contains_string("footnote ref")))
            assert_that(body_text, not_(contains_string("page 3")))

    def test_find_verse_positions_no_truncation(self):
        """Should find start_pos of verse 1 immediately after the marker to prevent first-letter truncation."""
        with given([]) as _:
            extractor = MatthewExtractor()
            # body text has chapter start and verse 1
            body_text = "Mathayo 1 1 Maya nĩ maandĩko"
            page_verses = [("Mathayo", 1, 1)]

        with when("finding verse positions"):
            positions = extractor._find_verse_positions(body_text, page_verses)

        with then("start_pos starts right after marker 1"):
            assert_that(positions[0]["start_pos"], is_(equal_to(11)))
            sliced = body_text[positions[0]["start_pos"] :].strip()
            assert_that(sliced, is_(equal_to("Maya nĩ maandĩko")))
