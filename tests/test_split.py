"""Unit tests for dataset splitting."""

import unittest

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, is_

from app.api.split import split_by_hash, split_data


class TestSplit(unittest.TestCase):
    def test_split_data_correct_proportions(self):
        """Dataset should be split into train, val, and test according to ratios."""
        with given([]) as _:
            # 10 pairs of data
            data = [(f"kikuyu_{i}", f"english_{i}") for i in range(10)]
            train_ratio = 0.8
            val_ratio = 0.1
            test_ratio = 0.1

        with when("splitting the dataset"):
            train, val, test = split_data(
                data=data,
                train_ratio=train_ratio,
                val_ratio=val_ratio,
                test_ratio=test_ratio,
                seed=42,
            )

        with then("the lengths of splits match the ratios"):
            assert_that(len(train), is_(equal_to(8)))
            assert_that(len(val), is_(equal_to(1)))
            assert_that(len(test), is_(equal_to(1)))

    def test_split_data_invalid_ratios_raises_error(self):
        """ValueError should be raised if ratios do not sum to 1.0."""
        with given([]) as _:
            data = [("ki", "en")]
            train_ratio = 0.5
            val_ratio = 0.2
            test_ratio = 0.2

        with when("splitting with invalid ratios"):

            def action():
                split_data(data, train_ratio, val_ratio, test_ratio)

        with then("a ValueError is raised"):
            self.assertRaises(ValueError, action)

    def test_split_data_reproducible(self):
        """Splits should be identical when using the same seed."""
        with given([]) as _:
            data = [(f"kikuyu_{i}", f"english_{i}") for i in range(100)]
            seed = 42

        with when("splitting twice with the same seed"):
            train1, val1, test1 = split_data(data, 0.8, 0.1, 0.1, seed=seed)
            train2, val2, test2 = split_data(data, 0.8, 0.1, 0.1, seed=seed)

        with then("the splits are identical"):
            assert_that(train1, is_(equal_to(train2)))
            assert_that(val1, is_(equal_to(val2)))
            assert_that(test1, is_(equal_to(test2)))

    def test_split_by_hash_is_independent_of_other_items(self):
        """A pair's split depends only on the pair and the seed, not its neighbours."""
        with given([]) as _:
            small = [(f"kikuyu_{i}", f"english_{i}") for i in range(100)]
            large = list(reversed(small)) + [(f"extra_{i}", f"x_{i}") for i in range(100)]

        with when("splitting both datasets with the same seed"):
            small_splits = split_by_hash(small, 0.8, 0.1, 0.1, seed=42)
            large_splits = split_by_hash(large, 0.8, 0.1, 0.1, seed=42)

        with then("every original pair keeps its split"):
            for small_part, large_part in zip(small_splits, large_splits, strict=True):
                assert_that(set(small_part) <= set(large_part), is_(True))

    def test_split_by_hash_changes_with_seed(self):
        """A different seed gives a different assignment."""
        with given([]) as _:
            data = [(f"kikuyu_{i}", f"english_{i}") for i in range(200)]

        with when("splitting with two seeds"):
            _, val_a, _ = split_by_hash(data, 0.8, 0.1, 0.1, seed=42)
            _, val_b, _ = split_by_hash(data, 0.8, 0.1, 0.1, seed=7)

        with then("the validation sets differ"):
            assert_that(val_a == val_b, is_(False))
