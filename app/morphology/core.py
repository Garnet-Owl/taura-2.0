"""Morfessor-based morphological segmentation for agglutinative Kikuyu text.

Morfessor's MDL criterion: total cost = corpusweight * corpus_cost + lexicon_cost.
Higher corpusweight penalises long per-word morpheme sequences, so the optimum
shifts toward shorter, reusable morphemes — exactly what Bantu agglutination needs.
"""

import os
from typing import Any, Callable

from app.shared.logger import setup_logger

logger = setup_logger(__name__)

# Calibrated for Bantu agglutination: forces the MDL objective to prefer
# splitting common prefixes (mũ-, a-, ka-, gũ-) over keeping whole word-forms.
MORFESSOR_CORPUS_WEIGHT: float = 4.0


def train_morfessor(
    sentences: list[str],
    corpusweight: float = MORFESSOR_CORPUS_WEIGHT,
) -> Any:
    """Train a Morfessor model on raw sentences and return it.

    Builds a word-frequency table from the sentences, feeds it to Morfessor's
    batch trainer via the documented two-step API (load_data then train_batch),
    and returns the trained model.
    """
    import morfessor  # PLC0415

    model = morfessor.BaselineModel(corpusweight=corpusweight)
    word_counts: dict[str, int] = {}
    for sent in sentences:
        for word in sent.lower().split():
            word_counts[word] = word_counts.get(word, 0) + 1

    train_data = [(count, word) for word, count in word_counts.items()]
    model.load_data(train_data)
    model.train_batch()
    logger.info("Morfessor trained on %d unique word types.", len(word_counts))
    return model


def save_morfessor(model: object, path: str) -> None:
    """Persist a trained Morfessor model to a binary file."""
    import morfessor  # PLC0415

    morfessor.MorfessorIO().write_binary_file(path, model)


def make_segment_fn(model: object) -> Callable[[str], str]:
    """Build a sentence-segmentation callable from a trained Morfessor model.

    The returned function splits each whitespace-delimited token into morphemes
    and rejoins them with spaces — exactly the transformation applied at train time.
    """

    def _segment(text: str) -> str:
        result: list[str] = []
        for word in text.split():
            try:
                morphemes, _ = model.viterbi_segment(word.lower())  # type: ignore[union-attr]
                result.append(" ".join(morphemes))
            except Exception:
                result.append(word)
        return " ".join(result)

    return _segment


def load_segment_fn(model_path: str) -> "Callable[[str], str] | None":
    """Load a persisted Morfessor model and return a segmentation callable.

    Returns None if the file is missing or morfessor is not installed.
    """
    if not os.path.exists(model_path):
        return None
    try:
        import morfessor  # PLC0415

        morph_model = morfessor.MorfessorIO().read_binary_file(model_path)
        logger.info("Morfessor model loaded from %s.", model_path)
        return make_segment_fn(morph_model)
    except Exception as e:
        logger.warning("Could not load Morfessor model from %s: %s", model_path, e)
        return None


def segment_sentences(
    sentences: list[str],
    segment_fn: Callable[[str], str],
) -> list[str]:
    """Apply segment_fn to each sentence in the list."""
    return [segment_fn(sent) for sent in sentences]
