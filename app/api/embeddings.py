"""Cross-lingual word embeddings alignment and translation logic."""

import io
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


def extract_identical_string_dictionary(
    src_words: list[str], tgt_words: list[str]
) -> list[str]:
    """Extracts words that exist exactly in both vocabularies to use as an initial seed dictionary."""
    src_set = set(src_words)
    tgt_set = set(tgt_words)
    common = src_set.intersection(tgt_set)
    # Keep words longer than 2 characters or pure digits
    seed = [w for w in common if len(w) > 2 or w.isdigit()]
    # Sort for determinism and cap at 5000 to avoid extreme memory usage in SVD
    return sorted(seed)[:5000]


def compute_csls_penalty(
    embs: np.ndarray, ref_embs: np.ndarray, k: int = 10
) -> np.ndarray:
    """Computes the mean cosine similarity of each embedding in `embs` to its `k` nearest neighbors in `ref_embs`."""
    if is_cuda_available:
        import torch

        try:
            device = torch.device("cuda")
            t_embs = torch.tensor(embs, device=device, dtype=torch.float32)
            t_ref = torch.tensor(ref_embs, device=device, dtype=torch.float32)
            t_embs = t_embs / t_embs.norm(dim=1, keepdim=True).clamp(min=1e-8)
            t_ref = t_ref / t_ref.norm(dim=1, keepdim=True).clamp(min=1e-8)

            sim = t_embs @ t_ref.T
            # topk is faster
            topk_sim, _ = torch.topk(sim, min(k, sim.shape[1]), dim=1)
            return topk_sim.mean(dim=1).cpu().numpy()
        except Exception as e:
            logger.warning("PyTorch CSLS failed: %s. Falling back to NumPy.", e)

    norm_embs = embs / np.maximum(np.linalg.norm(embs, axis=1, keepdims=True), 1e-8)
    norm_ref = ref_embs / np.maximum(
        np.linalg.norm(ref_embs, axis=1, keepdims=True), 1e-8
    )
    sim = norm_embs @ norm_ref.T
    sim.sort(axis=1)
    topk_sim = sim[:, -min(k, sim.shape[1]) :]
    return topk_sim.mean(axis=1)


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


def get_sentence_embeddings_parallel(
    model_path: str, sentences: list[str], dim: int = 100
) -> np.ndarray:
    """Extracts sentence embeddings using all available CPU cores without hoarding memory."""
    cpu_count = max(1, multiprocessing.cpu_count())
    # Cap workers at 12 to prevent OOM with 32GB RAM (each fastText model is ~800MB)
    workers = min(cpu_count, 12)

    with ProcessPoolExecutor(
        max_workers=workers, initializer=_init_worker, initargs=(model_path,)
    ) as executor:
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
            logger.warning(
                "PyTorch failed during learn_alignment_matrix SVD: %s. Falling back to NumPy.",
                e,
            )

    M = tgt_embeddings @ src_embeddings.T
    U, _, Vt = np.linalg.svd(M)
    W = U @ Vt
    return W  # type: ignore[no-any-return]


