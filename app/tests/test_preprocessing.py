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


class TestSubwordTokenizer(unittest.TestCase):
    def test_encode_splits_into_subword_pieces(self):
        """encode() should return the subword pieces for a sentence."""
        from unittest.mock import MagicMock, patch
        from app.api.preprocessing import SubwordTokenizer

        with given([]) as _:
            mock_sp = MagicMock()
            mock_sp.encode_as_pieces.return_value = ["▁ndi", "ga", "▁no", "ki"]

        with when("encoding a Kikuyu sentence"):
            with patch("sentencepiece.SentencePieceProcessor", return_value=mock_sp):
                tokenizer = SubwordTokenizer.__new__(SubwordTokenizer)
                tokenizer._sp = mock_sp
                pieces = tokenizer.encode("ndiga noki")

        with then("the sentence is split into subword pieces"):
            assert_that(pieces, is_(equal_to(["▁ndi", "ga", "▁no", "ki"])))

    def test_encode_returns_list_of_strings(self):
        """encode() output must always be a list of strings."""
        from unittest.mock import MagicMock
        from app.api.preprocessing import SubwordTokenizer

        with given([]) as _:
            mock_sp = MagicMock()
            mock_sp.encode_as_pieces.return_value = ["▁hello", "▁world"]
            tokenizer = SubwordTokenizer.__new__(SubwordTokenizer)
            tokenizer._sp = mock_sp

        with when("encoding any sentence"):
            result = tokenizer.encode("hello world")

        with then("the result is a list of strings"):
            assert isinstance(result, list)
            assert all(isinstance(p, str) for p in result)

    def test_decode_reconstructs_sentence(self):
        """decode() should rejoin subword pieces into a readable sentence."""
        from unittest.mock import MagicMock
        from app.api.preprocessing import SubwordTokenizer

        with given([]) as _:
            mock_sp = MagicMock()
            mock_sp.decode_pieces.return_value = "ndiga noki"
            tokenizer = SubwordTokenizer.__new__(SubwordTokenizer)
            tokenizer._sp = mock_sp

        with when("decoding a list of subword pieces"):
            result = tokenizer.decode(["▁ndi", "ga", "▁no", "ki"])

        with then("the original sentence is reconstructed"):
            assert_that(result, is_(equal_to("ndiga noki")))
