import string
import re
import sentencepiece


def normalize_text(text: str) -> str:
    """
    Normalizes text by lowercasing, removing punctuation, and stripping extra spaces.
    """
    # Lowercase
    text = text.lower()
    # Remove punctuation
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_text(text: str) -> list[str]:
    """
    Tokenizes text by splitting on spaces.
    """
    if not text:
        return []
    return text.split(" ")


class SubwordTokenizer:
    """
    Subword tokenizer backed by a trained SentencePiece BPE model.

    Provides encode/decode over subword pieces so that morphologically rich
    Kikuyu words are handled gracefully at the vocabulary boundary.  Load once
    and reuse across the training and serving pipelines.
    """

    def __init__(self, model_path: str) -> None:
        self._sp = sentencepiece.SentencePieceProcessor()
        self._sp.load(model_path)

    def encode(self, text: str) -> list[str]:
        """Returns the list of subword pieces for *text*."""
        return self._sp.encode_as_pieces(text)  # type: ignore[no-any-return]

    def decode(self, pieces: list[str]) -> str:
        """Reconstructs a sentence from its subword *pieces*."""
        return self._sp.decode_pieces(pieces)  # type: ignore[no-any-return]
