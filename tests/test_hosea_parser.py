"""Unit tests for the Book of Hosea parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.hosea.service import HoseaExtractor


class TestHoseaParser(unittest.TestCase):
    def test_hosea_extractor_constants(self):
        """Should initialize with correct book names, pages, and verse total."""
        with given([]) as _:
            extractor = HoseaExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Hosea")))
            assert_that(english_name, is_(equal_to("Hosea")))

        with when("checking page constants and total verses"):
            values = (
                extractor.KIKUYU_START_PAGE,
                extractor.KIKUYU_END_PAGE,
                extractor.ENGLISH_START_PAGE,
                extractor.ENGLISH_END_PAGE,
                extractor.total_verses,
            )

        with then("the extraction window covers Hosea only"):
            assert_that(values, is_(equal_to((1097, 1112, 910, 919, 197))))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = HoseaExtractor()
            parsed_data = {1: {1: "Hosea son of Beeri", 3: "   "}}

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_all_hosea_verses_aligned(self):
        """All 197 verse pairs must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = HoseaExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"
            eng_pdf = "data/English_Bible_all.pdf"

        with when("extracting and validating Hosea"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")
            eng_data = extractor.parse_book_verses(eng_pdf, "english")
            kik_missing, kik_empty = extractor.validate_extracted_verses(kik_data)
            eng_missing, eng_empty = extractor.validate_extracted_verses(eng_data)

        with then("no verse is missing or empty"):
            assert_that(kik_missing, is_(equal_to([])))
            assert_that(kik_empty, is_(equal_to([])))
            assert_that(eng_missing, is_(equal_to([])))
            assert_that(eng_empty, is_(equal_to([])))

    def test_chapter_last_verses_end_cleanly(self):
        """A chapter's last verse must not carry the next chapter number."""
        with given([]) as _:
            extractor = HoseaExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"

        with when("extracting the Kikuyu text"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")

        with then("chapter-final verses end with sentence punctuation"):
            assert_that(kik_data[1][11].rstrip().endswith("mũthenya mũnene."), is_(True))
            assert_that(
                kik_data[14][9].rstrip().endswith("marĩ o njĩra-inĩ icio."), is_(True)
            )
