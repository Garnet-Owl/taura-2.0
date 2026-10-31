"""Unit tests for the Book of Revelation parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.revelation.service import RevelationExtractor


class TestRevelationParser(unittest.TestCase):
    def test_revelation_extractor_constants(self):
        """Should initialize with correct book names, pages, and verse total."""
        with given([]) as _:
            extractor = RevelationExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Kũguũrĩrio")))
            assert_that(english_name, is_(equal_to("Revelation")))

        with when("checking page constants and total verses"):
            values = (
                extractor.KIKUYU_START_PAGE,
                extractor.KIKUYU_END_PAGE,
                extractor.ENGLISH_START_PAGE,
                extractor.ENGLISH_END_PAGE,
                extractor.total_verses,
            )

        with then("the extraction window covers Revelation only"):
            assert_that(values, is_(equal_to((1467, 1488, 1543, 1560, 404))))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = RevelationExtractor()
            parsed_data = {1: {1: "I saw a new heaven", 3: "   "}}

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_all_revelation_verses_aligned(self):
        """All 404 verse pairs must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = RevelationExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"
            eng_pdf = "data/English_Bible_all.pdf"

        with when("extracting and validating Revelation"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")
            eng_data = extractor.parse_book_verses(eng_pdf, "english")
            kik_missing, kik_empty = extractor.validate_extracted_verses(kik_data)
            eng_missing, eng_empty = extractor.validate_extracted_verses(eng_data)

        with then("no verse is missing or empty"):
            assert_that(kik_missing, is_(equal_to([])))
            assert_that(kik_empty, is_(equal_to([])))
            assert_that(eng_missing, is_(equal_to([])))
            assert_that(eng_empty, is_(equal_to([])))

    def test_numeric_counts_kept_but_chapter_numbers_dropped(self):
        """Counts inside Revelation verses must survive; chapter numbers must not."""
        with given([]) as _:
            extractor = RevelationExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"

        with when("extracting the Kikuyu text"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")

        with then("the sealed count keeps its number"):
            assert_that("144,000" in kik_data[7][4], is_(True))

        with then("the last verse is free of the next chapter's number"):
            assert_that(kik_data[22][21].endswith("Ameni."), is_(True))
