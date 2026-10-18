"""CPU inference for fine-tuned Marian (opus-mt) models exported to CTranslate2 int8.

The model directory holds one sub-folder per direction (``ki_en`` and ``en_ki``),
each with the CTranslate2 export plus ``source.spm`` and ``target.spm``.
Download it from the Hugging Face repo Garnet-Owl/taura-marian-kikuyu-english
(the ``<direction>/ct2-int8`` folders).
"""

import os
from dataclasses import dataclass
from typing import Any

import ctranslate2
import sentencepiece as spm

# English->Kikuyu reuses the Swahili target tag of opus-mt-en-mul, as in fine-tuning.
DIRECTION_PREFIXES: dict[str, list[str]] = {"ki_en": [], "en_ki": [">>swh<<"]}
MAX_DECODING_LENGTH = 256


@dataclass
class DirectionModel:
    """One translation direction: model, tokenizers and source prefix tokens."""

    translator: Any
    source_sp: Any
    target_sp: Any
    prefix: list[str]


def load_direction(
    direction_dir: str, prefix: list[str], threads: int = 0
) -> DirectionModel:
    """Loads one int8 CTranslate2 Marian model and its SentencePiece files on CPU."""
    translator = ctranslate2.Translator(
        direction_dir, device="cpu", compute_type="int8", intra_threads=threads
    )
    source_sp = spm.SentencePieceProcessor(
        model_file=os.path.join(direction_dir, "source.spm")
    )
    target_sp = spm.SentencePieceProcessor(
        model_file=os.path.join(direction_dir, "target.spm")
    )
    return DirectionModel(translator, source_sp, target_sp, prefix)


class NeuralTranslator:
    """Translates Kikuyu <-> English with one Marian model per direction."""

    def __init__(self, models: dict[str, DirectionModel], beam_size: int = 4) -> None:
        self.models = models
        self.beam_size = beam_size

    @classmethod
    def load(cls, model_dir: str, threads: int = 0) -> "NeuralTranslator":
        """Loads every direction found under model_dir."""
        models = {
            name: load_direction(os.path.join(model_dir, name), prefix, threads)
            for name, prefix in DIRECTION_PREFIXES.items()
            if os.path.isdir(os.path.join(model_dir, name))
        }
        return cls(models)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translates one sentence between 'ki' and 'en'."""
        return self.translate_batch([text], source_lang, target_lang)[0]

    def translate_batch(
        self, texts: list[str], source_lang: str, target_lang: str
    ) -> list[str]:
        """Translates a batch of sentences between 'ki' and 'en'."""
        model = self.models.get(f"{source_lang}_{target_lang}")
        if model is None:
            raise ValueError(f"No neural model for {source_lang} to {target_lang}.")
        pieces = model.source_sp.encode(texts, out_type=str)
        sources = [[*model.prefix, *p, "</s>"] for p in pieces]
        results = model.translator.translate_batch(
            sources, beam_size=self.beam_size, max_decoding_length=MAX_DECODING_LENGTH
        )
        return model.target_sp.decode([r.hypotheses[0] for r in results])
