import string
import re

def normalize_text(text: str) -> str:
    """
    Normalizes text by lowercasing, removing punctuation, and stripping extra spaces.
    """
    # Lowercase
    text = text.lower()
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_text(text: str) -> list[str]:
    """
    Tokenizes text by splitting on spaces.
    """
    if not text:
        return []
    return text.split(' ')
