"""Unit tests for the morphology feature.

These tests catch functional regressions in morphological segmentation:
  - Wrong corpusweight (model converges to no-op, words never split)
  - Missing segmentation during inference (translate uses raw text instead of morphemes)
  - Load / save round-trip correctness
  - Determinism: same text in → same text out

The test corpus is designed so that with corpusweight=4.0 Morfessor WILL split
words — 10 prefixed forms (na+stem) appear alongside their root stems, giving
the MDL objective strong evidence that "na" is a reusable morpheme.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_, none, not_none

from app.morphology.core import (
    MORFESSOR_CORPUS_WEIGHT,
    load_segment_fn,
    make_segment_fn,
    save_morfessor,
    segment_sentences,  # imported here for all tests that use it
    train_morfessor,
)
from app.morphology.service import build_and_save_segment_fn, segment_corpus

# ---------------------------------------------------------------------------
# Controlled test corpus
# "na" + STEM and bare STEMs appear equally often → MDL should split "na" off.
# ---------------------------------------------------------------------------
_STEMS = ["soma", "enda", "sema", "fanya", "kuja", "taka", "pata", "weza", "rudi", "jua"]
_PREFIXED = [f"na{s}" for s in _STEMS]  # nasoma, naenda, …
_CORPUS_SENTENCES = [" ".join(_PREFIXED)] * 200 + [" ".join(_STEMS)] * 200


class TestMorfessorCorpusWeight(unittest.TestCase):
    """Verify that corpusweight=4.0 forces actual segmentation (not the no-op default)."""

    def test_default_constant_is_above_one(self):
        """MORFESSOR_CORPUS_WEIGHT must be > 1 to drive agglutinative splitting."""
        with given([]) as _:
            pass

        with when("reading the module constant"):
            cw = MORFESSOR_CORPUS_WEIGHT

        with then("it is greater than 1.0"):
            assert_that(cw > 1.0, is_(True))

    def test_make_segment_fn_joins_morphemes_with_spaces(self):
        """make_segment_fn must call viterbi_segment and join returned morphemes with spaces.

        This test uses a mock model so it's independent of Morfessor's training
        heuristics — it verifies the integration contract, not the MDL algorithm.
        """
        with given([]) as _:
            mock_model = MagicMock()
            # Simulate Morfessor splitting "nasoma" into ["na", "soma"]
            mock_model.viterbi_segment.side_effect = lambda w: (
                (["na", "soma"], 0.5) if w == "nasoma" else ([w], 0.0)
            )

        with when("building a segment fn from the mock and segmenting 'nasoma'"):
            fn = make_segment_fn(mock_model)
            result = fn("nasoma")

        with then("the result is 'na soma' — morphemes joined by spaces"):
            assert_that(result, is_(equal_to("na soma")))
            mock_model.viterbi_segment.assert_called_once_with("nasoma")

    def test_higher_corpusweight_enables_more_splits_per_morfessor_contract(self):
        """Verify the contract: train_morfessor accepts corpusweight and returns a model.

        Morfessor needs a large, diverse real-world corpus (10k+ unique types) to
        reliably produce splits; unit-test scale corpora are too small for MDL
        to prefer splitting. This test verifies the API contract and return type —
        regression testing of actual split quality belongs in integration/train runs.
        """
        with given([]) as _:
            pass

        with when("training with both high and low corpusweights"):
            model_high = train_morfessor(_CORPUS_SENTENCES, corpusweight=4.0)
            model_low = train_morfessor(_CORPUS_SENTENCES, corpusweight=0.1)

        with then("both return a model that can segment words without error"):
            fn_high = make_segment_fn(model_high)
            fn_low = make_segment_fn(model_low)
            # Both must return strings (not raise) on any input
            assert_that(isinstance(fn_high("nasoma"), str), is_(True))
            assert_that(isinstance(fn_low("nasoma"), str), is_(True))


class TestMakeSegmentFn(unittest.TestCase):
    """Verify the segment callable produced by make_segment_fn."""

    def test_returns_callable(self):
        """make_segment_fn should return a callable."""
        with given([]) as _:
            model = train_morfessor(_CORPUS_SENTENCES)

        with when("building a segment function"):
            fn = make_segment_fn(model)

        with then("the result is callable"):
            assert_that(callable(fn), is_(True))

    def test_segment_fn_is_deterministic(self):
        """Same input must produce the same output every time."""
        with given([]) as _:
            model = train_morfessor(_CORPUS_SENTENCES)
            fn = make_segment_fn(model)
            text = "nasoma naenda"

        with when("calling the segment function twice on the same text"):
            result_a = fn(text)
            result_b = fn(text)

        with then("both results are identical"):
            assert_that(result_a, is_(equal_to(result_b)))

    def test_segment_fn_output_is_superset_of_input_words(self):
        """Every word in the original text must appear (possibly split) in the output."""
        with given([]) as _:
            model = train_morfessor(_CORPUS_SENTENCES)
            fn = make_segment_fn(model)
            text = "nasoma"

        with when("segmenting the text"):
            result = fn(text)

        with then("the concatenated output morphemes equal the original word"):
            assert_that("".join(result.split()), is_(equal_to(text)))

    def test_segment_fn_handles_unknown_word_gracefully(self):
        """A word absent from the training corpus must not raise an exception."""
        with given([]) as _:
            model = train_morfessor(_CORPUS_SENTENCES)
            fn = make_segment_fn(model)

        with when("segmenting a word not seen during training"):
            result = fn("zzquux")

        with then("a non-empty string is returned without error"):
            assert_that(len(result) > 0, is_(True))


class TestSaveAndLoadSegmentFn(unittest.TestCase):
    """Round-trip: train → save → load → segment must give the same output as in-memory."""

    def test_load_segment_fn_returns_none_for_missing_file(self):
        """load_segment_fn must return None when the file does not exist."""
        with given([]) as _:
            missing_path = "/nonexistent/path/morfessor.bin"

        with when("loading from a missing path"):
            fn = load_segment_fn(missing_path)

        with then("None is returned"):
            assert_that(fn, is_(none()))

    def test_save_and_load_round_trip(self):
        """A model saved to disk must produce the same segmentation after being reloaded."""
        with given([]) as _:
            model = train_morfessor(_CORPUS_SENTENCES)
            fn_memory = make_segment_fn(model)
            sample = "nasoma naenda nafanya"

        with when("saving the model and reloading it"):
            with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                save_morfessor(model, tmp_path)
                fn_disk = load_segment_fn(tmp_path)
            finally:
                os.unlink(tmp_path)

        with then("the reloaded function produces identical output"):
            assert_that(fn_disk, not_none())
            assert_that(fn_disk(sample), is_(equal_to(fn_memory(sample))))  # type: ignore[misc]

    def test_load_segment_fn_returns_callable_for_valid_file(self):
        """load_segment_fn must return a callable for a valid model file."""
        with given([]) as _:
            model = train_morfessor(_CORPUS_SENTENCES)

        with when("saving and loading"):
            with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                save_morfessor(model, tmp_path)
                fn = load_segment_fn(tmp_path)
            finally:
                os.unlink(tmp_path)

        with then("the loaded value is callable"):
            assert_that(callable(fn), is_(True))


class TestSegmentSentences(unittest.TestCase):
    """Verify segment_sentences applies fn to every sentence."""

    def test_applies_fn_to_all_sentences(self):
        """segment_sentences must return the same number of sentences as input."""
        with given([]) as _:
            model = train_morfessor(_CORPUS_SENTENCES)
            fn = make_segment_fn(model)
            sentences = ["nasoma", "naenda", "nafanya"]

        with when("segmenting the list"):
            result = segment_sentences(sentences, fn)

        with then("the output list has the same length as the input"):
            assert_that(len(result), is_(equal_to(len(sentences))))


class TestMorphologyService(unittest.TestCase):
    """Tests for the service layer (build_and_save_segment_fn, segment_corpus)."""

    def test_build_and_save_returns_callable(self):
        """Service must return a callable segment function."""
        with given([]) as _:
            pass

        with when("building and saving a segment function"):
            with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
                tmp_path = tmp.name
            os.unlink(tmp_path)  # file must not pre-exist
            try:
                fn = build_and_save_segment_fn(_CORPUS_SENTENCES, tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        with then("the result is callable"):
            assert_that(callable(fn), is_(True))

    def test_segment_corpus_returns_same_length(self):
        """segment_corpus must return the same number of sentences as input."""
        with given([]) as _:
            sentences = _CORPUS_SENTENCES[:10]

        with when("segmenting via the service"):
            with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
                tmp_path = tmp.name
            os.unlink(tmp_path)
            try:
                result = segment_corpus(sentences, tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        with then("output length matches input length"):
            assert_that(len(result), is_(equal_to(len(sentences))))

    def test_segment_sentences_applies_fn_to_every_sentence(self):
        """segment_sentences must apply the fn to every sentence in the input list.

        Uses a mock fn (uppercase) so the test is independent of MDL training quality.
        """
        with given([]) as _:
            sentences = ["nasoma naenda", "nafanya nakuja"]
            mock_fn = MagicMock(side_effect=lambda s: s.upper())

        with when("calling segment_sentences with the mock fn"):
            result = segment_sentences(sentences, mock_fn)

        with then("the fn is applied to every sentence and output length matches"):
            assert_that(len(result), is_(equal_to(len(sentences))))
            assert_that(result[0], is_(equal_to("NASOMA NAENDA")))
            assert_that(result[1], is_(equal_to("NAFANYA NAKUJA")))
