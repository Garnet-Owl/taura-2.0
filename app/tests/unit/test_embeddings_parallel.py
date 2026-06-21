import numpy as np
from hamcrest import assert_that, equal_to
from unittest.mock import patch, MagicMock

from app.api.embeddings import learn_alignment_matrix, iterative_procrustes, is_cuda_available
from app.tests.givenpy import given, when, then

def test_learn_alignment_matrix_accuracy() -> None:
    with given([]) as _:
        # Create an exact orthogonal transformation
        np.random.seed(42)
        X = np.random.randn(10, 100) # dim 10, N 100
        W_true, _ = np.linalg.qr(np.random.randn(10, 10))
        Y = W_true @ X
        
        with when("learning the alignment matrix"):
            W_learned = learn_alignment_matrix(X, Y)
            
        with then("the learned matrix should match the true orthogonal transformation"):
            error = np.linalg.norm(W_learned - W_true)
            assert_that(error < 1e-6, equal_to(True))

