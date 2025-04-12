import unittest

from app.api.embedding.processor import TextProcessor
from app.tests.givenpy import given, then, when


class TestTextProcessor(unittest.TestCase):
    """Test suite for the TextProcessor class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Set up sample stopwords
        self.english_stopwords = {"the", "a", "an", "in", "on", "at", "of"}
        self.kikuyu_stopwords = {"nĩ", "na", "kũ"}

        # Create a processor with stopwords
        self.processor_with_stopwords = TextProcessor(
            {
                "english": self.english_stopwords,
                "kikuyu": self.kikuyu_stopwords,
            }
        )

        # Create a processor without stopwords
        self.processor_no_stopwords = TextProcessor()

    def test_normalize_text(self):
        """
        Given a TextProcessor
        When normalize_text is called with various inputs
        Then the text should be properly normalized
        """
        with given():
            processor = self.processor_no_stopwords
            test_cases = [
                # Input, Expected Output
                ("HELLO WORLD", "hello world"),
                ("  Multiple   Spaces  ", "multiple spaces"),
                ("Unicode\u00a0Character", "unicode character"),
                ("", ""),  # Empty string
                (None, ""),  # None
                (123, ""),  # Non-string
                ("Line\nBreak", "line break"),
                ("Special@#$Characters", "special@#$characters"),
            ]

        for input_text, expected_output in test_cases:
            with when(f"normalizing text: '{input_text}'"):
                result = processor.normalize_text(input_text)

            with then(f"the result should be: '{expected_output}'"):
                assert result == expected_output

    def test_tokenize(self):
        """
        Given a TextProcessor
        When tokenize is called with different languages
        Then the text should be properly tokenized
        """
        with given():
            processor = self.processor_no_stopwords

        with when("tokenizing English text"):
            english_text = "The quick brown fox jumps over the lazy dog"
            english_tokens = processor.tokenize(english_text, "english")

        with then("the text should be properly tokenized"):
            expected_tokens = [
                "the",
                "quick",
                "brown",
                "fox",
                "jumps",
                "over",
                "the",
                "lazy",
                "dog",
            ]
            assert english_tokens == expected_tokens

        with when("tokenizing Kikuyu text"):
            kikuyu_text = "Nĩ mwega gũkũona"
            kikuyu_tokens = processor.tokenize(kikuyu_text, "kikuyu")

        with then("the text should be properly tokenized"):
            expected_tokens = ["nĩ", "mwega", "gũkũona"]
            assert kikuyu_tokens == expected_tokens

    def test_remove_stopwords(self):
        """
        Given a TextProcessor with stopwords
        When remove_stopwords is called
        Then stopwords should be removed from the tokens
        """
        with given():
            processor = self.processor_with_stopwords
            english_tokens = [
                "the",
                "quick",
                "brown",
                "fox",
                "jumps",
                "over",
                "the",
                "lazy",
                "dog",
            ]
            kikuyu_tokens = ["nĩ", "mwega", "na", "kũ", "gũkũona"]

        with when("removing English stopwords"):
            filtered_english = processor.remove_stopwords(english_tokens, "english")

        with then("stopwords should be removed"):
            expected_english = ["quick", "brown", "fox", "jumps", "over", "lazy", "dog"]
            assert filtered_english == expected_english

        with when("removing Kikuyu stopwords"):
            filtered_kikuyu = processor.remove_stopwords(kikuyu_tokens, "kikuyu")

        with then("stopwords should be removed"):
            expected_kikuyu = ["mwega", "gũkũona"]
            assert filtered_kikuyu == expected_kikuyu

        with when("removing stopwords for non-existent language"):
            filtered_other = processor.remove_stopwords(english_tokens, "french")

        with then("no stopwords should be removed"):
            assert filtered_other == english_tokens

    def test_prepare_for_fasttext(self):
        """
        Given a TextProcessor
        When prepare_for_fasttext is called
        Then texts should be processed correctly for FastText training
        """
        with given():
            processor = self.processor_with_stopwords
            english_texts = [
                "The quick brown fox",
                "Jumps over THE lazy dog",
                "",  # Empty string
            ]

        with when("preparing English texts without removing stopwords"):
            processed_english = processor.prepare_for_fasttext(
                english_texts, "english", remove_stopwords=False
            )

        with then("texts should be normalized but keep stopwords"):
            expected_english = [
                "the quick brown fox",
                "jumps over the lazy dog",
            ]
            assert processed_english == expected_english

        with when("preparing English texts and removing stopwords"):
            processed_english = processor.prepare_for_fasttext(
                english_texts, "english", remove_stopwords=True
            )

        with then("texts should be normalized and stopwords removed"):
            expected_english = [
                "quick brown fox",
                "jumps over lazy dog",
            ]
            assert processed_english == expected_english


if __name__ == "__main__":
    unittest.main()
