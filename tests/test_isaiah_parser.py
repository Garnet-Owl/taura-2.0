"""Unit tests for the Book of Isaiah parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.isaiah.service import IsaiahExtractor


class TestIsaiahParser(unittest.TestCase):
    def test_isaiah_extractor_constants(self):
        """Should initialize with correct book names, pages, and verse total."""
        with given([]) as _:
            extractor = IsaiahExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Isaia")))
            assert_that(english_name, is_(equal_to("Isaiah")))

        with when("checking page constants and total verses"):
            values = (
                extractor.KIKUYU_START_PAGE,
                extractor.KIKUYU_END_PAGE,
                extractor.ENGLISH_START_PAGE,
                extractor.ENGLISH_END_PAGE,
                extractor.total_verses,
            )

        with then("the extraction window covers Isaiah only"):
            assert_that(values, is_(equal_to((812, 914, 696, 758, 1292))))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = IsaiahExtractor()
            parsed_data = {
                1: {
                    1: "The vision of Isaiah",
                    3: "   ",
                }
            }

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))
