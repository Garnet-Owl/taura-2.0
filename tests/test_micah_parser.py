"""Unit tests for the Book of Micah parser/extractor."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.micah.service import MicahExtractor


class TestMicahParser(unittest.TestCase):
    def test_micah_extractor_constants(self):
        """Should initialize with correct book names, pages, and verse total."""
        with given([]) as _:
            extractor = MicahExtractor()

        with when("checking book names"):
            kikuyu_name = extractor.KIKUYU_NAME
            english_name = extractor.ENGLISH_NAME

        with then("names are correct"):
            assert_that(kikuyu_name, is_(equal_to("Mika")))
            assert_that(english_name, is_(equal_to("Micah")))

        with when("checking page constants and total verses"):
            values = (
                extractor.KIKUYU_START_PAGE,
                extractor.KIKUYU_END_PAGE,
                extractor.ENGLISH_START_PAGE,
                extractor.ENGLISH_END_PAGE,
                extractor.total_verses,
            )

        with then("the extraction window covers Micah only"):
            assert_that(values, is_(equal_to((1138, 1147, 937, 942, 105))))

    def test_validation_logic(self):
        """Should correctly detect missing and empty verses."""
        with given([]) as _:
            extractor = MicahExtractor()
            parsed_data = {1: {1: "Ahasuerus reigned", 3: "   "}}

        with when("validating parsed verses"):
            missing, empty = extractor.validate_extracted_verses(parsed_data)

        with then("missing and empty verses are reported correctly"):
            assert_that((1, 2) in missing, is_(True))
            assert_that((1, 3) in empty, is_(True))

    def test_all_micah_verses_aligned(self):
        """All 105 verse pairs must be extracted with no missing or empty on either side."""
        with given([]) as _:
            extractor = MicahExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"
            eng_pdf = "data/English_Bible_all.pdf"

        with when("extracting and validating Micah"):
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
            extractor = MicahExtractor()
            kik_pdf = "data/Kikuyu_Bible_all.pdf"

        with when("extracting the Kikuyu text"):
            kik_data = extractor.parse_book_verses(kik_pdf, "kikuyu")

        with then("verse 1 starts with its words and chapter ends are clean"):
            assert_that(
                kik_data[1][1].startswith("Ĩno nĩyo ndũmĩrĩri ya Jehova"), is_(True)
            )
            assert_that(
                kik_data[7][20].rstrip().endswith("matukũ-inĩ macio ma tene."), is_(True)
            )
            assert_that(kik_data[1][16][0].isalpha(), is_(True))

    def test_footnote_marks_are_removed(self):
        """Footnote symbols such as * and dagger must not remain in either language."""
        with given([]) as _:
            extractor = MicahExtractor()

        with when("extracting both languages"):
            kik = extractor.parse_book_verses("data/Kikuyu_Bible_all.pdf", "kikuyu")
            eng = extractor.parse_book_verses("data/English_Bible_all.pdf", "english")

        with then("no footnote symbol is left in any verse"):
            marks = "*\u2020\u2021\u00a7"
            for data in (kik, eng):
                for verses in data.values():
                    for text in verses.values():
                        assert_that(any(m in text for m in marks), is_(False))
            assert_that(
                eng[1][1].startswith("Yahweh\u2019s word that came to Micah"), is_(True)
            )
