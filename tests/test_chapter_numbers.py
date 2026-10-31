"""Unit tests for removing the next chapter's number left on a chapter's last verse."""

import unittest

import pandas as pd
from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.bible.base.core import strip_next_chapter_numbers


class TestStripNextChapterNumbers(unittest.TestCase):
    def test_chapter_last_verse_loses_next_chapter_number(self):
        """Genesis 1:31 is the last verse of chapter 1, so a trailing 2 is removed."""
        with given([]) as _:
            df = pd.DataFrame({
                "Reference": ["Genesis 1:31"],
                "Kikuyu": ["mũthenya wa gatandatũ. 2"],
                "English": ["a sixth day. 2"],
            })

        with when("cleaning the aligned verses"):
            cleaned = strip_next_chapter_numbers(df)

        with then("both languages end at the verse text"):
            assert_that(cleaned.loc[0, "Kikuyu"], is_(equal_to("mũthenya wa gatandatũ.")))
            assert_that(cleaned.loc[0, "English"], is_(equal_to("a sixth day.")))

    def test_other_numbers_are_kept(self):
        """Counts inside a verse, and numbers on non-final verses, must survive."""
        with given([]) as _:
            df = pd.DataFrame({
                "Reference": ["Nehemiah 7:9", "Genesis 1:31", "1 Corinthians 1:31"],
                "Kikuyu": ["ciarĩ 372", "thuutha wa mĩaka 7", "ũguo. 2"],
                "English": ["were 372", "after 7 years", "so. 2"],
            })

        with when("cleaning the aligned verses"):
            cleaned = strip_next_chapter_numbers(df)

        with then("a count, or a number that is not the next chapter, is untouched"):
            assert_that(cleaned.loc[0, "Kikuyu"], is_(equal_to("ciarĩ 372")))
            assert_that(cleaned.loc[1, "Kikuyu"], is_(equal_to("thuutha wa mĩaka 7")))
            assert_that(cleaned.loc[1, "English"], is_(equal_to("after 7 years")))

        with then("the last verse of 1 Corinthians 1 loses its trailing 2"):
            assert_that(cleaned.loc[2, "Kikuyu"], is_(equal_to("ũguo.")))
