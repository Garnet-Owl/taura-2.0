"""High-level morphology service: trains, saves, and exposes a segment function.

The service layer owns the train-and-persist workflow so scripts and tests
can exercise the morphology feature without importing from scripts/.
"""

from typing import Callable

from app.morphology.core import (
    MORFESSOR_CORPUS_WEIGHT,
    make_segment_fn,
    save_morfessor,
    segment_sentences,
    train_morfessor,
)
from app.shared.logger import setup_logger

logger = setup_logger(__name__)


def build_and_save_segment_fn(
    sentences: list[str],
    save_path: str,
    corpusweight: float = MORFESSOR_CORPUS_WEIGHT,
) -> "Callable[[str], str] | None":
    """Train Morfessor on sentences, persist the model, return a segment callable.

    Returns None if morfessor is not installed — callers must handle this case
    by falling back to unprocessed text.
    """
    try:
        import morfessor as _  # noqa: F401 PLC0415
    except ImportError:
        logger.warning("morfessor not installed — skipping morphological segmentation.")
        return None

    model = train_morfessor(sentences, corpusweight=corpusweight)
    try:
        save_morfessor(model, save_path)
        logger.info("Morfessor model saved to %s", save_path)
    except Exception as e:
        logger.warning("Could not save Morfessor model: %s", e)

    return make_segment_fn(model)


def segment_corpus(
    sentences: list[str],
    save_path: str,
    corpusweight: float = MORFESSOR_CORPUS_WEIGHT,
) -> list[str]:
    """Train Morfessor on sentences, save the model, and return segmented sentences.

    Falls back to the original sentences if morfessor is unavailable.
    """
    fn = build_and_save_segment_fn(sentences, save_path, corpusweight=corpusweight)
    if fn is None:
        return sentences
    return segment_sentences(sentences, fn)
