import logging
from pathlib import Path
from typing import Optional, Union, List

import fasttext
import numpy as np
from pydantic import BaseModel



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmbeddingConfig(BaseModel):
    """Configuration for FastText embedding models."""
    dim: int = 300
    min_count: int = 5
    epoch: int = 10
    learning_rate: float = 0.05
    word_ngrams: int = 2
    min_n: int = 3
    max_n: int = 6
    bucket: int = 2000000
    thread: int = 4
    loss: str = "ns"


class FastTextTrainer:
    """
    Trains, manages and provides access to FastText embedding models.
    """

    def __init__(self, model_directory: Union[str, Path]):
        self.model_directory = Path(model_directory)
        self.model_directory.mkdir(parents=True, exist_ok=True)
        self.models = {}

    @staticmethod
    def preprocess_data(data: List[str], output_path: Path) -> Path:
        with open(output_path, 'w', encoding='utf-8') as f:
            for sentence in data:
                clean_sentence = ' '.join(sentence.lower().split())
                if clean_sentence:
                    f.write(f"{clean_sentence}\n")

        logger.info(f"Preprocessed data saved to {output_path}")
        return output_path

    def train_model(
            self,
            language: str,
            train_data: List[str],
            config: Optional[EmbeddingConfig] = None,
            save_model: bool = True
    ) -> fasttext.FastText._FastText:

        if config is None:
            config = EmbeddingConfig()

        temp_file = self.model_directory / f"{language}_temp.txt"
        data_path = self.preprocess_data(train_data, temp_file)

        params = {
            'input': str(data_path),
            'dim': config.dim,
            'minCount': config.min_count,
            'epoch': config.epoch,
            'lr': config.learning_rate,
            'wordNgrams': config.word_ngrams,
            'minn': config.min_n,
            'maxn': config.max_n,
            'bucket': config.bucket,
            'thread': config.thread,
            'loss': config.loss
        }

        logger.info(f"Training FastText model for {language}")
        model = fasttext.train_unsupervised(**params)

        if save_model:
            model_path = self.model_directory / f"{language}.bin"
            model.save_model(str(model_path))
            logger.info(f"Model saved to {model_path}")

        self.models[language] = model

        data_path.unlink(missing_ok=True)

        return model

    def load_model(self, language: str) -> Optional[fasttext.FastText._FastText]:
        model_path = self.model_directory / f"{language}.bin"

        if language in self.models:
            return self.models[language]

        if model_path.exists():
            logger.info(f"Loading {language} model from {model_path}")
            model = fasttext.load_model(str(model_path))
            self.models[language] = model
            return model

        logger.warning(f"No model found for {language}")
        return None

    def get_word_vector(self, language: str, word: str) -> Optional[np.ndarray]:
        model = self.load_model(language)
        if model is None:
            return None

        return model.get_word_vector(word)

    def get_sentence_vector(self, language: str, sentence: str) -> Optional[np.ndarray]:
        model = self.load_model(language)
        if model is None:
            return None

        return model.get_sentence_vector(sentence)