def iterative_procrustes(
    src_vocab_embs: np.ndarray,
    tgt_vocab_embs: np.ndarray,
    W_init: np.ndarray,
    n_iters: int = 5,
    csls_k: int = 10,
) -> np.ndarray:
    """
    Refines an initial orthogonal alignment matrix W using iterative Procrustes
    and Mutual Nearest Neighbors (MNN) with CSLS.

    Args:
        src_vocab_embs: Embeddings of top N source vocabulary words (dim, N_src).
        tgt_vocab_embs: Embeddings of top N target vocabulary words (dim, N_tgt).
        W_init:         Initial orthogonal matrix of shape (dim, dim).
        n_iters:        Number of refinement iterations.
        csls_k:         K neighbors for CSLS penalty.

    Returns:
        W: Refined orthogonal projection matrix of shape (dim, dim).
    """
    W = W_init.copy()

    for iteration in range(n_iters):
        # 1. Project source vocabulary
        projected_src = W @ src_vocab_embs  # (dim, N_src)

        # Normalize
        norm_src = projected_src.T / np.maximum(
            np.linalg.norm(projected_src.T, axis=1, keepdims=True), 1e-8
        )  # (N_src, dim)
        norm_tgt = tgt_vocab_embs.T / np.maximum(
            np.linalg.norm(tgt_vocab_embs.T, axis=1, keepdims=True), 1e-8
        )  # (N_tgt, dim)

        # 2. Compute CSLS similarities
        if is_cuda_available:
            import torch

            try:
                device = torch.device("cuda")
                t_src = torch.tensor(norm_src, device=device)
                t_tgt = torch.tensor(norm_tgt, device=device)
                sim = t_src @ t_tgt.T  # (N_src, N_tgt)

                # CSLS penalties
                r_T, _ = torch.topk(sim, min(csls_k, sim.shape[1]), dim=1)
                r_T = r_T.mean(dim=1, keepdim=True)  # (N_src, 1)

                r_S, _ = torch.topk(sim, min(csls_k, sim.shape[0]), dim=0)
                r_S = r_S.mean(dim=0, keepdim=True)  # (1, N_tgt)

                csls_sim = 2 * sim - r_T - r_S
                csls_sim = csls_sim.cpu().numpy()
            except Exception as e:
                logger.warning(
                    "PyTorch failed during iterative_procrustes CSLS: %s. Falling back to NumPy.",
                    e,
                )
                sim = norm_src @ norm_tgt.T
                sim_sorted_t = np.sort(sim, axis=1)[:, -csls_k:]
                r_T = sim_sorted_t.mean(axis=1, keepdims=True)
                sim_sorted_s = np.sort(sim, axis=0)[-csls_k:, :]
                r_S = sim_sorted_s.mean(axis=0, keepdims=True)
                csls_sim = 2 * sim - r_T - r_S
        else:
            sim = norm_src @ norm_tgt.T
            sim_sorted_t = np.sort(sim, axis=1)[:, -csls_k:]
            r_T = sim_sorted_t.mean(axis=1, keepdims=True)
            sim_sorted_s = np.sort(sim, axis=0)[-csls_k:, :]
            r_S = sim_sorted_s.mean(axis=0, keepdims=True)
            csls_sim = 2 * sim - r_T - r_S

        # 3. Find Mutual Nearest Neighbors (MNN)
        src_to_tgt = np.argmax(csls_sim, axis=1)
        tgt_to_src = np.argmax(csls_sim, axis=0)

        mutual_pairs = []
        for i in range(len(src_to_tgt)):
            j = src_to_tgt[i]
            if tgt_to_src[j] == i:
                mutual_pairs.append((i, j))

        if not mutual_pairs:
            logger.warning(
                "No mutual nearest neighbors found. Stopping iterative Procrustes."
            )
            break

        logger.info(
            f"Iterative Procrustes step {iteration + 1}: found {len(mutual_pairs)} mutual nearest neighbors."
        )

        src_indices = [p[0] for p in mutual_pairs]
        tgt_indices = [p[1] for p in mutual_pairs]

        X_new = src_vocab_embs[:, src_indices]
        Y_new = tgt_vocab_embs[:, tgt_indices]

        # 4. Re-learn W
        W = learn_alignment_matrix(X_new, Y_new)

    return W


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
        csls_k: int = 10,
    ) -> None:
        self.src_model = src_model
        self.tgt_model = tgt_model
        self.projection_matrix = projection_matrix
        self.tgt_sentences = tgt_sentences
        self.csls_k = csls_k

        if precomputed_tgt_embeddings is not None:
            self.tgt_embeddings = precomputed_tgt_embeddings
        else:
            # Precompute target sentence embeddings
            tgt_embs = []
            for s in tgt_sentences:
                emb = get_sentence_embedding(tgt_model, s)
                tgt_embs.append(emb)
            self.tgt_embeddings = np.array(tgt_embs)

        # Precompute target r_S penalty for sentence retrieval
        if len(self.tgt_embeddings) > 0:
            # We approximate source sentence space with target sentence space (intra-hubness)
            # which is an effective lightweight CSLS variant when source queries aren't known upfront.
            self.tgt_csls_penalty = compute_csls_penalty(
                self.tgt_embeddings, self.tgt_embeddings, k=self.csls_k
            )

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

        # Apply CSLS r_S penalty (we ignore r_T as it's constant for a single query)
        if hasattr(self, "tgt_csls_penalty"):
            scores = 2 * scores - self.tgt_csls_penalty

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

            # Precompute word-level r_S penalty using a sample of source vocabulary to represent the source space
            src_words = self.src_model.get_words()[:20000]
            src_vocab_embs = np.array(
                [self.src_model.get_word_vector(w) for w in src_words]
            )
            projected_src_vocab = src_vocab_embs @ self.projection_matrix.T
            self.tgt_word_csls_penalty = compute_csls_penalty(
                self.tgt_vocab_embeddings, projected_src_vocab, k=self.csls_k
            )

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

            # Apply CSLS penalty
            scores = 2 * scores - self.tgt_word_csls_penalty

            best_idx = int(np.argmax(scores))
            translated_words.append(self.tgt_vocab_words[best_idx])

        return " ".join(translated_words)
