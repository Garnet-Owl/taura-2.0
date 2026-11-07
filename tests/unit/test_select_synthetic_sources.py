"""Unit tests for picking the next English sentences to translate."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, contains_exactly, equal_to, is_

from scripts.select_synthetic_sources import is_usable, jaccard, select


class TestSelect(unittest.TestCase):
    def test_skips_used_ids_known_sentences_and_near_duplicates(self) -> None:
        with given([]) as _:
            rows = [
                ("1", "We should look after our parents."),
                ("2", "We should look after our parents well."),
                ("3", "The children are brushing their teeth."),
                ("4", "Do you want to have some tea?"),
                ("5", "Do you want some coffee or something?"),
            ]
        with when("selecting with id 3 used and the tea sentence known"):
            chosen = select(rows, {"tatoeba:3"}, {"do you want to have some tea"}, 10)
        with then("only fresh, distinct sentences remain"):
            texts = {text for _, text in chosen}
            assert_that("The children are brushing their teeth." in texts, is_(False))
            assert_that("Do you want to have some tea?" in texts, is_(False))
            assert_that(
                len(texts & {rows[0][1], rows[1][1]}), equal_to(1)
            )  # near duplicates

    def test_is_usable_filters_length_and_blocked_words(self) -> None:
        with given([]) as _:
            cases = [
                "Hi there.",
                "This is a good sentence for us.",
                "What the shit is this?",
            ]
        with when("checking each"):
            results = [is_usable(c) for c in cases]
        with then("only the middle one passes"):
            assert_that(results, contains_exactly(False, True, False))

    def test_jaccard_of_identical_sets_is_one(self) -> None:
        with given([]) as _:
            words = {"a", "b"}
        with then("similarity is 1"):
            assert_that(jaccard(words, words), equal_to(1.0))
