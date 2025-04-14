import tempfile
import unittest
from pathlib import Path

import numpy as np

from app.api.embedding.utils import (
    cosine_similarity,
    create_vocabulary,
    euclidean_distance,
    find_nearest_neighbors,
    load_vectors_from_txt,
    save_vectors_to_txt,
)
from app.tests.givenpy import given, then, when


class TestEmbeddingUtils(unittest.TestCase):
    """Test suite for the embedding utilities."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        # Create sample vectors
        self.vector1 = np.array([1.0, 0.0, 0.0])
        self.vector2 = np.array([0.0, 1.0, 0.0])
        self.vector3 = np.array([1.0, 1.0, 0.0])  # Similar to both vector1 and vector2
        self.word_vectors = {
            "hello": np.array([1.0, 2.0, 3.0]),
            "world": np.array([2.0, 3.0, 4.0]),
            "test": np.array([0.5, 1.0, 1.5]),
            "example": np.array([1.5, 2.5, 3.5]),
        }

    def tearDown(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()

    def test_cosine_similarity(self):
        """
        Given two vectors
        When cosine_similarity is called
        Then the correct similarity score should be returned
        """
        with given():
            # Identical vectors should have similarity 1.0
            identical_vec = np.array([1.0, 2.0, 3.0])

            # Orthogonal vectors should have similarity 0.0
            orthogonal_vec1 = np.array([1.0, 0.0, 0.0])
            orthogonal_vec2 = np.array([0.0, 1.0, 0.0])

            # Similar vectors should have similarity between 0 and 1
            similar_vec1 = np.array([1.0, 1.0, 1.0])
            similar_vec2 = np.array([2.0, 2.0, 2.0])

            # Zero vector
            zero_vec = np.array([0.0, 0.0, 0.0])

        with when("calculating similarity between identical vectors"):
            identical_sim = cosine_similarity(identical_vec, identical_vec)

        with then("the similarity should be 1.0"):
            assert abs(identical_sim - 1.0) < 1e-10

        with when("calculating similarity between orthogonal vectors"):
            orthogonal_sim = cosine_similarity(orthogonal_vec1, orthogonal_vec2)

        with then("the similarity should be 0.0"):
            assert abs(orthogonal_sim) < 1e-10

        with when("calculating similarity between similar vectors"):
            similar_sim = cosine_similarity(similar_vec1, similar_vec2)

        with then("the similarity should be 1.0 (parallel vectors)"):
            assert abs(similar_sim - 1.0) < 1e-10

        with when("calculating similarity with zero vector"):
            zero_sim = cosine_similarity(identical_vec, zero_vec)

        with then("the similarity should be 0.0"):
            assert zero_sim == 0.0

    def test_euclidean_distance(self):
        """
        Given two vectors
        When euclidean_distance is called
        Then the correct distance should be returned
        """
        with given():
            # Identical vectors should have distance 0.0
            identical_vec = np.array([1.0, 2.0, 3.0])

            # Unit vectors with different directions
            unit_vec1 = np.array([1.0, 0.0, 0.0])
            unit_vec2 = np.array([0.0, 1.0, 0.0])

        with when("calculating distance between identical vectors"):
            identical_dist = euclidean_distance(identical_vec, identical_vec)

        with then("the distance should be 0.0"):
            assert identical_dist == 0.0

        with when("calculating distance between unit vectors"):
            unit_dist = euclidean_distance(unit_vec1, unit_vec2)

        with then("the distance should be sqrt(2)"):
            assert abs(unit_dist - np.sqrt(2)) < 1e-10

    def test_find_nearest_neighbors(self):
        """
        Given a query vector and a set of vectors
        When find_nearest_neighbors is called
        Then the correct neighbors should be returned
        """
        with given():
            query_vec = np.array([1.0, 2.0, 3.0])  # Same as "hello"

        with when("finding nearest neighbors using cosine similarity"):
            neighbors = find_nearest_neighbors(
                query_vec, self.word_vectors, n=2, metric="cosine"
            )

        with then("the correct neighbors should be returned"):
            assert len(neighbors) == 2
            # "hello" should be the closest, followed by either "world" or "example"
            assert neighbors[0][0] == "hello"
            assert neighbors[0][1] == 1.0  # Perfect match

        with when("finding nearest neighbors using euclidean distance"):
            neighbors = find_nearest_neighbors(
                query_vec, self.word_vectors, n=2, metric="euclidean"
            )

        with then("the correct neighbors should be returned"):
            assert len(neighbors) == 2
            # "hello" should be the closest, followed by others
            assert neighbors[0][0] == "hello"
            # Higher negative values indicate closer distance
            assert neighbors[0][1] == 0.0  # Perfect match, but negated

        with when("finding nearest neighbors with empty vectors"):
            empty_neighbors = find_nearest_neighbors(
                query_vec, {}, n=2, metric="cosine"
            )

        with then("an empty list should be returned"):
            assert empty_neighbors == []

    def test_create_vocabulary(self):
        """
        Given a list of tokenized sentences
        When create_vocabulary is called
        Then a vocabulary with correct frequencies should be returned
        """
        with given():
            sentences = [
                "the quick brown fox",
                "the fox jumps over the lazy dog",
                "quick quick brown brown",
                "the end",
            ]

        with when("creating vocabulary with min_count=1"):
            vocab = create_vocabulary(sentences, min_count=1)

        with then("all words should be included"):
            assert len(vocab) == 9
            assert vocab["the"] == 4
            assert vocab["quick"] == 3
            assert vocab["brown"] == 3
            assert vocab["fox"] == 2
            assert vocab["jumps"] == 1
            assert vocab["over"] == 1
            assert vocab["lazy"] == 1
            assert vocab["dog"] == 1
            assert vocab["end"] == 1

        with when("creating vocabulary with min_count=2"):
            vocab = create_vocabulary(sentences, min_count=2)

        with then("only words with frequency >= 2 should be included"):
            assert len(vocab) == 4
            assert "the" in vocab
            assert "quick" in vocab
            assert "brown" in vocab
            assert "fox" in vocab
            assert "jumps" not in vocab

    def test_save_and_load_vectors(self):
        """
        Given word vectors
        When save_vectors_to_txt and load_vectors_from_txt are called
        Then the vectors should be correctly saved and loaded
        """
        with given():
            output_path = self.test_dir / "test_vectors.txt"

        with when("saving and loading vectors with header"):
            save_vectors_to_txt(self.word_vectors, output_path, header=True)
            loaded_vectors = load_vectors_from_txt(output_path)

        with then("the loaded vectors should match the original vectors"):
            assert len(loaded_vectors) == len(self.word_vectors)
            for word, vector in self.word_vectors.items():
                assert word in loaded_vectors
                assert np.array_equal(loaded_vectors[word], vector)

        with when("saving and loading vectors without header"):
            no_header_path = self.test_dir / "test_vectors_no_header.txt"
            save_vectors_to_txt(self.word_vectors, no_header_path, header=False)
            loaded_no_header = load_vectors_from_txt(no_header_path)

        with then("the loaded vectors should match the original vectors"):
            assert len(loaded_no_header) == len(self.word_vectors)
            for word, vector in self.word_vectors.items():
                assert word in loaded_no_header
                assert np.array_equal(loaded_no_header[word], vector)


if __name__ == "__main__":
    unittest.main()
