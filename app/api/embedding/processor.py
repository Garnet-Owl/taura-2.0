import re
import unicodedata
from typing import List, Dict, Set, Optional


class TextProcessor:
    """
    Processes text for FastText embedding models with language-specific handling.
    """

    def __init__(self, stopwords: Optional[Dict[str, Set[str]]] = None):
        """
        Initialize the text processor.

        Args:
            stopwords: Dictionary mapping language codes to sets of stopwords
        """
        self.stopwords = stopwords or {}

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text by converting to lowercase, removing extra whitespace,
        and normalizing Unicode characters.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text
        """
        # Handle empty or non-string input
        if not text or not isinstance(text, str):
            return ""

        # Normalize Unicode characters
        text = unicodedata.normalize("NFKC", text)

        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def tokenize(self, text: str, language: str = "english") -> List[str]:
        """
        Tokenize text with language-specific handling.

        Args:
            text: Text to tokenize
            language: Language identifier

        Returns:
            List of tokens
        """
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
        """
        Remove stopwords from the list of tokens.

        Args:
            tokens: List of tokens
            language: Language identifier

        Returns:
            List of tokens with stopwords removed
        """
        if language in self.stopwords:
            return [token for token in tokens if token not in self.stopwords[language]]

        return tokens

    def prepare_for_fasttext(self, texts: List[str], language: str,
                             remove_stopwords: bool = False) -> List[str]:
        """
        Prepare a list of texts for FastText training.

        Args:
            texts: List of input texts
            language: Language identifier
            remove_stopwords: Whether to remove stopwords

        Returns:
            List of processed texts ready for FastText
        """
        processed_texts = []

        for text in texts:
            # Normalize text
            normalized = self.normalize_text(text)

            # Tokenize
            tokens = self.tokenize(normalized, language)

            # Remove stopwords if requested
            if remove_stopwords:
                tokens = self.remove_stopwords(tokens, language)

            # Join tokens back into a string
            processed_text = " ".join(tokens)

            # Add to results if not empty
            if processed_text:
                processed_texts.append(processed_text)

        return processed_texts
