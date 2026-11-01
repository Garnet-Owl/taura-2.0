"""Unit tests for the Book of John3 parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.john3.service import John3Extractor


class TestJohn3Parser(unittest.TestCase):
    def test_john3_extractor_constants(self):
        """Should initialize with correct book names, pages, and verse total."""
        with given([]) as _:
            extractor = John3Extractor()

        with when("checking names, pages and verse total"):
            names = (extractor.KIKUYU_NAME, extractor.ENGLISH_NAME)
            values = (
                extractor.KIKUYU_START_PAGE,
                extractor.KIKUYU_END_PAGE,
                extractor.ENGLISH_START_PAGE,
                extractor.ENGLISH_END_PAGE,
                extractor.total_verses,
            )

        with then("the extraction window covers John3 only"):
            assert_that(names, is_(equal_to(("3 Johana", "3 John"))))
            assert_that(values, is_(equal_to((1464, 1464, 1540, 1540, 14))))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = John3Extractor()
            parsed_data = {1: {1: "Paul, an apostle", 3: "   "}}

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_all_john3_verses_aligned(self):
        """All 14 verse pairs must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = John3Extractor()

        with when("extracting and validating John3"):
            kik = extractor.parse_book_verses("data/Kikuyu_Bible_all.pdf", "kikuyu")
            eng = extractor.parse_book_verses("data/English_Bible_all.pdf", "english")
            results = [
                extractor.validate_extracted_verses(kik),
                extractor.validate_extracted_verses(eng),
            ]

        with then("no verse is missing or empty"):
            for missing, empty in results:
                assert_that(missing, is_(equal_to([])))
                assert_that(empty, is_(equal_to([])))

    def test_footnote_marks_are_clean(self):
        """No footnote symbols remain in either language."""
        with given([]) as _:
            extractor = John3Extractor()

        with when("extracting both languages"):
            kik = extractor.parse_book_verses("data/Kikuyu_Bible_all.pdf", "kikuyu")
            eng = extractor.parse_book_verses("data/English_Bible_all.pdf", "english")

        with then("verses are clean"):
            marks = "*†‡§"
            for data in (kik, eng):
                for verses in data.values():
                    for text in verses.values():
                        assert_that(any(m in text for m in marks), is_(False))
