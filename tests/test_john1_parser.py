"""Unit tests for the Book of 1 John parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.john1.service import John1Extractor


class TestJohn1Parser(unittest.TestCase):
    def test_john1_extractor_constants(self):
        """Should initialize with correct book names, pages, and verse total."""
        with given([]) as _:
            extractor = John1Extractor()

        with when("checking names, pages and verse total"):
            names = (extractor.KIKUYU_NAME, extractor.ENGLISH_NAME)
            values = (
                extractor.KIKUYU_START_PAGE,
                extractor.KIKUYU_END_PAGE,
                extractor.ENGLISH_START_PAGE,
                extractor.ENGLISH_END_PAGE,
                extractor.total_verses,
            )

        with then("the extraction window covers 1 John only"):
            assert_that(names, is_(equal_to(("1 Johana", "1 John"))))
            assert_that(values, is_(equal_to((1459, 1462, 1535, 1538, 105))))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = John1Extractor()
            parsed_data = {1: {1: "John, an apostle", 3: "   "}}

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_all_john1_verses_aligned(self):
        """All 105 verse pairs must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = John1Extractor()

        with when("extracting and validating 1 John"):
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
            extractor = John1Extractor()

        with when("extracting both languages"):
            kik = extractor.parse_book_verses("data/Kikuyu_Bible_all.pdf", "kikuyu")
            eng = extractor.parse_book_verses("data/English_Bible_all.pdf", "english")

        with then("verses are clean"):
            marks = "*†‡§"
            for data in (kik, eng):
                for verses in data.values():
                    for text in verses.values():
                        assert_that(any(m in text for m in marks), is_(False))

    def test_heavenly_witnesses_clause_is_removed(self):
        """The Kikuyu-only textual variant in 5:7 is stripped so pairs align."""
        with given([]) as _:
            extractor = John1Extractor()
            text = "Nĩgũkorwo aira nĩ atatũ (kũu igũrũ: nao nĩ Ithe witũ; nao aya atatũ nĩ ũmwe. Gũkũ thĩ nakuo aira nĩ atatũ):"

        with when("cleaning the verse"):
            cleaned = extractor.strip_heavenly_witnesses(text)

        with then("only the shared clause remains"):
            assert_that(cleaned, is_(equal_to("Nĩgũkorwo aira nĩ atatũ:")))
