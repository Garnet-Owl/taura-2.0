"""Unit tests for the CTranslate2 Marian neural translator wrapper."""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.api.neural import DirectionModel, NeuralTranslator


def _fake_sentencepiece() -> MagicMock:
    sp = MagicMock()
    sp.encode.side_effect = lambda texts, out_type: [t.split() for t in texts]
    sp.decode.side_effect = lambda pieces: [" ".join(p) for p in pieces]
    return sp


def _direction(output_tokens: list[str], prefix: list[str]) -> DirectionModel:
    ct2 = MagicMock()
    ct2.translate_batch.return_value = [SimpleNamespace(hypotheses=[output_tokens])]
    return DirectionModel(ct2, _fake_sentencepiece(), _fake_sentencepiece(), prefix)


class TestNeuralTranslator(unittest.TestCase):
    def test_kikuyu_to_english_uses_ki_en_model(self):
        """Ki->En encodes the source with </s> and decodes the hypothesis."""
        with given([]) as _:
            ki_en = _direction(["In", "the", "beginning"], [])
            en_ki = _direction(["unused"], [">>swh<<"])
            translator = NeuralTranslator({"ki_en": ki_en, "en_ki": en_ki}, beam_size=2)

        with when("translating Kikuyu to English"):
            result = translator.translate("Kĩambĩrĩria-inĩ", "ki", "en")

        with then("the ki_en model sees the tokens and the result is clean text"):
            args, kwargs = ki_en.translator.translate_batch.call_args
            assert_that(args[0], is_(equal_to([["Kĩambĩrĩria-inĩ", "</s>"]])))
            assert_that(kwargs["beam_size"], is_(equal_to(2)))
            assert_that(result, is_(equal_to("In the beginning")))
            en_ki.translator.translate_batch.assert_not_called()

    def test_english_to_kikuyu_adds_target_language_tag(self):
        """En->Ki prefixes the source with the language tag used in fine-tuning."""
        with given([]) as _:
            en_ki = _direction(["Mwathani"], [">>swh<<"])
            translator = NeuralTranslator({"ki_en": _direction([], []), "en_ki": en_ki})

        with when("translating English to Kikuyu"):
            result = translator.translate("Lord", "en", "ki")

        with then("the tag leads the source tokens"):
            args, _ = en_ki.translator.translate_batch.call_args
            assert_that(args[0], is_(equal_to([[">>swh<<", "Lord", "</s>"]])))
            assert_that(result, is_(equal_to("Mwathani")))

    def test_rejects_unsupported_direction(self):
        """Only Kikuyu <-> English is supported."""
        with given([]) as _:
            translator = NeuralTranslator({"ki_en": _direction([], [])})

        with when("translating from French"):

            def action():
                translator.translate("Bonjour", "fr", "en")

        with then("a ValueError is raised"):
            self.assertRaises(ValueError, action)
