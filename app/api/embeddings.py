"""Cross-lingual word embeddings alignment and translation logic."""

import io
import os
import sys
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Any

import fasttext
import numpy as np

from app.api.preprocessing import normalize_text, tokenize_text
from app.shared.logger import setup_logger

logger = setup_logger(__name__)

is_cuda_available = False
try:
    import torch
    if torch.cuda.is_available():
        is_cuda_available = True
except Exception:
    pass

# Global variables for worker processes
_worker_model = None

def _init_worker(model_path: str) -> None:
    global _worker_model
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    _worker_model = fasttext.load_model(model_path)
    sys.stdout = old_stdout

def _get_embedding_worker(sentence: str, dim: int) -> np.ndarray:
    return get_sentence_embedding(_worker_model, sentence, dim=dim)

def get_sentence_embeddings_parallel(model_path: str, sentences: list[str], dim: int = 100) -> np.ndarray:
    """Extracts sentence embeddings using all available CPU cores without hoarding memory."""
    cpu_count = max(1, multiprocessing.cpu_count())
    # Cap workers at 12 to prevent OOM with 32GB RAM (each fastText model is ~800MB)
    workers = min(cpu_count, 12) 
    
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(model_path,)) as executor:
        func = partial(_get_embedding_worker, dim=dim)
        results = list(executor.map(func, sentences, chunksize=1000))
        
    return np.array(results)


def get_sentence_embedding(model: Any, sentence: str, dim: int = 100) -> np.ndarray:
    """
    Computes the average word embedding for a given sentence.
    """
    normalized = normalize_text(sentence)
    tokens = [t for t in tokenize_text(normalized) if t]

    if not tokens:
        actual_dim = getattr(model, "get_dimension", lambda: dim)()
        return np.zeros(actual_dim, dtype=np.float32)

    embeddings = [model.get_word_vector(token) for token in tokens]
    return np.mean(embeddings, axis=0).astype(np.float32)  # type: ignore[no-any-return]


def learn_alignment_matrix(
    src_embeddings: np.ndarray, tgt_embeddings: np.ndarray
) -> np.ndarray:
    """
    Learns an orthogonal mapping matrix W that aligns the source embedding space
    to the target embedding space using parallel anchor representations.
    Solves the orthogonal Procrustes problem: W = U V^T where U S V^T = SVD(Y X^T).

    Args:
        src_embeddings: Source embeddings of shape (dim, N)
        tgt_embeddings: Target embeddings of shape (dim, N)

    Returns:
        W: Orthogonal projection matrix of shape (dim, dim)
    """
    if is_cuda_available:
        import torch
        try:
            device = torch.device("cuda")
            t_src = torch.tensor(src_embeddings, device=device)
            t_tgt = torch.tensor(tgt_embeddings, device=device)
            M = t_tgt @ t_src.T
            U, _, Vt = torch.linalg.svd(M)
            W = U @ Vt
            return W.cpu().numpy()
        except Exception as e:
            logger.warning("PyTorch failed during learn_alignment_matrix SVD: %s. Falling back to NumPy.", e)

    M = tgt_embeddings @ src_embeddings.T
    U, _, Vt = np.linalg.svd(M)
    W = U @ Vt
    return W  # type: ignore[no-any-return]


def iterative_procrustes(
    src_embeddings: np.ndarray,
    tgt_embeddings: np.ndarray,
    W_init: np.ndarray,
    n_iters: int = 5,
) -> np.ndarray:
    """
    Refines an initial orthogonal alignment matrix W using iterative Procrustes.

    Each iteration projects the source embeddings with the current W, then
    re-solves the orthogonal Procrustes problem against the target embeddings.
    Typically converges in 3–5 steps, measurably improving Top-1 retrieval.

    Args:
        src_embeddings: Source embeddings of shape (dim, N).
        tgt_embeddings: Target embeddings of shape (dim, N).
        W_init:         Initial orthogonal matrix of shape (dim, dim).
        n_iters:        Number of refinement iterations.

    Returns:
        W: Refined orthogonal projection matrix of shape (dim, dim).
    """
    if is_cuda_available:
        import torch
        try:
            device = torch.device("cuda")
            t_src = torch.tensor(src_embeddings, device=device)
            t_tgt = torch.tensor(tgt_embeddings, device=device)
            W = torch.tensor(W_init.copy(), device=device)
            for _ in range(n_iters):
                projected = W @ t_src
                M = t_tgt @ projected.T
                U, _, Vt = torch.linalg.svd(M)
                W = U @ Vt
            return W.cpu().numpy()
        except Exception as e:
            logger.warning("PyTorch failed during iterative_procrustes: %s. Falling back to NumPy.", e)

    W = W_init.copy()
    for _ in range(n_iters):
        projected = W @ src_embeddings
        M = tgt_embeddings @ projected.T
        U, _, Vt = np.linalg.svd(M)
        W = U @ Vt
    return W  # type: ignore[no-any-return]


