"""CPU inference for a fine-tuned NLLB model exported to CTranslate2 (int8).

The model directory must hold the CTranslate2 export plus the NLLB
SentencePiece file ``sentencepiece.bpe.model``.
"""

import os
from typing import Any

import ctranslate2
import sentencepiece as spm

LANG_CODES: dict[str, str] = {"ki": "kik_Latn", "en": "eng_Latn"}
SPM_FILENAME = "sentencepiece.bpe.model"
MAX_DECODING_LENGTH = 256


class NeuralTranslator:
    """Translates Kikuyu <-> English with a CTranslate2 NLLB model."""

    def __init__(self, translator: Any, sp_processor: Any, beam_size: int = 4) -> None:
        self.translator = translator
        self.sp = sp_processor
        self.beam_size = beam_size

    @classmethod
    def load(cls, model_dir: str, threads: int = 0) -> "NeuralTranslator":
        """Loads the int8 CTranslate2 model and its SentencePiece tokenizer on CPU."""
        translator = ctranslate2.Translator(
            model_dir, device="cpu", compute_type="int8", intra_threads=threads
        )
        sp = spm.SentencePieceProcessor(model_file=os.path.join(model_dir, SPM_FILENAME))
        return cls(translator, sp)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translates one sentence between 'ki' and 'en'."""
        return self.translate_batch([text], source_lang, target_lang)[0]

    def translate_batch(
        self, texts: list[str], source_lang: str, target_lang: str
    ) -> list[str]:
        """Translates a batch of sentences between 'ki' and 'en'."""
        if source_lang not in LANG_CODES or target_lang not in LANG_CODES:
            raise ValueError("Supported language codes are 'ki' and 'en'.")
        src_tag, tgt_tag = LANG_CODES[source_lang], LANG_CODES[target_lang]
        pieces = self.sp.encode(texts, out_type=str)
        sources = [[src_tag, *p, "</s>"] for p in pieces]
        results = self.translator.translate_batch(
            sources,
            target_prefix=[[tgt_tag]] * len(sources),
            beam_size=self.beam_size,
            max_decoding_length=MAX_DECODING_LENGTH,
        )
        hypotheses = [r.hypotheses[0][1:] for r in results]
        return self.sp.decode(hypotheses)
