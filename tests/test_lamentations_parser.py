"""Unit tests for the Book of Lamentations parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.lamentations.service import LamentationsExtractor


class TestLamentationsParser(unittest.TestCase):
    def test_lamentations_extractor_constants(self):
        """Should initialize with correct book names, pages, and verse total."""
        with given([]) as _:
            extractor = LamentationsExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Macakaya")))
            assert_that(english_name, is_(equal_to("Lamentations")))

        with when("checking page constants and total verses"):
            values = (
                extractor.KIKUYU_START_PAGE,
                extractor.KIKUYU_END_PAGE,
                extractor.ENGLISH_START_PAGE,
                extractor.ENGLISH_END_PAGE,
                extractor.total_verses,
            )

        with then("the extraction window covers Lamentations only"):
            assert_that(values, is_(equal_to((1005, 1017, 826, 833, 154))))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = LamentationsExtractor()
            parsed_data = {1: {1: "Ahasuerus reigned", 3: "   "}}

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_all_lamentations_verses_aligned(self):
        """All 154 verse pairs must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = LamentationsExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"
            eng_pdf = "data/English_Bible_all.pdf"

        with when("extracting and validating Lamentations"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")
            eng_data = extractor.parse_book_verses(eng_pdf, "english")
            kik_missing, kik_empty = extractor.validate_extracted_verses(kik_data)
            eng_missing, eng_empty = extractor.validate_extracted_verses(eng_data)

        with then("no verse is missing or empty"):
            assert_that(kik_missing, is_(equal_to([])))
            assert_that(kik_empty, is_(equal_to([])))
            assert_that(eng_missing, is_(equal_to([])))
            assert_that(eng_empty, is_(equal_to([])))

    def test_verse_boundaries_are_clean(self):
        """Chapter-first verses must not keep the verse number, last verses no chapter number."""
        with given([]) as _:
            extractor = LamentationsExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"

        with when("extracting the Kikuyu text"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")

        with then("verse 1 starts with its words and chapter ends are clean"):
            assert_that(kik_data[1][1].startswith("Hĩ! Kaĩ itũũra"), is_(True))
            assert_that(
                kik_data[3][66].rstrip().endswith("mũhuro wa igũrũ rĩa Jehova."),
                is_(True),
            )
            assert_that(kik_data[5][22].rstrip().endswith("o mũno makĩria."), is_(True))
