import re
import unicodedata
from typing import List, Dict, Set, Optional


class TextProcessor:
    """
    Processes text for FastText embedding models with language-specific handling.
    """

    def __init__(self, stopwords: Optional[Dict[str, Set[str]]] = None):
        self.stopwords = stopwords or {}

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text or not isinstance(text, str):
            return ""

        # Normalize Unicode characters
        text = unicodedata.normalize("NFKC", text)

        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def tokenize(self, text: str, language: str = "english") -> List[str]:
        text = self.normalize_text(text)

        # Simple whitespace tokenization as a baseline
        tokens = text.split()

        # Apply language-specific tokenization if needed
        if language == "kikuyu":
            # Kikuyu-specific tokenization can be added here
            # For now, using simple whitespace tokenization
            pass

        return tokens

    def remove_stopwords(self, tokens: List[str], language: str) -> List[str]:
        if language in self.stopwords:
            return [token for token in tokens if token not in self.stopwords[language]]

        return tokens

    def prepare_for_fasttext(self, texts: List[str], language: str,
                             remove_stopwords: bool = False) -> List[str]:
        processed_texts = []

        for text in texts:
            normalized = self.normalize_text(text)

            tokens = self.tokenize(normalized, language)

            if remove_stopwords:
                tokens = self.remove_stopwords(tokens, language)

            processed_text = " ".join(tokens)

            if processed_text:
                processed_texts.append(processed_text)

        return processed_texts