class CrossLingualTranslator:
    """
    Bidirectional translator using cross-lingual word/sentence embeddings.
    """

    def __init__(
        self,
        src_model: Any,
        tgt_model: Any,
        projection_matrix: np.ndarray,
        tgt_sentences: list[str],
        precomputed_tgt_embeddings: np.ndarray | None = None,
    ) -> None:
        self.src_model = src_model
        self.tgt_model = tgt_model
        self.projection_matrix = projection_matrix
        self.tgt_sentences = tgt_sentences

        if precomputed_tgt_embeddings is not None:
            self.tgt_embeddings = precomputed_tgt_embeddings
        else:
            # Precompute target sentence embeddings
            tgt_embs = []
            for s in tgt_sentences:
                emb = get_sentence_embedding(tgt_model, s)
                tgt_embs.append(emb)
            self.tgt_embeddings = np.array(tgt_embs)

    def translate_sentence_retrieval(self, src_sentence: str) -> str:
        """
        Translates a source sentence by projecting its embedding to the target space
        and retrieving the target sentence with the highest cosine similarity.
        """
        if not self.tgt_sentences:
            return ""

        src_emb = get_sentence_embedding(self.src_model, src_sentence)
        projected = self.projection_matrix @ src_emb

        # Compute cosine similarities
        norm_projected = np.linalg.norm(projected)
        if norm_projected < 1e-8:
            return self.tgt_sentences[0]

        norms_tgt = np.linalg.norm(self.tgt_embeddings, axis=1)
        # Avoid division by zero for unaligned/empty target sentences
        norms_tgt[norms_tgt < 1e-8] = 1.0

        scores = np.dot(self.tgt_embeddings, projected) / (norms_tgt * norm_projected)
        best_idx = int(np.argmax(scores))
        return self.tgt_sentences[best_idx]

    def translate_word_by_word(self, src_sentence: str) -> str:
        """
        Translates a source sentence word-by-word by projecting each word's embedding
        and finding the nearest target vocabulary word.
        """
        from app.api.preprocessing import normalize_text, tokenize_text

        normalized = normalize_text(src_sentence)
        tokens = tokenize_text(normalized)
        tokens = [t for t in tokens if t]

        if not tokens:
            return ""

        # Get target vocabulary words and embeddings if not already cached
        if not hasattr(self, "tgt_vocab_words"):
            self.tgt_vocab_words = self.tgt_model.get_words()
            self.tgt_vocab_embeddings = np.array(
                [self.tgt_model.get_word_vector(w) for w in self.tgt_vocab_words]
            )
            self.tgt_vocab_norms = np.linalg.norm(self.tgt_vocab_embeddings, axis=1)
            self.tgt_vocab_norms[self.tgt_vocab_norms < 1e-8] = 1.0

        translated_words = []
        for token in tokens:
            v_src = self.src_model.get_word_vector(token)
            norm_v = np.linalg.norm(v_src)
            if norm_v < 1e-8:
                # If word is unknown/has zero vector, keep it as is
                translated_words.append(token)
                continue

            projected = self.projection_matrix @ v_src
            norm_proj = np.linalg.norm(projected)
            if norm_proj < 1e-8:
                translated_words.append(token)
                continue

            scores = np.dot(self.tgt_vocab_embeddings, projected) / (
                self.tgt_vocab_norms * norm_proj
            )
            best_idx = int(np.argmax(scores))
            translated_words.append(self.tgt_vocab_words[best_idx])

        return " ".join(translated_words)
