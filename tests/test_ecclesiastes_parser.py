"""Unit tests for the Book of Ecclesiastes parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.ecclesiastes.service import EcclesiastesExtractor


class TestEcclesiastesParser(unittest.TestCase):
    def test_ecclesiastes_extractor_constants(self):
        """Should initialize with correct book names, page constants, and verse total."""
        with given([]) as _:
            extractor = EcclesiastesExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Kohelethu")))
            assert_that(english_name, is_(equal_to("Ecclesiastes")))

        with when("checking page constants"):
            kik_start = extractor.KIKUYU_START_PAGE
            kik_end = extractor.KIKUYU_END_PAGE
            eng_start = extractor.ENGLISH_START_PAGE
            eng_end = extractor.ENGLISH_END_PAGE

        with then("pages are correct"):
            assert_that(kik_start, is_(equal_to(789)))
            assert_that(kik_end, is_(equal_to(801)))
            assert_that(eng_start, is_(equal_to(681)))
            assert_that(eng_end, is_(equal_to(689)))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = EcclesiastesExtractor()
            parsed_data = {
                1: {
                    1: "Blessed is the man",
                    3: "   ",
                }
            }

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))
