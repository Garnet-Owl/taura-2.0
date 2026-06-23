"""Unit tests for offline translation evaluation metrics."""

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
from givenpy import given, then, when
from hamcrest import assert_that, close_to, equal_to, is_

from app.api.embeddings import CrossLingualTranslator
from scripts.evaluate import (
    calculate_translation_scores,
    evaluate_retrieval_accuracy,
    load_all_parallel_csvs,
)
from scripts.train_embeddings import save_metrics


class TestLoadAllParallelCsvs(unittest.TestCase):
    def test_loads_kikuyu_and_english_columns(self):
        """Should parse CSV files with Kikuyu and English columns."""
        csv_content = "Reference,Kikuyu,English\n1:1,marigū,Bananas\n1:2,Kūrīma,Ploughing\n"

        with given([]) as _:
            mock_path = MagicMock()
            mock_path.glob.return_value = [mock_path / "test.csv"]
            mock_path.__truediv__ = lambda self, other: MagicMock(
                __str__=lambda s: "test.csv"
            )

        with when("loading parallel CSVs from a directory"):
            with (
                patch("pathlib.Path.glob") as mock_glob,
                patch(
                    "builtins.open",
                    return_value=io.StringIO(csv_content),
                ),
            ):
                mock_glob.return_value = [MagicMock(__str__=lambda s: "test.csv")]
                with tempfile.TemporaryDirectory() as tmpdir:
                    p = Path(tmpdir) / "test.csv"
                    p.write_text(csv_content, encoding="utf-8")
                    ki_sentences, en_sentences = load_all_parallel_csvs(tmpdir)

        with then("it parses into two aligned lists"):
            assert_that(ki_sentences, is_(equal_to(["marigū", "Kūrīma"])))
            assert_that(en_sentences, is_(equal_to(["Bananas", "Ploughing"])))

    def test_skips_rows_with_empty_fields(self):
        """Rows with empty Kikuyu or English should be silently skipped."""
        csv_content = (
            "Reference,Kikuyu,English\n1:1,,Bananas\n1:2,Kūrīma,\n1:3,marigū,Figs\n"
        )

        with given([]) as _:
            pass

        with when("loading a CSV that has some empty rows"):
            with tempfile.TemporaryDirectory() as tmpdir:
                p = Path(tmpdir) / "data.csv"
                p.write_text(csv_content, encoding="utf-8")
                ki_sentences, en_sentences = load_all_parallel_csvs(tmpdir)

        with then("only fully-populated rows are returned"):
            assert_that(len(ki_sentences), is_(equal_to(1)))
            assert_that(ki_sentences[0], is_(equal_to("marigū")))


class TestCalculateTranslationScores(unittest.TestCase):
    def test_perfect_match_returns_high_scores(self):
        """Identical hypotheses and references should return BLEU and ChrF near 100."""
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


class TestEvaluateRetrievalAccuracy(unittest.TestCase):
    def test_perfect_alignment_gives_top1_of_one(self):
        """When projection is identity and embeddings are perfectly aligned, Top-1 should be 1.0."""
        with given([]) as _:
            mock_src = MagicMock()
            mock_tgt = MagicMock()
            W = np.eye(3)

            # Three sentence pairs with distinct, well-separated embeddings
            tgt_sentences = ["a", "b", "c"]
            tgt_embs = np.array(
                [
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0],
                ],
                dtype=np.float32,
            )

            translator = CrossLingualTranslator(
                src_model=mock_src,
                tgt_model=mock_tgt,
                projection_matrix=W,
                tgt_sentences=tgt_sentences,
                precomputed_tgt_embeddings=tgt_embs,
            )

            # Source embeddings match the target embeddings exactly
            src_sentences = ["x", "y", "z"]
            src_embs = {
                "x": np.array([1.0, 0.0, 0.0], dtype=np.float32),
                "y": np.array([0.0, 1.0, 0.0], dtype=np.float32),
                "z": np.array([0.0, 0.0, 1.0], dtype=np.float32),
            }
            mock_src.get_word_vector.side_effect = lambda w: src_embs.get(
                w, np.zeros(3, dtype=np.float32)
            )

        with when("evaluating retrieval accuracy on a perfectly aligned set"):
            metrics = evaluate_retrieval_accuracy(translator, src_sentences, tgt_sentences)

        with then("Top-1, Top-5, and MRR are all 1.0"):
            assert_that(metrics["accuracy_top1"], is_(equal_to(1.0)))
            assert_that(metrics["accuracy_top5"], is_(equal_to(1.0)))
            assert_that(metrics["mrr"], is_(close_to(1.0, delta=1e-6)))

    def test_random_alignment_gives_low_accuracy(self):
        """Random projection should give near-zero Top-1 accuracy on non-trivial data."""
        with given([]) as _:
            np.random.seed(99)
            mock_src = MagicMock()
            mock_tgt = MagicMock()
            W = np.eye(4)

            n = 20
            tgt_embs = np.random.randn(n, 4).astype(np.float32)
            tgt_sentences = [str(i) for i in range(n)]
            src_sentences = [str(i) for i in range(n)]

            translator = CrossLingualTranslator(
                src_model=mock_src,
                tgt_model=mock_tgt,
                projection_matrix=W,
                tgt_sentences=tgt_sentences,
                precomputed_tgt_embeddings=tgt_embs,
            )
            # Each source sentence gets a completely different random vector
            src_vecs = np.random.randn(n, 4).astype(np.float32)
            mock_src.get_word_vector.side_effect = lambda w: src_vecs[int(w)]

        with when("evaluating with misaligned source and target embeddings"):
            metrics = evaluate_retrieval_accuracy(translator, src_sentences, tgt_sentences)

        with then("accuracy is below 0.5"):
            assert_that(metrics["accuracy_top1"] < 0.5, is_(True))
            assert_that(0.0 <= metrics["mrr"] <= 1.0, is_(True))


class TestSaveMetrics(unittest.TestCase):
    def test_merges_without_overwriting_existing_keys(self):
        """Should merge new metrics with existing metrics without overwriting unrelated keys."""
        with given([]) as _:
            existing_data = {
                "kikuyu_to_english": {"bleu_retrieval": 15.0},
                "english_to_kikuyu": {"chrf_word_by_word": 20.0},
            }
            new_metrics = {
                "kikuyu_to_english": {"accuracy_top1": 0.5},
                "english_to_kikuyu": {"accuracy_top1": 0.6},
            }

        with when("saving new metrics over existing ones"):
            with (
                patch("os.path.exists", return_value=True),
                patch("builtins.open", MagicMock()),
                patch("json.load", return_value=existing_data.copy()),
                patch("json.dump") as mock_dump,
            ):
                save_metrics(new_metrics, "dummy_metrics.json")

        with then("both old and new keys are present in the saved data"):
            mock_dump.assert_called_once()
            saved = mock_dump.call_args[0][0]
            assert_that(saved["kikuyu_to_english"]["bleu_retrieval"], is_(equal_to(15.0)))
            assert_that(saved["kikuyu_to_english"]["accuracy_top1"], is_(equal_to(0.5)))
            assert_that(
                saved["english_to_kikuyu"]["chrf_word_by_word"], is_(equal_to(20.0))
            )
            assert_that(saved["english_to_kikuyu"]["accuracy_top1"], is_(equal_to(0.6)))
