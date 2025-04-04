import logging
from pathlib import Path
from typing import Dict, List, Tuple, Union

import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


def cosine_similarity(first_vector: np.ndarray, second_vector: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        first_vector
        second_vector

    Returns:
        Cosine similarity (between -1 and 1)
    """
    norm1 = np.linalg.norm(first_vector)
    norm2 = np.linalg.norm(second_vector)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return np.dot(first_vector, second_vector) / (norm1 * norm2)


def euclidean_distance(first_vector: np.ndarray, second_vector: np.ndarray) -> float:

    return np.linalg.norm(first_vector - second_vector)


def find_nearest_neighbors(
        query_vector: np.ndarray,
        vectors: Dict[str, np.ndarray],
        n: int = 5,
        metric: str = "cosine"
) -> List[Tuple[str, float]]:
    """
    Find the nearest neighbors to a query vector.

    Args:
        query_vector: Vector to find neighbors for
        vectors: Dictionary mapping words to vectors
        n: Number of neighbors to return
        metric: Distance metric to use ('cosine' or 'euclidean')

    Returns:
        List of (word, similarity) tuples, sorted by similarity
    """
    if not vectors:
        return []

    # Calculate similarities
    similarities = []
    for word, vector in vectors.items():
        if metric == "cosine":
            # Higher is better for cosine similarity
            sim = cosine_similarity(query_vector, vector)
            similarities.append((word, sim))
        else:
            # Lower is better for euclidean distance
            dist = euclidean_distance(query_vector, vector)
            similarities.append((word, -dist))  # Negate for consistent sorting

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top n results
    return similarities[:n]


def create_vocabulary(sentences: List[str], min_count: int = 5) -> Dict[str, int]:
    """
    Create a vocabulary from a list of sentences with frequency counts.

    Args:
        sentences: List of tokenized sentences
        min_count: Minimum frequency to include in vocabulary

    Returns:
        Dictionary mapping words to their frequencies
    """
    word_counts = {}

    for sentence in sentences:
        for word in sentence.split():
            word_counts[word] = word_counts.get(word, 0) + 1

    # Filter by minimum count
    vocabulary = {word: count for word, count in word_counts.items()
                  if count >= min_count}

    return vocabulary


def save_vectors_to_txt(
        vectors: Dict[str, np.ndarray],
        output_path: Union[str, Path],
        header: bool = True
) -> None:
    """
    Save word vectors to a text file in word2vec format.

    Args:
        vectors: Dictionary mapping words to vectors
        output_path: Path to save vectors
        header: Whether to include a header line with dimensions
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        if header:
            vocab_size = len(vectors)
            vec_dim = next(iter(vectors.values())).shape[0] if vectors else 0
            f.write(f"{vocab_size} {vec_dim}\n")

        for word, vector in vectors.items():
            vector_str = ' '.join(map(str, vector))
            f.write(f"{word} {vector_str}\n")

    logger.info(f"Saved {len(vectors)} vectors to {output_path}")


def load_vectors_from_txt(input_path: Union[str, Path]) -> Dict[str, np.ndarray]:
    """
    Load word vectors from a text file in word2vec format.

    Args:
        input_path: Path to vector file

    Returns:
        Dictionary mapping words to vectors
    """
    vectors = {}

    with open(input_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip().split()

        # Check if first line is a header
        if len(first_line) == 2:
            # Skip header and continue
            pass
        else:
            # No header, process first line as a vector
            f.seek(0)

        for line in f:
            parts = line.strip().split()
            word = parts[0]
            vector = np.array([float(x) for x in parts[1:]])
            vectors[word] = vector

    logger.info(f"Loaded {len(vectors)} vectors from {input_path}")
    return vectors
