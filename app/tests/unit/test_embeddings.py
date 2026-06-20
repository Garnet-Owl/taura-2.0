"""Unit tests for cross-lingual word embeddings alignment and translation."""

import unittest
from unittest.mock import MagicMock
import numpy as np

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.api.embeddings import (
    get_sentence_embedding,
    learn_alignment_matrix,
    CrossLingualTranslator,
)


class TestEmbeddings(unittest.TestCase):
    def test_get_sentence_embedding_averaging(self):
        """Sentence embedding should be the average of its word embeddings."""
        with given([]) as _:
            # Mock FastText model
            mock_model = MagicMock()

            # Words "hello" and "world" have specific vectors
            vector_hello = np.array([1.0, 2.0, 3.0], dtype=np.float32)
            vector_world = np.array([4.0, 5.0, 6.0], dtype=np.float32)

            def get_word_vector(word):
                if word == "hello":
                    return vector_hello
                elif word == "world":
                    return vector_world
                return np.zeros(3, dtype=np.float32)

            mock_model.get_word_vector.side_effect = get_word_vector
            sentence = "Hello, world!"  # Will normalize to "hello world"

        with when("computing the sentence embedding"):
            emb = get_sentence_embedding(mock_model, sentence)

        with then("the embedding is the average of word vectors"):
            expected_emb = (vector_hello + vector_world) / 2.0
            np.testing.assert_array_almost_equal(emb, expected_emb)

    def test_get_sentence_embedding_empty_returns_zeros(self):
        """An empty or unaligned sentence should return a zero vector."""
        with given([]) as _:
            mock_model = MagicMock()
            mock_model.get_dimension.return_return = 3
            mock_model.get_word_vector.return_value = np.zeros(3, dtype=np.float32)
            sentence = ""

        with when("computing embedding for an empty sentence"):
            emb = get_sentence_embedding(mock_model, sentence, dim=3)

        with then("the embedding is a zero vector"):
            np.testing.assert_array_equal(emb, np.zeros(3, dtype=np.float32))

    def test_learn_alignment_matrix_orthogonal_procrustes(self):
        """Alignment matrix should map source space to target space accurately."""
        with given([]) as _:
            # Create a known orthogonal rotation matrix R (90 degrees around Z axis)
            R = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])

            # Random source points
            np.random.seed(42)
            X = np.random.randn(3, 10)  # dim x num_points

            # Target points are rotated source points
            Y = R @ X

        with when("learning the alignment matrix"):
            W = learn_alignment_matrix(X, Y)

        with then("the learned matrix is close to the rotation matrix"):
            np.testing.assert_array_almost_equal(W, R, decimal=6)
            # Check orthogonality
            np.testing.assert_array_almost_equal(W.T @ W, np.eye(3), decimal=6)

    def test_translator_sentence_retrieval(self):
        """Translator should select the closest target sentence via retrieval."""
        with given([]) as _:
            # Mock source and target models
            mock_src_model = MagicMock()
            mock_tgt_model = MagicMock()

            # Dimension is 2
            mock_src_model.get_dimension.return_value = 2
            mock_tgt_model.get_dimension.return_value = 2

            # Identity projection matrix
            W = np.eye(2)

            # Candidates in target language
            tgt_sentences = ["apple", "banana"]

            # Mock word vectors
            # "apple" -> [1.0, 0.0], "banana" -> [0.0, 1.0]
            def get_tgt_vector(word):
                if word == "apple":
                    return np.array([1.0, 0.0])
                if word == "banana":
                    return np.array([0.0, 1.0])
                return np.zeros(2)

            mock_tgt_model.get_word_vector.side_effect = get_tgt_vector

            # Source query
            # "apple" in source language maps to [0.9, 0.1]
            def get_src_vector(word):
                if word == "mubuyu":
                    return np.array([0.9, 0.1])
                return np.zeros(2)

            mock_src_model.get_word_vector.side_effect = get_src_vector

            # Instantiate translator
            translator = CrossLingualTranslator(
                src_model=mock_src_model,
                tgt_model=mock_tgt_model,
                projection_matrix=W,
                tgt_sentences=tgt_sentences,
            )

        with when("translating the source sentence"):
            translation = translator.translate_sentence_retrieval("mubuyu")

        with then("the closest target sentence is retrieved"):
            assert_that(translation, is_(equal_to("apple")))

    def test_translator_word_by_word(self):
        """Translator should translate word-by-word by mapping vocab items."""
        with given([]) as _:
            mock_src_model = MagicMock()
            mock_tgt_model = MagicMock()

            mock_src_model.get_dimension.return_value = 2
            mock_tgt_model.get_dimension.return_value = 2

            W = np.eye(2)

            # Mock vocabulary
            mock_tgt_model.get_words.return_value = ["apple", "banana"]

            def get_tgt_vector(word):
                if word == "apple":
                    return np.array([1.0, 0.0])
                if word == "banana":
                    return np.array([0.0, 1.0])
                return np.zeros(2)

            mock_tgt_model.get_word_vector.side_effect = get_tgt_vector

            def get_src_vector(word):
                if word == "mubuyu":
                    return np.array([0.9, 0.1])
                return np.zeros(2)

            mock_src_model.get_word_vector.side_effect = get_src_vector

            translator = CrossLingualTranslator(
                src_model=mock_src_model,
                tgt_model=mock_tgt_model,
                projection_matrix=W,
                tgt_sentences=[],
            )

        with when("translating word-by-word"):
            translation = translator.translate_word_by_word("mubuyu")

        with then("each word is translated to its closest vocabulary target"):
            assert_that(translation, is_(equal_to("apple")))
