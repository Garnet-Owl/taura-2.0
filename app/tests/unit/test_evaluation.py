"""Unit tests for offline translation evaluation metrics."""

import unittest
from unittest.mock import MagicMock, patch
from givenpy import given, then, when
from hamcrest import assert_that, equal_to, has_key, is_

# We will import the evaluation functions from scripts.evaluate
# Since scripts.evaluate does not exist yet, this test will fail on import
from scripts.evaluate import calculate_translation_scores, load_test_data


class TestEvaluation(unittest.TestCase):
    def test_load_test_data(self):
        """Should parse a TSV file with Kikuyu and English sentence pairs."""
        with given([]) as _:
            # Mock file content
            mock_tsv_content = "kikuyu\tenglish\nmarigū\tBananas\nKūrīma\tPloughing\n"
            mock_open = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_tsv_content.splitlines()

        with when("loading the test data"):
            with patch("builtins.open", mock_open), \
                 patch("os.path.exists", return_value=True):
                ki_sentences, en_sentences = load_test_data("dummy_path.tsv")

        with then("it parses into two aligned lists of sentences"):
            assert_that(ki_sentences, is_(equal_to(["marigū", "Kūrīma"])))
            assert_that(en_sentences, is_(equal_to(["Bananas", "Ploughing"])))

    def test_calculate_translation_scores(self):
        """Should compute BLEU and ChrF scores using sacrebleu."""
        with given([]) as _:
            translations = ["Bananas", "Ploughing"]
            references = ["Bananas", "Ploughing"]

            mock_bleu = MagicMock()
            mock_bleu.score = 100.0
            mock_chrf = MagicMock()
            mock_chrf.score = 100.0

        with when("calculating translation scores"):
            with patch("sacrebleu.corpus_bleu", return_value=mock_bleu) as patched_bleu, \
                 patch("sacrebleu.corpus_chrf", return_value=mock_chrf) as patched_chrf:
                bleu_score, chrf_score = calculate_translation_scores(translations, references)

        with then("it returns the scores from sacrebleu"):
            assert_that(bleu_score, is_(equal_to(100.0)))
            assert_that(chrf_score, is_(equal_to(100.0)))
            patched_bleu.assert_called_once_with(translations, [references])
            patched_chrf.assert_called_once_with(translations, [references])
