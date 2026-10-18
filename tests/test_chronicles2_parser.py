"""Unit tests for the Book of 2 Chronicles parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.chronicles2.service import Chronicles2Extractor


class TestChronicles2Parser(unittest.TestCase):
    def test_chronicles2_extractor_constants(self):
        """Should initialize with correct book names, pages, and verse total."""
        with given([]) as _:
            extractor = Chronicles2Extractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("2 Maũndũ")))
            assert_that(english_name, is_(equal_to("2 Chronicles")))

        with when("checking page constants and total verses"):
            values = (
                extractor.KIKUYU_START_PAGE,
                extractor.KIKUYU_END_PAGE,
                extractor.ENGLISH_START_PAGE,
                extractor.ENGLISH_END_PAGE,
                extractor.total_verses,
            )

        with then("the extraction window covers 2 Chronicles only"):
            assert_that(values, is_(equal_to((471, 508, 459, 497, 822))))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = Chronicles2Extractor()
            parsed_data = {1: {1: "The LORD spoke to Moses", 3: "   "}}

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_all_chronicles2_verses_aligned(self):
        """All 822 verse pairs must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = Chronicles2Extractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"
            eng_pdf = "data/English_Bible_all.pdf"

        with when("extracting and validating 2 Chronicles"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")
            eng_data = extractor.parse_book_verses(eng_pdf, "english")
            kik_missing, kik_empty = extractor.validate_extracted_verses(kik_data)
            eng_missing, eng_empty = extractor.validate_extracted_verses(eng_data)

        with then("no verse is missing or empty"):
            assert_that(kik_missing, is_(equal_to([])))
            assert_that(kik_empty, is_(equal_to([])))
            assert_that(eng_missing, is_(equal_to([])))
            assert_that(eng_empty, is_(equal_to([])))

    def test_numbers_in_text_are_not_verse_markers(self):
        """Counts such as '3,600' and '22 na airĩtu' must stay inside their verse."""
        with given([]) as _:
            extractor = Chronicles2Extractor()
            kik_data = extractor.parse_book_verses("data/Kikuyu_Bible_all.pdf", "kikuyu")

        with when("reading 2 Chronicles 2:2 and 13:21"):
            verse_2_2 = kik_data[2][2]
            verse_13_21 = kik_data[13][21]

        with then("the numbers remain inside the verse that owns them"):
            assert_that(verse_2_2.endswith("3,600 a kũmaroraga."), is_(True))
            assert_that(verse_13_21.endswith("aanake 22 na airĩtu 16."), is_(True))
