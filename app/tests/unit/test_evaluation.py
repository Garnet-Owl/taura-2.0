"""Unit tests for offline translation evaluation metrics."""

import unittest
from unittest.mock import MagicMock, patch
from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

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
            mock_open.return_value.__enter__.return_value = (
                mock_tsv_content.splitlines()
            )

        with when("loading the test data"):
            with (
                patch("builtins.open", mock_open),
                patch("os.path.exists", return_value=True),
            ):
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
            with (
                patch("sacrebleu.corpus_bleu", return_value=mock_bleu) as patched_bleu,
                patch("sacrebleu.corpus_chrf", return_value=mock_chrf) as patched_chrf,
            ):
                bleu_score, chrf_score = calculate_translation_scores(
                    translations, references
                )

        with then("it returns the scores from sacrebleu"):
            assert_that(bleu_score, is_(equal_to(100.0)))
            assert_that(chrf_score, is_(equal_to(100.0)))
            patched_bleu.assert_called_once_with(translations, [references])
            patched_chrf.assert_called_once_with(translations, [references])

    def test_save_metrics_merges_data(self):
        """Should merge new metrics with existing metrics without overwriting unrelated keys."""
        from scripts.train_embeddings import save_metrics
        import json
        
        with given([]) as _:
            existing_data = {
                "kikuyu_to_english": {"bleu_retrieval": 15.0},
                "english_to_kikuyu": {"chrf_word_by_word": 20.0}
            }

            new_metrics = {
                "kikuyu_to_english": {"accuracy_top1": 0.5},
                "english_to_kikuyu": {"accuracy_top1": 0.6}
            }

        with when("saving new metrics"):
            with (
                patch("os.path.exists", return_value=True),
                patch("builtins.open", MagicMock()),
                patch("json.load", return_value=existing_data.copy()),
                patch("json.dump") as mock_dump
            ):
                save_metrics(new_metrics, "dummy_metrics.json")
                
        with then("it merges both metrics"):
            mock_dump.assert_called_once()
            saved_data = mock_dump.call_args[0][0]
            
            assert_that(saved_data["kikuyu_to_english"]["bleu_retrieval"], is_(equal_to(15.0)))
            assert_that(saved_data["kikuyu_to_english"]["accuracy_top1"], is_(equal_to(0.5)))
            assert_that(saved_data["english_to_kikuyu"]["chrf_word_by_word"], is_(equal_to(20.0)))
            assert_that(saved_data["english_to_kikuyu"]["accuracy_top1"], is_(equal_to(0.6)))

