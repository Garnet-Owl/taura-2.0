"""Unit tests for the Book of Romans parser/extractor."""

import unittest
from unittest.mock import MagicMock

from givenpy import given, then, when
from hamcrest import assert_that, contains_string, equal_to, is_, not_

from app.preprocessing.bible.romans.service import RomansExtractor


class TestRomansParser(unittest.TestCase):
    def test_romans_extractor_constants(self):
        """Should initialize with correct book names, page constants, and verse total."""
        with given([]) as _:
            extractor = RomansExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Aroma")))
            assert_that(english_name, is_(equal_to("Romans")))

        with when("checking page constants"):
            kik_start = extractor.KIKUYU_START_PAGE
            kik_end = extractor.KIKUYU_END_PAGE
            eng_start = extractor.ENGLISH_START_PAGE
            eng_end = extractor.ENGLISH_END_PAGE

        with then("pages are correct"):
            assert_that(kik_start, is_(equal_to(1350)))
            assert_that(kik_end, is_(equal_to(1367)))
            assert_that(eng_start, is_(equal_to(1434)))
            assert_that(eng_end, is_(equal_to(1449)))

        with then("total verse count is 433"):
            assert_that(extractor.total_verses, is_(equal_to(433)))

    def test_clean_english_verse(self):
        """Should strip cross-reference markers from English verse text."""
        with given([]) as _:
            extractor = RomansExtractor()
            raw_text = "For all have sinned* 3:23 and fall short of the glory of God."

        with when("cleaning english verse"):
            cleaned = extractor.clean_english_verse(raw_text)

        with then("cross-reference marker is removed"):
            assert_that(cleaned, not_(contains_string("* 3:23")))
            assert_that(cleaned, contains_string("For all have sinned"))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = RomansExtractor()
            parsed_data = {
                1: {
                    1: "Paul, a servant of Jesus Christ",
                    # 2 missing
                    3: "   ",
                }
            }

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_extract_page_body_text_filters_headers_and_footnotes(self):
        """Should exclude header lines, footer lines, and small-font footnote lines."""
        with given([]) as _:
            extractor = RomansExtractor()
            mock_page = MagicMock()
            mock_page.get_text.return_value = {
                "blocks": [
                    {
                        "lines": [
                            {
                                "bbox": (50, 40, 500, 60),
                                "spans": [
                                    {
                                        "text": "1434 Romans 1:1",
                                        "font": "Normal",
                                        "size": 12.0,
                                    }
                                ],
                            },
                            {
                                "bbox": (50, 80, 500, 100),
                                "spans": [
                                    {
                                        "text": "Paul, a servant of Jesus Christ",
                                        "font": "Normal",
                                        "size": 12.0,
                                    }
                                ],
                            },
                            {
                                "bbox": (50, 660, 500, 675),
                                "spans": [
                                    {
                                        "text": "footnote ref 3:23",
                                        "font": "Normal",
                                        "size": 9.0,
                                    }
                                ],
                            },
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
            assert_that(body_text, not_(contains_string("1434 Romans 1:1")))
            assert_that(body_text, contains_string("Paul, a servant of Jesus Christ"))
            assert_that(body_text, not_(contains_string("footnote ref")))
            assert_that(body_text, not_(contains_string("page 1")))

    def test_all_romans_verses_aligned(self):
        """Romans extraction: Kikuyu 0 missing/empty; English allows 2 missing due to
        versification difference (WEB places 16:26-27 in a doxology footnote instead of
        numbering them as chapter 16 verses). At least 430 aligned pairs must be produced."""
        with given([]) as _:
            extractor = RomansExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"
            eng_pdf = "data/English_Bible_all.pdf"

        with when("extracting and aligning Romans"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")
            eng_data = extractor.parse_book_verses(eng_pdf, "english")
            kik_missing, kik_empty = extractor.validate_extracted_verses(kik_data)
            eng_missing, eng_empty = extractor.validate_extracted_verses(eng_data)
            df = extractor.extract_and_align(kik_pdf, eng_pdf)

        with then("Kikuyu extraction is clean"):
            assert_that(len(kik_missing), is_(equal_to(0)))
            assert_that(len(kik_empty), is_(equal_to(0)))

        with then(
            "English has at most 2 missing due to known versification gap (16:26-27)"
        ):
            assert_that(len(eng_missing) <= 2, is_(True))
            assert_that(len(eng_empty), is_(equal_to(0)))

        with then("at least 430 aligned pairs are produced"):
            assert_that(len(df) >= 430, is_(True))
