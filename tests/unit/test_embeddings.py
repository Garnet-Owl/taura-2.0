"""Unit tests for cross-lingual word embeddings alignment and translation."""

import unittest
from unittest.mock import MagicMock

import numpy as np
from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.api.embeddings import (
    CrossLingualTranslator,
    compute_csls_penalty,
    extract_identical_string_dictionary,
    extract_parallel_proper_noun_anchors,
    get_sentence_embedding,
    iterative_procrustes,
    learn_alignment_matrix,
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

            mock_src_model.get_words.return_value = ["mubuyu"]
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


class TestIterativeProcrustes(unittest.TestCase):
    def test_iterative_procrustes_recovers_rotation(self):
        """Iterative Procrustes should converge to the known rotation matrix."""
        with given([]) as _:
            # A known 10-degree rotation in 2D
            theta = np.radians(10)
            c, s = np.cos(theta), np.sin(theta)
            R = np.array([[c, -s], [s, c]])
            np.random.seed(7)
            X = np.random.randn(2, 50)  # src embeddings (dim x N)
            Y = R @ X  # target embeddings under the known rotation

            # Start from the exact solution to ensure it remains stable
            # (Mutual nearest neighbors will perfectly pair X and Y)
            W_init = R.copy()

        with when("running iterative Procrustes refinement for 5 steps"):
            W_refined = iterative_procrustes(X, Y, W_init, n_iters=5, csls_k=2)

        with then("the refined matrix is orthogonal and close to R"):
            np.testing.assert_array_almost_equal(
                W_refined @ W_refined.T, np.eye(2), decimal=5
            )
            np.testing.assert_array_almost_equal(W_refined, R, decimal=4)

    def test_iterative_procrustes_returns_orthogonal_matrix(self):
        """Iterative Procrustes output must always be orthogonal regardless of data."""
        with given([]) as _:
            np.random.seed(21)
            X = np.random.randn(10, 100)
            Y = np.random.randn(10, 100)
            W_init = learn_alignment_matrix(X, Y)

        with when("running 3 refinement iterations on random data"):
            W_refined = iterative_procrustes(X, Y, W_init, n_iters=3, csls_k=2)

        with then("the result matrix is orthogonal"):
            product = W_refined @ W_refined.T
            np.testing.assert_array_almost_equal(product, np.eye(10), decimal=5)


class TestCrossLingualAlignmentPipeline(unittest.TestCase):
    def test_extract_identical_string_dictionary(self):
        """Should extract matching strings > 2 chars or digits."""
        with given([]) as _:
            src_words = ["hello", "world", "123", "a", "kenya", "mũndũ"]
            tgt_words = ["kenya", "earth", "123", "a", "hi"]

        with when("extracting identical strings"):
            seed = extract_identical_string_dictionary(src_words, tgt_words)

        with then("only valid overlapping strings are extracted"):
            assert_that(len(seed), is_(equal_to(2)))
            assert_that(seed, is_(equal_to(["123", "kenya"])))  # Sorted order

    def test_extract_parallel_proper_noun_anchors_finds_shared_names(self):
        """Should extract proper nouns appearing verbatim in both sides of a pair."""
        with given([]) as _:
            # 'Kenya' appears capitalised in English but as 'kenya' in Kikuyu
            en = ["Kenya is a beautiful country", "Peter went to Jerusalem"]
            ki = ["kenya ni iguru", "peter niakinya yerusalemu"]

        with when("extracting proper-noun anchors"):
            anchors = extract_parallel_proper_noun_anchors(en, ki)

        with then("shared names are extracted (case-normalised)"):
            assert_that("kenya" in anchors, is_(True))
            assert_that("peter" in anchors, is_(True))

    def test_extract_parallel_proper_noun_anchors_excludes_short_words(self):
        """Words shorter than min_len must not be included as anchors."""
        with given([]) as _:
            en = ["Go to Ki today"]
            ki = ["ki ni thii hari"]

        with when("extracting with default min_len=3"):
            anchors = extract_parallel_proper_noun_anchors(en, ki)

        with then("'Ki' (2 chars) is excluded"):
            assert_that("ki" in anchors, is_(False))

    def test_extract_parallel_proper_noun_anchors_ignores_non_shared_words(self):
        """Proper nouns that appear only on the English side must be excluded."""
        with given([]) as _:
            en = ["Abraham went to Egypt"]
            ki = ["niakinya atiriri"]  # Abraham / Egypt NOT present in Kikuyu

        with when("extracting anchors"):
            anchors = extract_parallel_proper_noun_anchors(en, ki)

        with then("no anchors are extracted since nothing matches"):
            assert_that(len(anchors), is_(equal_to(0)))

    def test_compute_csls_penalty_penalizes_hubs(self):
        """CSLS penalty should be higher for hub words that are close to many queries."""
        with given([]) as _:
            # Create 3 targets
            # T0 is a hub (close to everything)
            # T1, T2 are isolated
            targets = np.array([
                [1.0, 0.0],  # T0
                [0.0, 1.0],  # T1
                [-1.0, 0.0],  # T2
            ])
            # Create queries that are mostly clustered around T0
            queries = np.array([[0.9, 0.1], [0.8, 0.2], [1.0, -0.1]])

        with when("computing CSLS penalty for targets using queries as reference"):
            penalty = compute_csls_penalty(targets, queries, k=2)

        with then("the hub T0 has a much higher penalty than isolated targets"):
            assert_that(penalty[0] > penalty[1], is_(True))
            assert_that(penalty[0] > penalty[2], is_(True))

    def test_translator_applies_csls_to_mitigate_hubness(self):
        """Translator should use CSLS to reject a lexically overlapping hub in favor of a true semantic match."""
        with given([]) as _:
            mock_src_model = MagicMock()
            mock_tgt_model = MagicMock()
            mock_src_model.get_dimension.return_value = 2
            mock_tgt_model.get_dimension.return_value = 2
            W = np.eye(2)

            # Target vocab: "▁bod" (hub, vector [1,0]) and "deity" (true meaning, vector [0.8, 0.6])
            mock_tgt_model.get_words.return_value = ["▁bod", "deity"]

            def get_tgt_vector(word):
                if word == "▁bod":
                    return np.array([1.0, 0.0])
                if word == "deity":
                    return np.array([0.8, 0.6])
                return np.zeros(2)

            mock_tgt_model.get_word_vector.side_effect = get_tgt_vector

            # Source query: "ngai" (vector [0.9, 0.4])
            mock_src_model.get_words.return_value = ["ngai", "x1", "x2", "x3"]

            def get_src_vector(word):
                if word == "ngai":
                    return np.array([0.9, 0.4])
                # Provide some reference points that make "▁bod" a huge hub
                return np.array([1.0, 0.0])

            mock_src_model.get_word_vector.side_effect = get_src_vector

            translator = CrossLingualTranslator(
                src_model=mock_src_model,
                tgt_model=mock_tgt_model,
                projection_matrix=W,
                tgt_sentences=[],
                csls_k=2,
            )

        with when("translating with CSLS enabled"):
            translation = translator.translate_word_by_word("ngai")

        with then("it successfully completes without error"):
            assert_that(translation, is_(equal_to("deity")))
