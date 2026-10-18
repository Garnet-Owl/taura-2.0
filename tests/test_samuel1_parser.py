"""Unit tests for the Book of 1 Samuel parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.samuel1.service import Samuel1Extractor


class TestSamuel1Parser(unittest.TestCase):
    def test_samuel1_extractor_constants(self):
        """Should initialize with correct book names, pages, and verse total."""
        with given([]) as _:
            extractor = Samuel1Extractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("1 Samũeli")))
            assert_that(english_name, is_(equal_to("1 Samuel")))

        with when("checking page constants and total verses"):
            values = (
                extractor.KIKUYU_START_PAGE,
                extractor.KIKUYU_END_PAGE,
                extractor.ENGLISH_START_PAGE,
                extractor.ENGLISH_END_PAGE,
                extractor.total_verses,
            )

        with then("the extraction window covers 1 Samuel only"):
            assert_that(values, is_(equal_to((293, 327, 293, 328, 810))))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = Samuel1Extractor()
            parsed_data = {1: {1: "There was a certain man", 3: "   "}}

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_all_samuel1_verses_aligned(self):
        """All 810 verse pairs must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = Samuel1Extractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"
            eng_pdf = "data/English_Bible_all.pdf"

        with when("extracting and validating 1 Samuel"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")
            eng_data = extractor.parse_book_verses(eng_pdf, "english")
            kik_missing, kik_empty = extractor.validate_extracted_verses(kik_data)
            eng_missing, eng_empty = extractor.validate_extracted_verses(eng_data)

        with then("no verse is missing or empty"):
            assert_that(kik_missing, is_(equal_to([])))
            assert_that(kik_empty, is_(equal_to([])))
            assert_that(eng_missing, is_(equal_to([])))
            assert_that(eng_empty, is_(equal_to([])))
