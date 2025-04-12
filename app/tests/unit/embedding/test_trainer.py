import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from app.api.embedding.trainer import EmbeddingConfig, FastTextTrainer
from app.tests.givenpy import given, then, when


class TestFastTextTrainer(unittest.TestCase):
    """Test suite for the FastTextTrainer class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test models
        self.temp_dir = tempfile.TemporaryDirectory()
        self.model_dir = Path(self.temp_dir.name)

        # Sample training data
        self.english_data = [
            "hello world",
            "the quick brown fox jumps over the lazy dog",
            "machine learning is fun",
            "natural language processing helps computers understand human language",
        ]

        self.kikuyu_data = [
            "nĩ mwega",
            "ndũgĩka ũguo",
            "wĩkĩte atĩa",
            "mũrĩ agĩrĩire",
        ]

    def tearDown(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """
        Given a valid model directory
        When a FastTextTrainer is initialized
        Then the model directory should be created
        """
        with given():
            model_dir = self.model_dir / "test_init"

        with when("initializing a FastTextTrainer"):
            trainer = FastTextTrainer(model_dir)

        with then("the model directory should be created"):
            assert model_dir.exists()
            assert trainer.models == {}

    @mock.patch("fasttext.train_unsupervised")
    def test_train_model(self, mock_train):
        """
        Given a trainer and training data
        When train_model is called
        Then a FastText model should be trained and saved
        """
        # Mock FastText model
        mock_model = mock.MagicMock()
        mock_model.get_word_vector.return_value = np.zeros(300)
        mock_train.return_value = mock_model

        with given():
            trainer = FastTextTrainer(self.model_dir)
            config = EmbeddingConfig(dim=100, epoch=1)

        with when("training a model"):
            model = trainer.train_model(
                "english", self.english_data, config, save_model=True
            )

        with then("the model should be trained with correct parameters"):
            mock_train.assert_called_once()
            # Check training params
            call_kwargs = mock_train.call_args[1]
            assert call_kwargs["dim"] == 100
            assert call_kwargs["epoch"] == 1

            # Check that the model was saved
            assert "english" in trainer.models
            mock_model.save_model.assert_called_once()

    @mock.patch("fasttext.load_model")
    def test_load_model(self, mock_load):
        """
        Given a trainer with a saved model
        When load_model is called
        Then the model should be loaded from disk
        """
        # Mock FastText model
        mock_model = mock.MagicMock()
        mock_load.return_value = mock_model

        with given():
            trainer = FastTextTrainer(self.model_dir)

            # Create a dummy model file
            model_path = self.model_dir / "english.bin"
            model_path.touch()

        with when("loading a model"):
            model = trainer.load_model("english")

        with then("the model should be loaded from disk"):
            mock_load.assert_called_once_with(str(model_path))
            assert trainer.models["english"] == mock_model

    @mock.patch("fasttext.train_unsupervised")
    def test_get_word_vector(self, mock_train):
        """
        Given a trainer with a loaded model
        When get_word_vector is called
        Then the correct word vector should be returned
        """
        # Mock FastText model
        mock_model = mock.MagicMock()
        mock_model.get_word_vector.return_value = np.ones(300)
        mock_train.return_value = mock_model

        with given():
            trainer = FastTextTrainer(self.model_dir)
            trainer.train_model("english", self.english_data, save_model=False)

        with when("getting a word vector"):
            vector = trainer.get_word_vector("english", "hello")

        with then("the correct vector should be returned"):
            mock_model.get_word_vector.assert_called_once_with("hello")
            assert np.array_equal(vector, np.ones(300))

    @mock.patch("fasttext.train_unsupervised")
    def test_get_sentence_vector(self, mock_train):
        """
        Given a trainer with a loaded model
        When get_sentence_vector is called
        Then the correct sentence vector should be returned
        """
        # Mock FastText model
        mock_model = mock.MagicMock()
        mock_model.get_sentence_vector.return_value = np.ones(300)
        mock_train.return_value = mock_model

        with given():
            trainer = FastTextTrainer(self.model_dir)
            trainer.train_model("english", self.english_data, save_model=False)

        with when("getting a sentence vector"):
            vector = trainer.get_sentence_vector("english", "hello world")

        with then("the correct vector should be returned"):
            mock_model.get_sentence_vector.assert_called_once_with("hello world")
            assert np.array_equal(vector, np.ones(300))

    def test_preprocess_data(self):
        """
        Given a trainer and raw text data
        When preprocess_data is called
        Then the data should be properly formatted for FastText
        """
        with given():
            trainer = FastTextTrainer(self.model_dir)
            messy_data = [
                "  HELLO World  ",
                "",  # Empty string should be skipped
                "The quick\nbrown fox",
                "Multiple    spaces  here",
            ]
            output_path = self.model_dir / "test_output.txt"

        with when("preprocessing data"):
            result_path = trainer.preprocess_data(messy_data, output_path)

        with then("the data should be properly formatted"):
            assert result_path == output_path
            assert result_path.exists()

            # Check the content of the file
            with open(result_path, encoding="utf-8") as f:
                lines = f.readlines()
                assert len(lines) == 3  # Empty string should be skipped
                assert lines[0].strip() == "hello world"
                assert lines[1].strip() == "the quick brown fox"
                assert lines[2].strip() == "multiple spaces here"


if __name__ == "__main__":
    unittest.main()
