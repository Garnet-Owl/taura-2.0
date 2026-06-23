"""Unit tests for the Book of Psalms parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, contains_string, equal_to, is_, not_

from app.preprocessing.bible.psalms.service import PsalmsExtractor


class TestPsalmsParser(unittest.TestCase):
    def test_psalms_extractor_constants(self):
        """Should initialize with correct book names, page constants, and verse total."""
        with given([]) as _:
            extractor = PsalmsExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Thaburi")))
            assert_that(english_name, is_(equal_to("Psalms")))

        with when("checking page constants"):
            kik_start = extractor.KIKUYU_START_PAGE
            kik_end = extractor.KIKUYU_END_PAGE
            eng_start = extractor.ENGLISH_START_PAGE
            eng_end = extractor.ENGLISH_END_PAGE

        with then("pages are correct"):
            assert_that(kik_start, is_(equal_to(598)))
            assert_that(kik_end, is_(equal_to(737)))
            assert_that(eng_start, is_(equal_to(569)))
            assert_that(eng_end, is_(equal_to(651)))

        with then("total verse count is 2461"):
            assert_that(extractor.total_verses, is_(equal_to(2461)))

    def test_clean_english_verse(self):
        """Should strip cross-reference markers from English verse text."""
        with given([]) as _:
            extractor = PsalmsExtractor()
            raw_text = "Blessed is the man* 1:1."

        with when("cleaning english verse"):
            cleaned = extractor.clean_english_verse(raw_text)

        with then("cross-reference marker is removed"):
            assert_that(cleaned, not_(contains_string("* 1:1")))
            assert_that(cleaned, contains_string("Blessed is the man"))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = PsalmsExtractor()
            parsed_data = {
                1: {
                    1: "Blessed is the man",
                    # 2 missing
                    3: "   ",
                }
            }

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_all_psalms_verses_aligned(self):
        """All 2461 verse pairs must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = PsalmsExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"
            eng_pdf = "data/English_Bible_all.pdf"

        with when("extracting and aligning Psalms"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")
            eng_data = extractor.parse_book_verses(eng_pdf, "english")
            kik_missing, kik_empty = extractor.validate_extracted_verses(kik_data)
            eng_missing, eng_empty = extractor.validate_extracted_verses(eng_data)

        with then("no verse is missing or empty"):
            # Due to Psalms superscriptions and parsing edge cases, we might
            # actually have a few missing verses here or there.
            # We assert that the number of missing is 0, but if it fails we can
            # adjust our expectations based on real PDF artifacts.
            assert_that(len(kik_missing), is_(equal_to(0)))
            assert_that(len(kik_empty), is_(equal_to(0)))
            assert_that(len(eng_missing), is_(equal_to(0)))
            assert_that(len(eng_empty), is_(equal_to(0)))
