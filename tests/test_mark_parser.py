"""Unit tests for the Book of Mark parser/extractor."""

import unittest
from unittest.mock import MagicMock

from givenpy import given, then, when
from hamcrest import assert_that, contains_string, equal_to, is_, not_

from app.preprocessing.bible.mark.service import MarkExtractor


class TestMarkParser(unittest.TestCase):
    def test_mark_extractor_constants(self):
        """Should initialize with correct book names, page constants, and verse total."""
        with given([]) as _:
            extractor = MarkExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Mariko")))
            assert_that(english_name, is_(equal_to("Mark")))

        with when("checking page constants"):
            kik_start = extractor.KIKUYU_START_PAGE
            kik_end = extractor.KIKUYU_END_PAGE
            eng_start = extractor.ENGLISH_START_PAGE
            eng_end = extractor.ENGLISH_END_PAGE

        with then("pages are correct"):
            assert_that(kik_start, is_(equal_to(1218)))
            assert_that(kik_end, is_(equal_to(1241)))
            assert_that(eng_start, is_(equal_to(1301)))
            assert_that(eng_end, is_(equal_to(1324)))

        with then("total verse count is 678"):
            assert_that(extractor.total_verses, is_(equal_to(678)))

    def test_clean_english_verse(self):
        """Should strip cross-reference markers from English verse text."""
        with given([]) as _:
            extractor = MarkExtractor()
            raw_text = "And he healed many * 1:34 who were sick."

        with when("cleaning english verse"):
            cleaned = extractor.clean_english_verse(raw_text)

        with then("cross-reference is removed"):
            assert_that(cleaned, is_(equal_to("And he healed many  who were sick.")))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = MarkExtractor()
            parsed_data = {
                1: {
                    1: "The beginning of the gospel",
                    # 2 missing
                    3: "   ",  # empty
                }
            }

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_extract_page_body_text_filters_headers_and_footnotes(self):
        """Should exclude header lines, true footer lines, and bottom-region small-font lines."""
        with given([]) as _:
            extractor = MarkExtractor()
            mock_page = MagicMock()
            mock_page.get_text.return_value = {
                "blocks": [
                    {
                        "lines": [
                            # Header: ly1=60 < 71 — excluded
                            {
                                "bbox": (50, 40, 500, 60),
                                "spans": [
                                    {
                                        "text": "1301 Mark 1:1",
                                        "font": "Normal",
                                        "size": 12.0,
                                    }
                                ],
                            },
                            # Body line — included
                            {
                                "bbox": (50, 80, 500, 100),
                                "spans": [
                                    {
                                        "text": "The beginning of the gospel",
                                        "font": "Normal",
                                        "size": 12.0,
                                    }
                                ],
                            },
                            # Last valid body line at ly0=722 (below 745 cutoff) — included
                            {
                                "bbox": (50, 722, 500, 742),
                                "spans": [
                                    {
                                        "text": "45 last verse on page",
                                        "font": "Normal",
                                        "size": 12.0,
                                    }
                                ],
                            },
                            # Bottom-region small font (9pt) — excluded
                            {
                                "bbox": (50, 660, 500, 675),
                                "spans": [
                                    {
                                        "text": "footnote ref 1:34",
                                        "font": "Normal",
                                        "size": 9.0,
                                    }
                                ],
                            },
                            # True footer at ly0=750 >= 745 — excluded
                            {
                                "bbox": (50, 750, 500, 765),
                                "spans": [
                                    {"text": "page 1", "font": "Normal", "size": 12.0}
                                ],
                            },
                        ]
                    }
                ]
            }

        with when("extracting body text"):
            body_text = extractor.extract_page_body_text(mock_page)

        with then("only body text survives"):
            assert_that(body_text, not_(contains_string("1301 Mark 1:1")))
            assert_that(body_text, contains_string("The beginning of the gospel"))
            assert_that(body_text, contains_string("45 last verse on page"))
            assert_that(body_text, not_(contains_string("footnote ref")))
            assert_that(body_text, not_(contains_string("page 1")))

    def test_all_mark_verses_aligned(self):
        """All 678 Mark verses must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = MarkExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"
            eng_pdf = "data/English_Bible_all.pdf"

        with when("extracting and aligning Mark"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")
            eng_data = extractor.parse_book_verses(eng_pdf, "english")
            kik_missing, kik_empty = extractor.validate_extracted_verses(kik_data)
            eng_missing, eng_empty = extractor.validate_extracted_verses(eng_data)

        with then("no verse is missing or empty"):
            assert_that(len(kik_missing), is_(equal_to(0)))
            assert_that(len(kik_empty), is_(equal_to(0)))
            assert_that(len(eng_missing), is_(equal_to(0)))
            assert_that(len(eng_empty), is_(equal_to(0)))
