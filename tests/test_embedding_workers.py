"""Unit tests for sizing the sentence-embedding worker pool."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.api.embeddings import max_embedding_workers

GB = 1024**3


class TestEmbeddingWorkers(unittest.TestCase):
    def test_workers_limited_by_memory(self):
        """Should cap workers so each 2.4 GB model copy fits in free memory."""
        with given([]) as _:
            model_bytes = int(2.4 * GB)

        with when("only 10 GB is free on a 4-core machine"):
            workers = max_embedding_workers(model_bytes, 10 * GB, cpu_count=4)

        with then("fewer workers than cores are used"):
            assert_that(workers, is_(equal_to(2)))

    def test_workers_limited_by_cpu_and_floor(self):
        """Should never exceed cores or 12, and always keep at least one."""
        with when("memory is plentiful"):
            many = max_embedding_workers(GB, 512 * GB, cpu_count=64)
            tight = max_embedding_workers(4 * GB, GB, cpu_count=8)

        with then("the cap is 12 and the floor is 1"):
            assert_that(many, is_(equal_to(12)))
            assert_that(tight, is_(equal_to(1)))
