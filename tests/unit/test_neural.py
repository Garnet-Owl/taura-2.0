"""Unit tests for the CTranslate2 neural translator wrapper."""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.api.neural import NeuralTranslator


def _fake_sentencepiece() -> MagicMock:
    sp = MagicMock()
    sp.encode.side_effect = lambda texts, out_type: [t.split() for t in texts]
    sp.decode.side_effect = lambda pieces: [" ".join(p) for p in pieces]
    return sp


class TestNeuralTranslator(unittest.TestCase):
    def test_adds_nllb_language_tags_and_strips_target_tag(self):
        """Source gets the NLLB language tag and </s>; output drops the target tag."""
        with given([]) as _:
            ct2 = MagicMock()
            ct2.translate_batch.return_value = [
                SimpleNamespace(hypotheses=[["eng_Latn", "In", "the", "beginning"]])
            ]
            translator = NeuralTranslator(ct2, _fake_sentencepiece(), beam_size=2)

        with when("translating Kikuyu to English"):
            result = translator.translate("Kĩambĩrĩria-inĩ", "ki", "en")

        with then("the model sees tagged tokens and the result is clean text"):
            args, kwargs = ct2.translate_batch.call_args
            assert_that(args[0], is_(equal_to([["kik_Latn", "Kĩambĩrĩria-inĩ", "</s>"]])))
            assert_that(kwargs["target_prefix"], is_(equal_to([["eng_Latn"]])))
            assert_that(kwargs["beam_size"], is_(equal_to(2)))
            assert_that(result, is_(equal_to("In the beginning")))

    def test_rejects_unsupported_language(self):
        """Only 'ki' and 'en' are supported."""
        with given([]) as _:
            translator = NeuralTranslator(MagicMock(), _fake_sentencepiece())

        with when("translating from French"):

            def action():
                translator.translate("Bonjour", "fr", "en")

        with then("a ValueError is raised"):
            self.assertRaises(ValueError, action)
