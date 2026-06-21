"""Unit tests for text preprocessing."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.api.preprocessing import normalize_text, tokenize_text


class TestPreprocessing(unittest.TestCase):
    def test_normalize_text_lowercases(self):
        """Text should be lowercased."""
        with given([]) as _:
            text = "HeLLo WoRLd"

        with when("normalizing text"):
            result = normalize_text(text)

        with then("the text is completely lowercased"):
            assert_that(result, is_(equal_to("hello world")))

    def test_normalize_text_removes_punctuation(self):
        """Punctuation should be removed from text."""
        with given([]) as _:
            text = "Hello, world! This is a test."

        with when("normalizing text"):
            result = normalize_text(text)

        with then("punctuation is removed and text is lowercased"):
            assert_that(result, is_(equal_to("hello world this is a test")))

    def test_normalize_text_handles_extra_spaces(self):
        """Extra spaces should be stripped and condensed."""
        with given([]) as _:
            text = "  hello   world  "

        with when("normalizing text"):
            result = normalize_text(text)

        with then("extra spaces are removed"):
            assert_that(result, is_(equal_to("hello world")))

    def test_tokenize_text(self):
        """Text should be tokenized by spaces."""
        with given([]) as _:
            text = "hello world this is a test"

        with when("tokenizing text"):
            result = tokenize_text(text)

        with then("the text is split into a list of words"):
            assert_that(
                result, is_(equal_to(["hello", "world", "this", "is", "a", "test"]))
            )

    def test_tokenize_text_empty(self):
        """Empty text should return an empty list."""
        with given([]) as _:
            text = ""

        with when("tokenizing empty text"):
            result = tokenize_text(text)

        with then("an empty list is returned"):
            assert_that(result, is_(equal_to([])))

