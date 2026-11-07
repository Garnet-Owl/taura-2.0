"""Unit tests for removing footnote marks and Psalms layout leftovers from verses."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.preprocessing.clean import clean_sentence


class TestCleanSentence(unittest.TestCase):
    def test_removes_footnote_marks(self):
        with given([]) as _:
            text = "Andũ a Galili,* mũrũgamĩte† haha‡ nĩkĩ?"

        with when("it is cleaned"):
            result = clean_sentence(text)

        with then("the marks are gone and spacing stays single"):
            assert_that(result, is_(equal_to("Andũ a Galili, mũrũgamĩte haha nĩkĩ?")))

    def test_removes_leading_verse_number(self):
        with given([]) as _:
            english = "1 Blessed is the man who doesn’t walk in the counsel."
            kikuyu = "20 Na rĩrĩ, andũ a Isiraeli nĩmoimagarire."

        with when("they are cleaned"):
            cleaned = (clean_sentence(english), clean_sentence(kikuyu))

        with then("the number is dropped"):
            assert_that(
                cleaned,
                is_(
                    equal_to((
                        "Blessed is the man who doesn’t walk in the counsel.",
                        "Na rĩrĩ, andũ a Isiraeli nĩmoimagarire.",
                    ))
                ),
            )

    def test_removes_psalms_book_and_title_leftovers(self):
        with given([]) as _:
            book = "Amen and amen. BOOK 2"
            book_and_title = "son of Jesse. BOOK 3 73 A Psalm by Asaph."
            title = "to him.” 51 For the Chief Musician. A Psalm by David."
            kikuyu = "mamũgooce! 65 Thaburi ya Daudi"

        with when("they are cleaned"):
            cleaned = [clean_sentence(t) for t in (book, book_and_title, title, kikuyu)]

        with then("only the verse text remains"):
            assert_that(
                cleaned,
                is_(
                    equal_to(["Amen and amen.", "son of Jesse.", "to him.”", "mamũgooce!"])
                ),
            )

    def test_keeps_numbers_inside_sentences(self):
        with given([]) as _:
            text = "maarĩ andũ 157,600. Acio nĩo mbakũri 20 cia thahabu."

        with when("it is cleaned"):
            result = clean_sentence(text)

        with then("it is unchanged"):
            assert_that(result, is_(equal_to(text)))
